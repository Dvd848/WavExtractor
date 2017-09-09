import os
import sys
import mmap
import argparse
import traceback
from ctypes import *
from CustomConfig import *

class mmapEx(mmap.mmap):
    def finditer(self, str):
        pos = 0
        while (pos >= 0):
            pos = self.find(str, pos)
            if pos != -1:
                yield pos
                pos += 1
        raise StopIteration

        
class WavHeaderStart(Structure):
    _pack_ = True
    _fields_ = [
        ("ChunkID",     c_char * 4),
        ("ChunkSize",   c_uint32),
        ("Format",      c_char * 4)
    ] 


class WavExtractor:

    ########################################
    # Config 
    ########################################
    class WavExtractorConfig(object):

        ### -------------------------------------------

        @property
        @CustomConfigDecorators.getter
        def out_dir(self):
            return os.path.join(os.getcwd(), "WAVs")

        @out_dir.setter
        @CustomConfigDecorators.setter
        def out_dir(self, value):
            if not value[-1] == os.sep:
                value = value + os.sep
            if not os.access(os.path.abspath(os.path.join(value, os.pardir)), os.W_OK):
                raise ValueError("Illegal path: {}".format(value))
            return value

        ### -------------------------------------------

        @property
        @CustomConfigDecorators.getter
        def out_file_name_prefix(self):
            return "output_"

        @out_file_name_prefix.setter
        @CustomConfigDecorators.setter
        def out_file_name_prefix(self, value):
            if value.strip() == "":
                raise ValueError("Illegal name: {} (Can't be empty)".format(value))
            if "{" in value:
                raise ValueError("Illegal name: {}".format(value))
            return value

        ### -------------------------------------------

        @property
        @CustomConfigDecorators.getter
        def out_file_name_suffix(self):
            return ".wav"

        ### -------------------------------------------

        @property
        @CustomConfigDecorators.getter
        def debug_skip_write(self):
            return True

        ### -------------------------------------------

        @property
        @CustomConfigDecorators.getter
        def debug_enable_log(self):
            return True

        ### -------------------------------------------

    ########################################
    # Implementation
    ########################################

    def __init__(self, resource_path):
        if not os.path.exists(resource_path) or not os.path.isfile(resource_path):
            raise ArgumentError("Error! Can't find resource path {}".format(resource_path))
        self.resource_path = resource_path
        self.ResetConfig()
        


    @staticmethod
    def is_valid_wav_header(wavHeader):
        if (wavHeader.ChunkID != "RIFF"):
            return False
        if (wavHeader.Format != "WAVE"):
            return False
        return True

    def log(self, msg):
        if not self.config.debug_enable_log:
            return

        print msg

    def getNextOutputPath(self):
        if not os.path.exists(self.config.out_dir):
            raise RuntimeError("Expecting {} to exist".format(self.config.out_dir))
        base_name = self.config.out_file_name_prefix \
                    + "{}" \
                    + self.config.out_file_name_suffix
        counter = 0
        while True:
            current_name = base_name.format(counter)
            current_path = os.path.join(self.config.out_dir, current_name)
            if (not os.path.exists(current_path)):
                break
            counter += 1
        return current_path


    def Config(self, **kwargs):
        try:
            for key, val in kwargs.iteritems():
                setattr(self.config, key, val)
        except AttributeError as e:
            msg = "Error: Can't set attribute {}!".format(key)
            self.log(msg)
            raise AttributeError(msg)

    def ResetConfig(self):
        self.config = self.WavExtractorConfig()
        self.config.out_file_name_prefix = os.path.splitext(os.path.basename(self.resource_path))[0] + "_"


    def Extract(self):
        try:
            self.log("Will output files to {}".format(self.config.out_dir))
            if not os.path.exists(self.config.out_dir):
                os.makedirs(self.config.out_dir)

            with open(self.resource_path, "r+b") as input_f:
                mm = mmapEx(input_f.fileno(), 0)
                for riffStart in mm.finditer('RIFF'):
                    wavHeader = WavHeaderStart.from_buffer_copy(mm[riffStart:])
                    if not self.is_valid_wav_header(wavHeader):
                        continue

                    self.log("Found WAV file of size 0x{:02X} at offset 0x{:02X}".format(wavHeader.ChunkSize, riffStart))

                    if riffStart + wavHeader.ChunkSize > mm.size():
                        self.log("\tWarning: File size {} is out of bounds".format(wavHeader.ChunkSize))
                        continue

                    out_file_path = self.getNextOutputPath()
                    if not self.config.debug_skip_write:
                        with open(out_file_path, "wb") as output_f:
                            output_f.write(mm[riffStart:riffStart + wavHeader.ChunkSize])
                            self.log("\tFile {} created".format(out_file_path))
                    else:
                        self.log("\tSkipping write due to debug flag")

                    print "---"


        except IOError as e:
            raise e


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract WAV files from a resource file')
    parser.add_argument('-i','--input_file', help='Path to resouce file', required=True)
    parser.add_argument('-od','--output_dir', help='Path to output directory', required=False)
    args = parser.parse_args()
    try:
        we = WavExtractor(args.input_file)
        if args.output_dir:
            we.Config(out_dir = args.output_dir)
        we.Extract()
        sys.exit(0)
    except Exception:
        print "Error!"
        traceback.print_exc()
        sys.exit(-1)
