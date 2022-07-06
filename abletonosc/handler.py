from ableton.v2.control_surface.component import Component
from typing import Optional, Tuple, Any
import json
import logging
from .osc_server import OSCServer

import Live


class AbletonOSCHandler(Component):
    def __init__(self, manager):
        super().__init__()

        self.logger = logging.getLogger("abletonosc")
        self.manager = manager
        self.osc_server: OSCServer = self.manager.osc_server
        self.init_api()
        self.listener_functions = {}

    def init_api(self):
        application = Live.Application.get_application()

        self.add_live_object_model_api('/live_app', lambda: application, 'Application')

        self.add_live_object_model_api('/live_app/view', lambda: application, 'Application.View')

        def get_version(addr_args, params) -> Tuple:
            application = Live.Application.get_application()
            return application.get_major_version(), application.get_minor_version()
        self.osc_server.add_handler('/live_app/get_version', get_version)

        self.add_live_object_model_api('/live_set', lambda: self.song, 'Song')

        self.add_live_object_model_api('/live_set/view', lambda: self.song.view, 'Song.View')

        self.add_live_object_model_api(
            r'/live_set/tracks/(\d+)',
            lambda t: self.song.tracks[int(t)],
            'Track'
        )

        self.add_live_object_model_api(
            r'/live_set/tracks/0/view',
            lambda t: self.song.tracks[int(t)].view,
            'Track.View'
        )

        self.add_live_object_model_api(
            r'/live_set/tracks/(\d+)/clip_slots/(\d+)',
            lambda t, c: self.song.tracks[int(t)].clip_slots[int(c)],
            'ClipSlot'
        )

        self.add_live_object_model_api('/live_set/groove_pool', lambda: self.song.groove_pool, 'GroovePool')


    def clear_api(self):
        pass

    def add_live_object_model_api(self, osc_prefix, get_obj_func, class_name):
        self.logger.info('Adding LOM api for class %s at address %s' % (class_name, osc_prefix))
        if not hasattr(self, 'lom_data'):
            with open(__file__.replace('/abletonosc/handler.py', '/lom.json'), 'r') as f:
                setattr(self, 'lom_data', json.load(f))
        lom_def = getattr(self, 'lom_data', {}).get(class_name)
        if lom_def:
            # if addr contains a re pattern, the handler will be called with the result of
            # match.groups() as the first argument
            def make_handler(target_method, field_name, ret=False):
                def f(addr_params, params):
                    obj = get_obj_func(*addr_params)
                    r = target_method(obj, field_name, params)
                    if r or ret:
                        return r
                return f

            for fname in lom_def['functions']:
                addr = '%s/%s/call' % (osc_prefix, fname)
                self.osc_server.add_handler(addr, make_handler(self._call_method, fname, True))
            for pname, prop in lom_def['properties'].items():
                access = set(prop['access'].split(', '))
                addr = '%s/%s' % (osc_prefix, pname)
                if 'get' in access:
                    self.osc_server.add_handler(addr + '/get', make_handler(self._get, pname, True))
                if 'set' in access:
                    self.osc_server.add_handler(addr + '/set', make_handler(self._set, pname))
                if 'observe' in access:
                    self.osc_server.add_handler(addr + '/start_listen', make_handler(self._start_listen, pname))
                    self.osc_server.add_handler(addr + '/stop_listen', make_handler(self._stop_listen, pname))

    def _call_method(self, target, method, params: Optional[Tuple[Any]] = ()):
        self.logger.info("Calling method: %s (params %s)" % (method, str(params)))
        return getattr(target, method)(*params),

    def _set(self, target, prop, params: Tuple[Any]) -> None:
        self.logger.info("Setting property: %s (new value %s)" % (prop, params[0]))
        setattr(target, prop, params[0])
        return None,

    def _get(self, target, prop, params: Optional[Tuple[Any]] = ()) -> Tuple[Any]:
        self.logger.info("Getting property: %s" % prop)
        return getattr(target, prop),

    def _start_listen(self, target, prop, params: Optional[Tuple[Any]] = ()) -> None:
        def property_changed_callback():
            value = getattr(target, prop)
            self.logger.info("Property %s changed: %s" % (prop, value))
            # TODO
            osc_address = "/live/set/get/%s" % prop
            self.osc_server.send(osc_address, (value,))

        add_listener_function_name = "add_%s_listener" % prop
        add_listener_function = getattr(target, add_listener_function_name)
        add_listener_function(property_changed_callback)
        self.listener_functions[prop] = property_changed_callback

    def _stop_listen(self, target, prop, params: Optional[Tuple[Any]] = ()) -> None:
        if prop in self.listener_functions:
            listener_function = self.listener_functions[prop]
            remove_listener_function_name = "remove_%s_listener" % prop
            remove_listener_function = getattr(target, remove_listener_function_name)
            remove_listener_function(listener_function)
            del self.listener_functions[prop]
        else:
            self.logger.warning("No listener function found for property: %s" % prop)