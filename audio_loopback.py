"""@package Simple audio controller class for capturing computer audio. Depends on https://vb-audio.com/Cable/
"""
import pyaudio
import numpy as np
import allogate as logging
class AudioController:
    """ Simple class to capture fft data from audio stream
    """
    def __init__(self, aud_format=pyaudio.paInt16, channels=2, rate=48000, device_name="CABLE Output"):

        self.FORMAT = aud_format
        self.CHANNELS = channels
        self.RATE = rate
        self.CHUNK = 1024
        self.device_name = device_name
        self.p = pyaudio.PyAudio()
        
        self.last = []

        #open audio 
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

    def dfft_reduce(dfft, count=25, reduction_coef=20):
        """ Reduce an fft result to "count" elements.
            This is done by summing "reduction_coef" many results into a single value.
            Whatever remains is ignored after count*reduction_coef elements.
        """
        simplified = []
        sumt = 0
        for j in range(count):
            for k in range(reduction_coef):
                if(dfft[count*j+k]>0):
                    sumt+=dfft[count*j+k]
            simplified.append(sumt)
            sumt=0
            
        logging.pprint(f"Simplified FFT: {simplified}", 6)
        return simplified


    def find_device(self, name):
        """ Find device with correct name
        """
        
        #Enum sound devices
        info = self.p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        for i in range(0, numdevices):
                #print all device names
                if (self.p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                    logging.pprint(f"Input Device id {i} - {self.p.get_device_info_by_host_api_device_index(0, i).get('name')}", )

        for i in range(self.p.get_device_count()):
            # check if device name starts with expected device name
            if(self.p.get_device_info_by_index(i)["name"].startswith(name)):
                return self.p.get_device_info_by_index(i)["index"]

    def readOnce(self,count,reduction):
        """ Read data from stream but only once.
        """
        # Read chunk sized data from stream
        logging.pprint("Reading data...", 6)
        in_data = self.stream.read(self.CHUNK)

        # Format audio data
        logging.pprint("Formatting data...", 6)
        audio_data = np.fromstring(in_data, np.int16)
        
        try:
            # Fast Fourier Transform, 10*log10(abs) is to scale it to dB
            # and make sure it's not imaginary
            logging.pprint("Performing FFT...", 6)
            dfft = 10.*np.log10(abs(np.fft.rfft(audio_data)))
        except:
            # if something went wrong (most likely division by 0) send last output and hope it doesn't happen again.
            # Yes. This module runs on hopes and dreams.
            return self.last
        self.last = AudioController.dfft_reduce(dfft,count,reduction)
        return self.last




if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Audio loopback capture, FFT')
    parser.add_argument("-v","--verbose", action="count", help="Set verbosity level")
    parser.add_argument("-c","--count", help="Count to reduce the array size to")
    parser.add_argument("-r","--reduction", help="Reduction coefficient")
    parser.add_argument("-k","--constant", help="Constant to multiply output with")
    args = parser.parse_args() 

    logging.VERBOSITY=2
    if(args.verbose):
        logging.VERBOSITY=args.verbose
    
    count=25
    if(args.count):
        count=args.count
    
    reduction=20
    if(args.reduction):
        reduction=args.reduction
    
    constant=9/1200
    if(args.constant):
        constant=args.constant

    controller = AudioController(aud_format=pyaudio.paInt16, channels=2, rate=48000, device_name="CABLE Output")

    while(True):
        
        a = list(map(lambda x: int(x*constant), controller.readOnce(count,reduction)))
        logging.pprint(str(a), 2)

