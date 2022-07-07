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

        self.add_live_object_model_api(
            r'/live_app',
            lambda: application,
            'Application'
        )

        self.add_live_object_model_api(
            r'/live_app/view',
            lambda: application,
            'Application.View'
        )

        self.add_live_object_model_api(
            r'/live_set',
            lambda: self.song,
            'Song'
        )

        self.add_live_object_model_api(
            r'/live_set/view',
            lambda: self.song.view,
            'Song.View'
        )

        self.add_live_object_model_api(
            r'/live_set/tracks/(\d+)',
            lambda t: self.song.tracks[int(t)],
            'Track'
        )

        self.add_live_object_model_api(
            r'/live_set/tracks/(\d+)/view',
            lambda t: self.song.tracks[int(t)].view,
            'Track.View'
        )

        self.add_live_object_model_api(
            r'/live_set/tracks/(\d+)/clip_slots/(\d+)',
            lambda t, c: self.song.tracks[int(t)].clip_slots[int(c)],
            'ClipSlot'
        )

        self.add_live_object_model_api(
            r'/live_set/tracks/(\d+)/clip_slots/(\d+)/clip',
            lambda t, c: self.song.tracks[int(t)].clip_slots[int(c)].clip,
            'Clip'
        )

        self.add_live_object_model_api(
            r'/live_set/tracks/(\d+)/clip_slots/(\d+)/clip/view',
            lambda t, c: self.song.tracks[int(t)].clip_slots[int(c)].clip.view,
            'Clip.View'
        )

        self.add_live_object_model_api(
            r'/live_set/tracks/(\d+)/arrangement_clips/(\d+)',
            lambda t, c: self.song.tracks[int(t)].arrangement_clips[int(c)],
            'Clip'
        )

        self.add_live_object_model_api(
            r'/live_set/tracks/(\d+)/arrangement_clips/(\d+)/view',
            lambda t, c: self.song.tracks[int(t)].arrangement_clips[int(c)].view,
            'Clip.View'
        )

        self.add_live_object_model_api(
            r'/live_set/groove_pool',
            lambda: self.song.groove_pool,
            'GroovePool'
        )

        self.add_live_object_model_api(
            r'/live_set/groove_pool/grooves/(\d+)',
            lambda g: self.song.groove_pool.grooves[int(g)],
            'Groove'
        )

        self.add_live_object_model_api(
            r'/live_set/tracks/(\d+)/clip_slots/(\d+)/clip/groove',
            lambda t, c: self.song.tracks[int(t)].clip_slots[int(c)].clip.groove,
            'Groove'
        )

        self.add_live_object_model_api(
            r'/live_set/tracks/(\d+)/devices/(\d+)',
            lambda t, d: self.song.tracks[int(t)].devices[int(d)],
            'Device'
        )

        self.add_live_object_model_api(
            r'/live_set/tracks/(\d+)/devices/(\d+)/chains/(\d+)/devices/(\d+)',
            lambda t, d, l, k: self.song.tracks[int(t)].devices[int(d)].chains[int(l)].devices[int(k)],
            'Device'
        )

        self.add_live_object_model_api(
            r'/live_set/tracks/(\d+)/devices/(\d+)/return_chains/(\d+)/devices/(\d+)',
            lambda t, d, l, k: self.song.tracks[int(t)].devices[int(d)].return_chains[int(l)].devices[int(k)],
            'Device'
        )

        self.add_live_object_model_api(
            r'/live_set/tracks/(\d+)/devices/(\d+)/view',
            lambda t, d: self.song.tracks[int(t)].devices[int(d)].view,
            'Device.View'
        )

        self.add_live_object_model_api(
            r'/live_set/tracks/(\d+)/devices/(\d+)/chains/(\d+)/devices/(\d+)/view',
            lambda t, d, l, k: self.song.tracks[int(t)].devices[int(d)].chains[int(l)].devices[int(k)].view,
            'Device.View'
        )

        self.add_live_object_model_api(
            r'/live_set/tracks/(\d+)/devices/(\d+)/return_chains/(\d+)/devices/(\d+)/view',
            lambda t, d, l, k: self.song.tracks[int(t)].devices[int(d)].return_chains[int(l)].devices[int(k)].view,
            'Device.View'
        )

        self.add_live_object_model_api(
            r'/live_set/tracks/(\d+)/devices/(\d+)/parameters/(\d+)',
            lambda t, d, l: self.song.tracks[int(t)].devices[int(d)].parameters[int(l)],
            'DeviceParameter'
        )

        # TODO: how to expose RackDevice, since it is a specialization of Device without canonical path?

        self.add_live_object_model_api(
            r'/live_set/tracks/(\d+)/devices/(\d+)/drum_pads/(\d+)',
            lambda t, d, l: self.song.tracks[int(t)].devices[int(d)].drum_pads[int(l)],
            'DrumPad'
        )

        self.add_live_object_model_api(
            r'/live_set/tracks/(\d+)/devices/(\d+)/chains/(\d+)',
            lambda t, d, l: self.song.tracks[int(t)].devices[int(d)].chains[int(l)],
            'Chain'
        )

        self.add_live_object_model_api(
            r'/live_set/tracks/(\d+)/devices/(\d+)/return_chains/(\d+)',
            lambda t, d, l: self.song.tracks[int(t)].devices[int(d)].return_chains[int(l)],
            'Chain'
        )

        self.add_live_object_model_api(
            r'/live_set/tracks/(\d+)/devices/(\d+)/chains/(\d+)/devices/(\d+)/chains/(\d+)',
            lambda t, d, l, d1, l1: self.song.tracks[int(t)].devices[int(d)].chains[int(l)].devices[int(d1)].chains[int(l1)],
            'Chain'
        )

        self.add_live_object_model_api(
            r'/live_set/tracks/(\d+)/devices/(\d+)/return_chains/(\d+)/devices/(\d+)/chains/(\d+)',
            lambda t, d, l, d1, l1: self.song.tracks[int(t)].devices[int(d)].return_chains[int(l)].devices[int(d1)].chains[int(l1)],
            'Chain'
        )

        # TODO: how to expose DrumChain, since it is a specialization of Chain without canonical path?

        self.add_live_object_model_api(
            r'/live_set/tracks/(\d+)/devices/(\d+)/chains/(\d+)/mixer_device',
            lambda t, d, c: self.song.tracks[int(t)].devices[int(d)].chains[int(c)].mixer_device,
            'ChainMixerDevice'
        )

        self.add_live_object_model_api(
            r'/live_set/tracks/(\d+)/devices/(\d+)/return_chains/(\d+)/mixer_device',
            lambda t, d, c: self.song.tracks[int(t)].devices[int(d)].return_chains[int(c)].mixer_device,
            'ChainMixerDevice'
        )

        # TODO: how to expose SimplerDevice, SimplerDevice.View?

        self.add_live_object_model_api(
            r'/live_set/tracks/(\d+)/devices/(\d+)/sample',
            lambda t, d: self.song.tracks[int(t)].devices[int(d)].sample,
            'Sample'
        )

        # TODO: how to expose WavetableDevice, CompressorDevice, PluginDevice, MaxDevice, Eq8Device,
        #       HybridReverbDevice, SpectralResonatorDevice?

        self.add_live_object_model_api(
            r'/live_set/tracks/(\d+)/mixer_device',
            lambda t: self.song.tracks[int(t)].mixer_device,
            'MixerDevice'
        )

        # TODO: how to expose DeviceIO?

        self.add_live_object_model_api(
            r'/live_set/scenes/(\d+)',
            lambda s: self.song.scenes[int(s)],
            'Scene'
        )

        self.add_live_object_model_api(
            r'/live_set/cue_points/(\d+)',
            lambda c: self.song.cue_points[int(c)],
            'CuePoint'
        )

        #self.add_live_object_model_api(
        #    r'/control_surfaces/(\d+)',
        #    lambda c: self.???[int(c)],
        #    'ControlSurface'
        #)

        # additional custom addresses:

        def get_version(addr_args, params) -> Tuple:
            application = Live.Application.get_application()
            return application.get_major_version(), application.get_minor_version()
        self.osc_server.add_handler('/live_app/get_version', get_version)


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