from .audio_loopback import *
from .audio_visualizer import *
import sys
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Audio loopback capture, FFT')
    parser.add_argument("-v", "--verbose", action="count", help="Set verbosity level")
    parser.add_argument("-c", "--count", help="Count to reduce the array size to")
    parser.add_argument("-r", "--reduction", help="Reduction coefficient")
    parser.add_argument("-k", "--constant", help="Constant to multiply output with")
    parser.add_argument("-n", "--name", help="Device name to listen from. \"CABLE Output\" for windows, \"pulse\" for linux.")
    args = parser.parse_args()

    logging.VERBOSITY = 2
    if args.verbose:
        logging.VERBOSITY = args.verbose

    count = 25
    if args.count:
        count = args.count

    reduction = 20
    if args.reduction:
        reduction = args.reduction

    constant = 9 / 1200
    if args.constant:
        constant = args.constant

    if not args.name:
        if(sys.platform == 'win32'):
            args.name = "CABLE Output"
        else:
            args.name = "pulse"
    controller = AudioController(aud_format=pyaudio.paInt16, channels=2, rate=48000, device_name=args.name)

    while True:
        a = list(map(lambda x: int(x * constant), controller.read_once(count, reduction)))
        logging.pprint(str(a), 2)
