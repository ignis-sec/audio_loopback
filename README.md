# Audio Speaker FFT


## Dependecies
Along wiht pyaudio, this project is supposed to work together with [VB-Audio's Cable](https://vb-audio.com/Cable/)


## How to set up

- Install VB-Audio Cable
- Go to Windows Sound Settings, Playback Devices.
- Make sure CABLE Input is not your default playback device.
- Go to Windows Sound Settings, Recording Devices.
- Go to CABLE Output's properties.
- Under "Listen" tab, check "Listen to this device"
- Set "Playback through this device" to "Default Playback Device"
- Under "Levels" tab, set both "CABLE Output" and "Wave In Volume" to 100%.
- Save settings and close.

## How to set up an application for loopback

Follow [this guide](https://www.howtogeek.com/352787/how-to-set-per-app-sound-outputs-in-windows-10/) to change the sound device your application is feeding output to. If you are not hearing output from the application after this, make sure you read `How to set up` part, and set the "listen" settings properly.


## How to set up an everything for loopback
- Go to Windows Sound Settings, Playback Devices.
- Set CABLE Input as your default playback device.
- Go to Windows Sound Settings, Recording Devices.
- Go to CABLE Output's properties.
- Under "Listen" tab, check "Listen to this device"
- Set "Playback through this device" to your speakers/headphone.
- Under "Levels" tab, set both "CABLE Output" and "Wave In Volume" to 100%.
- Save settings and close.



## Testing