# Audio Speaker FFT

Documentation: http://ignis.wtf/audio_loopback/

## Dependecies
Along with pyaudio, this project is supposed to work together with [VB-Audio's Cable](https://vb-audio.com/Cable/) on Windows.
Supports Linux with pulse too.

## Usage

This is meant to be integrated to other software, but you can run the module directly.
```
usage: audio_loopback.py [-h] [-v] [-c COUNT] [-r REDUCTION] [-k CONSTANT]

Audio loopback capture, FFT

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Set verbosity level
  -c COUNT, --count COUNT
                        Count to reduce the array size to
  -r REDUCTION, --reduction REDUCTION
                        Reduction coefficient
  -k CONSTANT, --constant CONSTANT
                        Constant to multiply output with
```

## How to set up on windows

- Install VB-Audio Cable
- Go to Windows Sound Settings, Playback Devices.
- Make sure CABLE Input is not your default playback device.
- Go to Windows Sound Settings, Recording Devices.
- Go to CABLE Output's properties.
- Under "Listen" tab, check "Listen to this device"
- Set "Playback through this device" to "Default Playback Device"
- Under "Levels" tab, set both "CABLE Output" and "Wave In Volume" to 100%.
- Save settings and close.

## How to set up on Linux
- Install imports with pip.
- Install pavucontrol.
- Change the device being recorded to "Monitor of *your_output_device*"

## How to set up an application for loopback (Windows)

Follow [this guide](https://www.howtogeek.com/352787/how-to-set-per-app-sound-outputs-in-windows-10/) to change the sound device your application is feeding output to. If you are not hearing output from the application after this, make sure you read `How to set up` part, and set the "listen" settings properly.


## How to set up an everything for loopback  (Windows)
- Go to Windows Sound Settings, Playback Devices.
- Set CABLE Input as your default playback device.
- Go to Windows Sound Settings, Recording Devices.
- Go to CABLE Output's properties.
- Under "Listen" tab, check "Listen to this device"
- Set "Playback through this device" to your speakers/headphone.
- Under "Levels" tab, set both "CABLE Output" and "Wave In Volume" to 100%.
- Save settings and close.



