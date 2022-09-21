from ableton.v2.control_surface import ControlSurface

from . import abletonosc

import importlib
import traceback
import logging
import sys
import os

from typing import Tuple

logger = logging.getLogger("abletonosc")

if sys.platform == "darwin":
    # On macOS, put logs in /tmp
    tmp_dir = "/tmp"
else:
    # On Windows, put logs in c:\temp
    tmp_dir = r"c:\temp"

log_path = os.path.join(tmp_dir, "abletonosc.log")
file_handler = logging.FileHandler(log_path)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('(%(asctime)s) [%(levelname)s] %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

class Manager(ControlSurface):
    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance)
        self.handler = None
        self.show_message("AbletonOSC: Listening for OSC on port %d" % abletonosc.OSC_LISTEN_PORT)

        self.osc_server = abletonosc.OSCServer()
        self.schedule_message(0, self.tick)

        self.init_api()

    def init_api(self):
        def test_callback(addr_args, params):
            self.show_message("Received OSC OK")
            self.osc_server.send("/test", ("ok",))
        def reload_callback(addr_args, params):
            self.reload_imports()
        def pyeval_callback(addr_args, params) -> Tuple:
            flags, code = params
            logger.info(f'pyeval: {code}')
            try:
                ret = [True, eval(code)]
            except Exception as e:
                ret = [False, str(e)]
            if not isinstance(ret[1], (int, float, bool, str)):
                ret[1] = str(ret[1])
            self.osc_server.send('/pyeval', ret)

        self.osc_server.add_handler("/test", test_callback)
        self.osc_server.add_handler("/reload", reload_callback)
        self.osc_server.add_handler("/pyeval", pyeval_callback)

        with self.component_guard():
            self.handler = abletonosc.AbletonOSCHandler(self)

    def clear_api(self):
        self.osc_server.clear_handlers()
        self.handler.clear_api()

    def tick(self):
        """
        Called once per 100ms "tick".
        Live's embedded Python implementation does not appear to support threading,
        and beachballs when a thread is started. Instead, this approach allows long-running
        processes such as the OSC server to perform operations.
        """
        logger.debug("Tick...")
        self.osc_server.process()
        self.schedule_message(1, self.tick)

    def reload_imports(self):
        try:
            importlib.reload(abletonosc.handler)
            importlib.reload(abletonosc.osc_server)
            importlib.reload(abletonosc.constants)
            importlib.reload(abletonosc)
        except Exception as e:
            exc = traceback.format_exc()
            logging.warning(exc)

        if self.handler:
            self.clear_api()
            self.init_api()
        logger.info("Reloaded code")

    def disconnect(self):
        self.show_message("Disconnecting...")
        logger.info("Disconneting...")
        self.osc_server.shutdown()
        super().disconnect()
