# AbletonOSC: Control Ableton Live 11+ with OSC

AbletonOSC is a MIDI remote script that provides an Open Sound Control (OSC) interface to control [Ableton Live 11+](https://www.ableton.com/en/live/). Building on ideas from the older [LiveOSC](https://github.com/hanshuebner/LiveOSC) scripts, its aim is to expose the entire [Live Object Model](https://docs.cycling74.com/max8/vignettes/live_object_model) API, providing comprehensive control over Live's control interfaces using the same naming structure and object hierarchy as LOM.

# Installation

To install the script:

 - Clone this repo, or download/unzip and rename AbletonOSC-master to AbletonOSC
 - Move the AbletonOSC folder to the MIDI Remote Scripts folder inside the Ableton application: `/Applications/Ableton Live*.app/Contents/App-Resources/MIDI Remote Scripts`
 - Restart Live
 - In `Preferences > MIDI`, add the new AbletonOSC Control Surface that should appear. Live should display a message saying "AbletonOSC: Listening for OSC on port 11000"
 - On macOS, an activity log will be created at `/tmp/abletonosc.log` 

# Usage

AbletonOSC listens for OSC messages on port **11000**, and sends replies on port **11001**. 

## Application API

AbletonOSC exposes the [Live Object Model](https://docs.cycling74.com/max8/vignettes/live_object_model). Simply replace
spaces with slashes to translate a *canonical path* to an OSC address. For instance, the canonical path of `ClipSlot`
is `live_set tracks N clip_slots M`, therefore its OSC address will be `/live_set/tracks/N/clip_slots`.

Properties have additional sub-addresses:

- `<property-address>/get` if the access is "get"; sending a message to this address causes the property value to be written to the reply socket at same address;
- `<property-address>/set` if the access is "set"; send a message with one argument to change the property value;
- `<property-address>/start_listen` and `<property-address>/stop_listen` if the access is "observe", which respectively start and stop the automatic sending of property message; property value will be written to the reply socket as soon as it changes when the listener is running;

For instance, to get song's tempo send `/live_set/song/tempo/get` and to change tempo send `/live_set/song/tempo/set 125.0`.
 
Functions can be called by appending `/call`, for instance: `/live_app/get_version_major/call`; the result of the function call will be sent to the reply socket.

 ---
 
# Acknowledgements

- [Stu Fisher](https://github.com/stufisher/) (and other authors) for LiveOSC, the spiritual predecessor to this library.
- [Julien Bayle](https://structure-void.com/ableton-live-midi-remote-scripts/#liveAPI) and [NSUSpray](https://nsuspray.github.io/Live_API_Doc/) for providing XML API docs, based on original work by [Hans Petrov](http://remotescripts.blogspot.com/p/support-files.html).
- [Daniel Jones](https://github.com/ideoforms) for the original AbletonOSC.
- [Federico Ferri](https://github.com/fferri) for rewriting the OSC protocol to follow Live Object Model.
