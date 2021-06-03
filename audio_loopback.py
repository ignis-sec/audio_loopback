## @package audio_loopback
# Simple audio controller class for capturing computer audio. Depends on https://vb-audio.com/Cable/ for windows.
# For linux, use pulse "Monitor"s
#


import pyaudio
import numpy as np
import allogate as logging


class AudioController:
    """ Simple class to capture fft data from audio stream

     :param aud_format: Audio output format for PyAudio. Default is pyaudio.paInt16
     :param channels: The desired number of input channels for PyAudio. Default is 1
     :param rate: Sampling Rate. 48000 by default. Lower sampling rates will take longer to collect.
     :param device_name: Name of the audio device to attach to.
     :param dampen: Level of audio dampening to apply. Ideally, silence should yield [0,0,0,0...] and the slightest noise should yield non-zero.
    """

    def __init__(self, aud_format: int = pyaudio.paInt16, channels: int = 1, rate: int = 48000,
                 device_name: str = "pulse", dampen: float = -25) -> object:

        # Pyaudio parameters
        self.FORMAT = aud_format
        self.CHANNELS = channels
        self.RATE = rate
        self.CHUNK = 1024
        self.device_name = device_name
        self.p = pyaudio.PyAudio()

        self.last = []
        self.dampen_coef = dampen

        logging.pprint("Starting audio stream", 4)
        self.stream = self.p.open(format=self.FORMAT, channels=self.CHANNELS,
                                  rate=self.RATE, input=True, input_device_index=self.find_device(device_name),
                                  frames_per_buffer=self.CHUNK)

        self.stream.start_stream()

    def __del__(self):
        """ Stop stream and close. Terminate pyaudio.
        """
        logging.pprint("Stopping audio stream", 2)
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

    @staticmethod
    def dfft_reduce(dfft: list, count: int = 25, reduction_coef: float = 50, top: int = 100, skip: int = 30) -> list:
        """ Reduce an fft result to "count" elements.
            This is done by summing "reduction_coef" many results into a single value.
            Whatever remains is ignored after count*reduction_coef elements.

            :param dfft: DFFT data array to reduce
            :param count: Number of partitions to split the spectrum into. Number of steps on the graph from 0hz to max hz. Default is 25.
            :param reduction_coef: Coefficient to to scale the output with. Default is 50. Sensitivity.
            :param top: Maximum value the graph will be scaled up to. Default is 100.
            :param skip: Size of partitions to skip between each partition. Larger is faster, but less precise.
            :rtype: list
            :return: A list of audio output after fast fourier transform
        """
        simplified = []
        sumt = 0
        t = int(top / count)
        for j in range(count):
            for k in range(reduction_coef):
                if dfft[skip + t * j + k] > 0:
                    sumt += dfft[skip + t * j + k]
            simplified.append(sumt)
            sumt = 0

        logging.pprint(f"Simplified FFT: {simplified}", 6)
        return simplified

    def find_device(self, name: str) -> object:
        """ Find device with the given name

        :param name: Name of the audio device to find.
        :return: Audio device
        :rtype: object
        """
        # Enum sound devices
        info = self.p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        for i in range(0, numdevices):
            # print all device names
            if (self.p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                logging.pprint(
                    f"Input Device id {i} - {self.p.get_device_info_by_host_api_device_index(0, i).get('name')}", 6)

        for i in range(self.p.get_device_count()):
            # check if device name starts with expected device name
            if (self.p.get_device_info_by_index(i)["name"].startswith(name)):
                return self.p.get_device_info_by_index(i)["index"]

    def read_once(self, count, reduction) -> list:
        """ Read immediate audio sample from the device

        :param count: Number of partitions data will be split to
        :param reduction: Reduction coefficient
        :return: Processed DFFT data
        """
        audio_data = self.raw_read()
        return self.process_audio(audio_data, count, reduction)

    def dampen(self, dfft: list, amount: float = None) -> list:
        """ Dampen the given

        :param dfft: DFFT array to dampen down.
        :param amount: Amount to dampen. If its not given, default value is self.dampen_coef
        :return: A dampened version of the DFFT array
        """
        if (amount == None):
            amount = self.dampen_coef
        for i in range(len(dfft)):
            a = dfft[i] - amount
            if (a < 0): a = 0
            dfft[i] = a

        return dfft

    def raw_read(self) -> list:
        """Read chunk sized data from stream

        :return: audio data array in format np.int16
        """
        logging.pprint("Reading data...", 6)
        in_data = self.stream.read(self.CHUNK)

        # Format audio data
        logging.pprint("Formatting data...", 6)
        audio_data = np.fromstring(in_data, np.int16)
        return audio_data

    def process_audio(self, audio_data: list, count: int, reduction: float) -> list:
        """ Process raw audio data,apply the reduction and partition steps and perform fast fourier on it.

        :param audio_data: Audio data to process.
        :param count: Number of partitions to split the data in
        :param reduction: Reduction coefficient
        :return: DFFT audio data.
        """
        try:
            # Fast Fourier Transform, 10*log10(abs) is to scale it to dB
            # and make sure it's not imaginary
            logging.pprint("Performing FFT...", 6)
            dfft = 10. * np.log10(abs(np.fft.rfft(audio_data) / len(audio_data)))
            dfft = self.dampen(dfft)
        except:
            # if something went wrong (most likely division by 0) send last output and hope it doesn't happen again.
            # Yes. This module runs on hopes and dreams.
            return self.last
        self.last = AudioController.dfft_reduce(dfft, count, reduction)
        return self.last
