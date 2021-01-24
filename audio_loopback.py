"""@package Simple audio controller class for capturing computer audio. Depends on https://vb-audio.com/Cable/
"""
import pyaudio
import numpy as np

p = pyaudio.PyAudio()

class AudioController:
    """
    """
    def __init__(self, aud_format=pyaudio.paInt16, channels=2, rate=48000, device_name="CABLE Output"):

        self.FORMAT = aud_format
        self.CHANNELS = channels
        self.RATE = rate
        self.CHUNK = 1024
        self.device_name = device_name
        self.stream = p.open(format=self.FORMAT, channels=self.CHANNELS,
            rate=self.RATE, input=True, input_device_index=self.getCableDevice(),
            frames_per_buffer=self.CHUNK)
        self.last = []

    def __del__(self):
        self.stream.stop_stream()
        self.stream.close()
        p.terminate()

    def dfft_reduce(dfft):
        simplified = []
        sumt = 0
        for j in range(25):
            for k in range(20):
                sumt+=dfft[25*j+k]
            simplified.append(sumt)
            sumt=0
        return simplified

    def getCableDevice(self):
        info = p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        for i in range(0, numdevices):
                if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                    print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))

        for i in range(p.get_device_count()):
            if(p.get_device_info_by_index(i)["name"].startswith(self.device_name)):
                return p.get_device_info_by_index(i)["index"]

    def readOnce(self):
        # Open the connection and start streaming the data
        self.stream.start_stream()
        # Loop so program doesn't end while the stream callback's
        # itself for new data
        in_data = self.stream.read(self.CHUNK)

        audio_data = np.fromstring(in_data, np.int16)
        # Fast Fourier Transform, 10*log10(abs) is to scale it to dB
        # and make sure it's not imaginary
        try:
            dfft = 10.*np.log10(abs(np.fft.rfft(audio_data)))
        except:
            return last
        self.last = AudioController.dfft_reduce(dfft)
        return self.last








