import asyncio
import math

import allogate as logging

from .audio_loopback import AudioController


class DeviceController:
    def __init__(self):
        pass


class AudioVisualizer:
    """ Audio visualizer class, virtual parent class. Avoid.
    convert audio data to Keyboard color_matrix

    :param device_controller: Device controller class responsible of audio to color translation.
    :param audio_controller: Audio controller object to read audio data from.
    :param fade: Fade speed for the visualization
    :param delay: Step delay amount between animations
    :param dampen: Dampening coefficient for visualization
    :param ceiling: Ceiling value for the visualization. Max value expected from the audio controller DFFT.
    :param ambient_brightness_coef: Background brightness behind the visualization
    """

    def __init__(self, device_controller: DeviceController, audio_controller: AudioController = None, fade: float = 0.8,
                 delay: float = 0.01, dampen: int = 2200, ceiling: int = 2850, ambient_brightness_coef: float = 0.1):

        self.device_controller = device_controller
        if audio_controller:
            self.audio = audio_controller
        else:
            self.audio = AudioController()

        self.r = 255
        self.g = 255
        self.b = 255

        self.fade = fade
        self.delay = delay
        self.dampen = dampen
        self.ceiling = ceiling
        self.ambient_brightness_coef = ambient_brightness_coef

    async def visualize(self, falloff: float = 0.9, row: float = 25, col: int = 20, top: int = 100):
        """ Loop visualize_once infinitely async

        :param falloff: Falloff to apply on each step
        :param row: Number of rows in the visualization
        :param col: Number of columns in the visualization
        :param top: Top value expected from the visualization
        """
        while True:
            self.visualize_once(falloff, row, col)
            await asyncio.sleep(self.delay)


class AudioVisualizer1D(AudioVisualizer):
    """ Audio visualizer class for 1D device.
    convert audio data to Keyboard color_matrix

    """

    def __init__(self, device_controller: DeviceController, audio_controller: AudioController = None, fade: float = 0.8,
                 delay: float = 0.01, dampen: int = 2200, ceiling: int = 2850, ambient_brightness_coef: float = 0.1):

        super().__init__(device_controller, audio_controller, fade, delay, dampen, ceiling, ambient_brightness_coef)

    def visualize_once(self, falloff: float = 0.8, rows: float = 25, col: int = 20, top: int = 100):
        """ Visualize current levels of audio on the razer devices, and render it

        :param falloff: Substraction coefficient to apply to last frame of the animation
        :param rows: Number of rows to have in visualization
        :param col: Number of columns to have in visualization
        :param top: Maximum number expected from the visualization
        """
        r = self.device_controller.r * falloff
        g = self.device_controller.g * falloff
        b = self.device_controller.b * falloff

        # audio data from stream (after fft)
        data = self.audio.read_once(rows, col)
        logging.pprint(str(data[4]), 5)

        # render colors
        new_coef = (data[4] - self.dampen) / (self.ceiling - self.dampen)
        if (new_coef >= self.device_controller.coef):
            self.device_controller.coef = new_coef
        else:
            self.device_controller.coef = self.device_controller.coef * falloff

        if (
                self.device_controller.coef < self.ambient_brightness_coef): self.device_controller.coef = self.ambient_brightness_coef

    async def change_color(self, r, g, b):
        """ Change device color

        :param r: Red
        :param g: Green
        :param b: Blue
        """
        self.device_controller.fade(r, g, b)


class ColorMatrix:
    """ A 2D matrix class holding RGB values for all keys

    :param device: Device controller class
    """

    def __init__(self, device):
        self.red = [
            [0] * 21,
            [0] * 21,
            [0] * 21,
            [0] * 21,
            [0] * 21,
            [0] * 21
        ]
        self.green = [
                         [0] * 21,
                         [0] * 21,
                         [0] * 21,
                         [0] * 21,
                         [0] * 21,
                         [0] * 21
                     ] * 6
        self.blue = [
                        [0] * 21,
                        [0] * 21,
                        [0] * 21,
                        [0] * 21,
                        [0] * 21,
                        [0] * 21
                    ] * 6
        self.device = device

    def render(self, r=None, g=None, b=None):
        """ Render the visualization

        :param r:
        :param g:
        :param b:
        """
        pass
        # implement for your device


