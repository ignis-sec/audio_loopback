
from .audio_loopback import AudioController
import allogate as logging
import asyncio
import math


class AudioVisualizer1D:
    """ Audio visualizer class for 1D device.
        convert audio data to Keyboard color_matrix
    """
    def __init__(self, device_controller, audio_controller=None, fade=0.8, delay=0.01, dampen=2200, ceiling=2850, ambient_brightness_coef=0.1):
        """
        @param threshold - Threshold to clamp audio data when reached. Maximum audio level from input.
        @param fade - fade constant, higher the value, longer the fade effect will last. Between 0-1
        @param delay - how long to wait between each read from audio
        """

        self.device_controller = device_controller
        if audio_controller:
            self.audio = audio_controller
        else:
            self.audio = AudioController()

        self.r=255
        self.g=255
        self.b=255

        self.fade = fade
        self.delay = delay
        self.dampen = dampen
        self.ceiling = ceiling
        self.ambient_brightness_coef = ambient_brightness_coef

    def visualizeOnce(self, falloff=0.8, rows=25, col=20):
        """ Visualize current levels of audio on the razer devices, and render it
        """
        
        r = self.device_controller.r * falloff
        g = self.device_controller.g * falloff
        b = self.device_controller.b * falloff

        #audio data from stream (after fft)
        data = self.audio.readOnce(rows,col)
        logging.pprint(str(data[4]), 5)
        
        #render colors
        new_coef = (data[4]-self.dampen)/(self.ceiling - self.dampen)
        if(new_coef>=self.device_controller.coef):
            self.device_controller.coef = new_coef
        else:
            self.device_controller.coef = self.device_controller.coef * falloff

        if(self.device_controller.coef<self.ambient_brightness_coef): self.device_controller.coef=self.ambient_brightness_coef


    async def change_color(self, r,g,b):
        self.device_controller.fade(r,g,b)
        
    async def visualize(self, falloff=0.9, row=25, col=20):
        """ Loop visualizeOnce infinitely async
        """
        while True:
            self.visualizeOnce(falloff,row,col)
            await asyncio.sleep(self.delay)


class ColorMatrix():
    """A 2D matrix class holding RGB values for all keys
    """
    def __init__(self, device):
        self.red = [
            [0]*21,
            [0]*21,
            [0]*21,
            [0]*21,
            [0]*21,
            [0]*21
        ]
        self.green = [
            [0]*21,
            [0]*21,
            [0]*21,
            [0]*21,
            [0]*21,
            [0]*21
        ]*6
        self.blue = [
            [0]*21,
            [0]*21,
            [0]*21,
            [0]*21,
            [0]*21,
            [0]*21
        ]*6
        self.device=device
 
    def render(self, r=None,g=None,b=None):
        pass
        #implement for your device

class AudioVisualizer2D(AudioVisualizer1D):
    """ Audio visualizer class for 2d devices.
        convert audio data to color_matrix
    """
    def __init__(self, color_matrix, audio_controller=None, ceiling=1220, fade=0.8, delay=0.05, ambient_brightness_coef=15, dampen=1000, dampen_bias=0.92, ceiling_bias=0.98):
        """
        @param ceiling - Threshold to clamp audio data when reached. Maximum audio level from input.
        @param fade - fade constant, higher the value, longer the fade effect will last. Between 0-1
        @param delay - how long to wait between each read from audio
        """

        super().__init__(color_matrix, audio_controller, fade, delay, dampen, ceiling, ambient_brightness_coef)
        self.color_matrix = color_matrix
        self.dampen_bias = dampen_bias
        self.ceiling_bias = ceiling_bias

    def visualizeOnce(self,row=25,col=20):
        """ Visualize current levels of audio on the 2d device, and render it
        """
        #audio data from stream (after fft)
        data = self.audio.readOnce(row,col)

        #for each column of 2d device
        for i in range(len(self.color_matrix.red[0])):
            for j in range(6):

                #fade out old values
                self.color_matrix.red[j][i]=math.floor(self.color_matrix.red[j][i]*self.fade)
                self.color_matrix.green[j][i]=math.floor(self.color_matrix.green[j][i]*self.fade)
                self.color_matrix.blue[j][i]=math.floor(self.color_matrix.blue[j][i]*self.fade)

        #sanitize data, in case of -inf and division by zeroes

        current_dampening = self.dampen
        current_ceiling = self.ceiling    
        for i in range(len(self.color_matrix.red[0])):
            d = data[i]
            d = d - current_dampening
            if(d<self.ambient_brightness_coef): d=self.ambient_brightness_coef
            if(d>current_ceiling):
                d = current_ceiling
            
            #re-range the value between 0-6
            d = math.floor(d/(current_ceiling-current_dampening)*6)
            if(d>6): d=6

            current_dampening = current_dampening*self.dampen_bias
            current_ceiling = current_ceiling * self.ceiling_bias
            #depending on the fft level, rows for columns
            for j in range(d):
                if self.color_matrix.red[j][i] <= self.r:
                    self.color_matrix.red[j][i] += int(self.r * (1-self.fade))
                    if self.color_matrix.red[j][i] > self.r: self.color_matrix.red[j][i]=self.r
                if self.color_matrix.green[j][i] <= self.g: 
                    self.color_matrix.green[j][i] += int(self.g * (1-self.fade))
                    if self.color_matrix.green[j][i] > self.g: self.color_matrix.green[j][i]=self.g
                if self.color_matrix.blue[j][i] <= self.b: 
                    self.color_matrix.blue[j][i] += int(self.b * (1-self.fade))
                    if self.color_matrix.blue[j][i] > self.g: self.color_matrix.blue[j][i]=self.g
            
        #render colors
        self.color_matrix.render()

    async def visualize(self, row=20, col=5):
        """ Loop visualizeOnce infinitely
        """
        while True:
            self.visualizeOnce(row,col)
            await asyncio.sleep(self.delay)

    async def change_color(self,r,g,b):
        """ Change color, use color corrections
        """
        self.r=r
        self.g=g
        self.b=b