class AudioVisualizer2D(AudioVisualizer):
    """ Audio visualizer class for 2d devices.
        convert audio data to color_matrix

        :param color_matrix: Color matrix to work with
        :param dampen_bias: Dampening coefficient to multiply with on every step left to right
        :param ceiling_bias: Ceiling coefficient to multiply with on every step left to right
    """

    def __init__(self, color_matrix: ColorMatrix, device_controller: DeviceController,
                 audio_controller: AudioController = None, ceiling: int = 1220, fade: float = 0.8, delay: float = 0.05,
                 ambient_brightness_coef: float = 0.1, dampen: float = 1000, dampen_bias: float = 0.92,
                 ceiling_bias: float = 0.98) -> object:

        super().__init__(device_controller, audio_controller, fade, delay, dampen, ceiling, ambient_brightness_coef)
        self.color_matrix = color_matrix
        self.dampen_bias = dampen_bias
        self.ceiling_bias = ceiling_bias

        self.minr = int(self.r * ambient_brightness_coef)
        self.ming = int(self.g * ambient_brightness_coef)
        self.minb = int(self.b * ambient_brightness_coef)

    def visualize_once(self, row: int = 25, col: int = 20, top: int = 100) -> None:
        """ Visualize current levels of audio on the 2d device, and render it

        :param row: Number of rows to have in the visualization
        :param col: Number of columns to have in visualization
        :param top: Expected top value in visualization
        """
        # audio data from stream (after fft)
        data = self.audio.read_once(row, col, top)
        # for each column of 2d device
        for i in range(len(self.color_matrix.red[0])):
            for j in range(6):

                # fade out old values
                self.color_matrix.red[j][i] = math.floor(self.color_matrix.red[j][i] * self.fade)
                self.color_matrix.green[j][i] = math.floor(self.color_matrix.green[j][i] * self.fade)
                self.color_matrix.blue[j][i] = math.floor(self.color_matrix.blue[j][i] * self.fade)

                if (self.color_matrix.red[j][i] < self.minr):
                    self.color_matrix.red[j][i] = self.minr
                if (self.color_matrix.green[j][i] < self.ming):
                    self.color_matrix.green[j][i] = self.ming
                if (self.color_matrix.blue[j][i] < self.minb):
                    self.color_matrix.blue[j][i] = self.minb

        # sanitize data, in case of -inf and division by zeroes
        current_dampening = self.dampen
        current_ceiling = self.ceiling
        for i in range(len(self.color_matrix.red[0])):
            d = data[i]
            d = d - current_dampening
            if (d < self.ambient_brightness_coef): d = self.ambient_brightness_coef
            if (d > current_ceiling):
                d = current_ceiling

            # re-range the value between 0-6
            d = math.floor(d / (current_ceiling - current_dampening) * 6)
            if (d > 6): d = 6

            current_dampening = current_dampening * self.dampen_bias
            current_ceiling = current_ceiling * self.ceiling_bias
            # depending on the fft level, rows for columns
            for j in range(d):
                if self.color_matrix.red[j][i] <= self.r:
                    self.color_matrix.red[j][i] += int(self.r * (1 - self.fade))
                    if self.color_matrix.red[j][i] > self.r: self.color_matrix.red[j][i] = self.r
                if self.color_matrix.green[j][i] <= self.g:
                    self.color_matrix.green[j][i] += int(self.g * (1 - self.fade))
                    if self.color_matrix.green[j][i] > self.g: self.color_matrix.green[j][i] = self.g
                if self.color_matrix.blue[j][i] <= self.b:
                    self.color_matrix.blue[j][i] += int(self.b * (1 - self.fade))
                    if self.color_matrix.blue[j][i] > self.g: self.color_matrix.blue[j][i] = self.g

        # render colors
        self.color_matrix.render()

    async def change_color(self, r: int, g: int, b: int) -> None:
        """ Change color, use color corrections

        :param r:
        :param g:
        :param b:
        """
        self.minr = int(self.r * self.ambient_brightness_coef)
        self.ming = int(self.g * self.ambient_brightness_coef)
        self.minb = int(self.b * self.ambient_brightness_coef)
        self.r = r
        self.g = g
        self.b = b
