#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
ENCODE TO MP3 - AUDIO FORMAT CONVERTER
    by Fmuaddib

FILENAME: enc2mp3.py
VERSION: 1.3.0
AUTHOR: Fmuaddib
LICENSE: MIT
'''

import sys
import os
import io
from io import StringIO
import argparse
from pathlib import Path
from pathlib import PurePath

APP_NAME = "enc2mp3.py"
APP_AUTHOR = "Fmuaddib"
VERSION = "1.3.0"

LOG_FILE_NAME = Path("converted_filenames_log.txt")
LOG_COMPLETED_FILENAME = Path("files_completed_log.txt")
LOG_FAILED_FILENAME = Path("files_failed_log.txt")
config = {
        "CONTAINER": 'mp3',
        "BITRATE": 0,
        "FREQUENCY": 0,
#        "BITDEPTH" : 0,
        "NORMALIZE": False,
        "DONT_KEEP_ORIGINALS": False,
        "VBR": False,
        "SUPPORTEDTYPES": ('.3gp', '.aac', '.ac3', '.aiff', '.asf', '.avi', '.caf', '.dff', '.dsf', '.dts', '.f4v', '.flac', '.flv', '.hevc', '.m4a', '.m4b', '.m4r', '.maud', '.mka', '.mkv', '.mov', '.mp2', '.mp3', '.mp4', '.mpeg', '.mpg', '.oga', '.ogg', '.opus', '.ts', '.tta', '.vob', '.voc', '.w64', '.wav', '.webm', '.wma', '.wmv'),
        "SAMPLEFORMAT": 'original',
        "FORCE_REENCODING": False,
        "TRY_REMUXING": False,       #Using stream copy to remux (no re-encoding)
        "OMIT_SUFFIX": False
}


class Parameters():
        input_path = None
        output_path = None
        output_file = None
        listfile_path = None
        config_listfile = None
        config_container = config['CONTAINER']
        config_bitrate = config['BITRATE']
        config_frequency = config['FREQUENCY']
#        config_bitdepth = config['BITDEPTH']
        config_normalize = config['NORMALIZE']
        config_sampleformat = config['SAMPLEFORMAT']
        config_dont_keep = config['DONT_KEEP_ORIGINALS']
        config_vbr = config['VBR']
        config_supported_types = config['SUPPORTEDTYPES']
        config_force_reencoding = config['FORCE_REENCODING']
        config_try_remuxing = config['TRY_REMUXING']
        config_omit_suffix = config['OMIT_SUFFIX']

files_completed = set()
files_failed = set()
final_files_list = set()


def replace_extension(filename, ext, expected_real_ext=None):
    filename = str(filename)
    name, real_ext = os.path.splitext(filename)
    return '{0}.{1}'.format(name if not expected_real_ext or real_ext[1:] == expected_real_ext else filename, ext)

def main():
        print("ENC2MP3 by Fmuaddib")
        print("Version: {}".format(VERSION))
        print("USAGE:")
        print("       SINGLE:  enc2mp3.py <INPUT FILENAME> -c mp3")
        print("       BATCH:   enc2mp3.py <INPUT FOLDER> -l files.txt -c mp3")
        print(".......ALL SOUND FILES IN FOLDER:  enc2mp3.py <INPUT FOLDER> -c mp3")
        print()
        '''Parse arguments from command line'''
        parser = argparse.ArgumentParser(
                prog="enc2mp3.py",
                description='A Python CLI program for converting audio files to MP3 or MP4 (.m4a, .m4b, .mp4, .mov) format')
        parser.add_argument('input', type=str, help='Input file or directory')
        parser.add_argument('-l', '--listfile', type=str, default=None, help='Path to .txt file with a List of filenames to convert (default: all files in input folder)')
        parser.add_argument('-o', '--output', type=str, default=Path.cwd(), help='Output folder (default: current folder)')
        parser.add_argument('-b', '--bitrate', default=config['BITRATE'], type=int, help='Preferred bitrate for audio files in kb/s (default: auto)')
        parser.add_argument('-f', '--frequency', default=config['FREQUENCY'], type=int, help='Preferred frequency for audio files in Hz (example: 44100) (default: original)')
#        parser.add_argument('-d', '--bitdepth', default=config['BITDEPTH'], type=int, help='Preferred bitdepth for audio files in bits (original, 16, 32) (default: original)')        
        parser.add_argument('-n', '--normalize', default=config['NORMALIZE'], help='Normalize Volume levels (option -af "loudnorm" in FFMpeg) (default: False)', action="store_true")
        parser.add_argument('-k', '--dont-keep', default=config['DONT_KEEP_ORIGINALS'], help='Don\'t Keep original files (default: False)', action="store_true")
        parser.add_argument('-v', '--vbr', default=config['VBR'], help='Encode audio with variable bitrate (default: False)', action="store_true")
        parser.add_argument('-s', '--sampleformat', default=config['SAMPLEFORMAT'], help='Audio sampling format (original, s16, s16p, s32, s32p, fltp) (default: original)', choices=["original", "s16", "s16p", "s32", "s32p", "fltp"], metavar="original/s16/s16p/s32/s32p/fltp")
        parser.add_argument('-c', '--container', default=config['CONTAINER'], help='Container file format ( mp3, m4a, caf, flac) (default: mp3)', choices=["mp3", "m4a", "caf", "flac"], metavar="mp3/m4a/caf/flac")
        parser.add_argument('-m', '--try_remuxing', default=config['TRY_REMUXING'], help='Try to use stream copy to remux audio leaving the original codec (avoiding re-encoding if possible) (default: False)', action="store_true")
        parser.add_argument('-r', '--force_reencoding', default=config['FORCE_REENCODING'], help='Force reencoding when the input and output file extensions are the same (default: False)', action="store_true")
        parser.add_argument('-x', '--omit_suffix', default=config['OMIT_SUFFIX'], help='Do not add the "(was XXX)" suffix to the converted file name (default: False)', action="store_true")
        args = parser.parse_args()



        ## DELETE OLD LOGS
        ## If file exists, delete it ##
        if Path.is_file(LOG_FILE_NAME):
                Path.unlink(LOG_FILE_NAME)
        ## If file exists, delete it ##
        if Path.is_file(LOG_COMPLETED_FILENAME):
                Path.unlink(LOG_COMPLETED_FILENAME)
        ## If file exists, delete it ##
        if Path.is_file(LOG_FAILED_FILENAME):
                Path.unlink(LOG_FAILED_FILENAME)



        # Setup the conversion parameters #
        params = Parameters()

        params.input_path = Path(args.input)
        params.output_path = Path(args.output)
        params.listfile_path = args.listfile
        params.config_bitrate = args.bitrate
        params.config_frequency = args.frequency
        #params.config_bitdepth = args.bitdepth
        params.config_normalize = args.normalize
        params.config_sampleformat = args.sampleformat
        params.config_container = args.container.lower()
        params.config_dont_keep = args.dont_keep
        params.config_vbr = args.vbr
        params.config_supported_types = config['SUPPORTEDTYPES']
        params.config_force_reencoding = args.force_reencoding
        params.config_try_remuxing = args.try_remuxing
        params.config_omit_suffix = args.omit_suffix

        all_is_valid = True

        # Check Input File or Folder or File List #
        if Path.is_dir(params.input_path) or Path.is_file(params.input_path) or params.listfile_path is not None:
                all_is_valid = True
        else:
                all_is_valid = False
                print("The input path/file is invalid! " + str(params.input_path))

        # Check Output Folder #
        if not Path.is_dir(params.output_path):
                all_is_valid = False
                print("The output path is invalid! "+str(params.output_path))
        else:
                params.output_path =Path(PurePath.joinpath(Path.cwd(), Path(params.output_path)))

        # Check Filenames List from Txt File
        if params.listfile_path is not None:
                params.listfile_path=Path(params.listfile_path)
                if Path.is_file(params.listfile_path):
                        params.config_listfile = load_list_file(params.listfile_path)
                else:
                        all_is_valid = False
                        print("The files list path is invalid! "+ str(params.listfile_path))

        # If All Is Valid, Start The Conversion #
        if all_is_valid:
                if params.listfile_path is not None and params.config_listfile is not None:
                        params.input_path = Path(PurePath.joinpath(Path.cwd(), Path(params.input_path)))
                        convert_folder(params)
                else:
                        if Path.is_dir(params.input_path):
                                params.input_path = Path(PurePath.joinpath(Path.cwd(), Path(params.input_path)))
                                convert_folder(params)
                        elif Path.is_file(params.input_path):
                                params.input_path = Path(PurePath.joinpath(Path.cwd(), Path(params.input_path)))
                                convert_file(params)
                        else:
                            sys.exit()
        else:
                sys.exit()

        saveTextFile("\n".join(files_completed), LOG_COMPLETED_FILENAME)
        saveTextFile("\n".join(files_failed), LOG_FAILED_FILENAME)
        
        for filename_record in final_files_list:
                write_filename_to_txt_final_output_log(filename_record, True)
        


## Logger
def write_filename_to_txt_final_output_log(filePath, full_path=False):
        outputFile = Path(filePath)
        if full_path is False:
                filename = str(outputFile.name)
        else:
                filename = str(outputFile.absolute())
        append_lines_to_log_file(LOG_FILE_NAME, filename)

## EXTERNAL HELPER FUNCTION
def convert_to_format(filename, container_format='mp4', vbr_mode=False, bitrate=0, try_remuxing=False, delete_originals=True):
        # Setup the conversion parameters #
        params = Parameters()

        params.input_path = Path(filename)
        params.output_path = Path(filename).parent
        params.listfile_path = None
        params.config_container = container_format
        params.config_omit_suffix = True
        params.config_dont_keep = delete_originals
        params.config_bitrate = bitrate
        params.config_vbr = vbr_mode
        params.config_try_remuxing = try_remuxing
        
        
        all_is_valid = True

        # Check Input File or Folder or File List #
        if Path.is_dir(params.input_path) or Path.is_file(params.input_path) or params.listfile_path is not None:
                all_is_valid = True
        else:
                all_is_valid = False
                print("The input path/file is invalid! " + str(params.input_path))

        # Check Output Folder #
        if not Path.is_dir(params.output_path):
                all_is_valid = False
                print("The output path is invalid! "+str(params.output_path))
        else:
                params.output_path =Path(PurePath.joinpath(Path.cwd(), Path(params.output_path)))

        # Check Filenames List from Txt File
        if params.listfile_path is not None:
                params.listfile_path=Path(params.listfile_path)
                if Path.is_file(params.listfile_path):
                        params.config_listfile = load_list_file(params.listfile_path)
                else:
                        all_is_valid = False
                        print("The files list path is invalid! "+ str(params.listfile_path))

        # If All Is Valid, Start The Conversion #
        if all_is_valid:
                if params.listfile_path is not None and params.config_listfile is not None:
                        params.input_path = Path(PurePath.joinpath(Path.cwd(), Path(params.input_path)))
                        convert_folder(params)
                else:
                        if Path.is_dir(params.input_path):
                                params.input_path = Path(PurePath.joinpath(Path.cwd(), Path(params.input_path)))
                                convert_folder(params)
                        elif Path.is_file(params.input_path):
                                params.input_path = Path(PurePath.joinpath(Path.cwd(), Path(params.input_path)))
                                convert_file(params)
                        else:
                            sys.exit()
        else:
                sys.exit()
        
        print("File " + str(params.output_file) + "successfully converted.")
        return str(params.output_file)
        


def load_list_file(list_file_name):
        clean_lines = set()
        if Path.is_file(list_file_name):
                with open(list_file_name, encoding='utf8') as f:
                        lines = f.readlines()
                        clean_lines = set([line.rstrip().strip() for line in lines])
                        print(str(len(clean_lines)+1) + " files received as input:")
                        for fline in clean_lines:
                            print(str(fline))
                return clean_lines
        else:
                print("Error : " + str(list_file_name) + " is not a valid file!")
                return None




def load_text_file(txt_file_name):
        contents = None
        txt_file_name = Path.joinpath(Path.cwd(), Path(txt_file_name))
        if Path.is_file(txt_file_name):
                with open(txt_file_name, encoding='utf8') as f:
                        contents = f.read()
                        print(contents)
                return contents
        else:
                print("Error : "+str(txt_file_name)+" is not a valid file!")
                return None

def saveTextFile(text, filename):
        file_path = Path(PurePath.joinpath(Path.cwd(), Path(filename)))
        with open(file_path, "a+", encoding="utf-8") as f:
                f.write(text.strip())
        print("Saved text file in: "+str(file_path))
        print()
        return


def append_lines_to_log_file(log_file_name, lines_to_append):
        log_file_name = Path(PurePath.joinpath(Path.cwd(),Path(log_file_name)))
        # Open the file in append & read mode ('a+')
        with open(log_file_name, "a+", encoding="utf-8") as file_object:
                appendEOL = False
                # Move read cursor to the start of file.
                file_object.seek(0)
                # Check if file is not empty
                data = file_object.read(100)
                if len(data) > 0:
                        appendEOL = True
                if isinstance(lines_to_append,str):
                        # If file is not empty then append '\n' before first line for
                        # other lines always append '\n' before appending line
                        if appendEOL == True:
                                file_object.write("\n")
                        else:
                                appendEOL = True
                        # Append element at the end of file
                        file_object.write(lines_to_append)
                elif isinstance(lines_to_append,list):
                        # Iterate over each string in the list
                        for line in lines_to_append:
                                # If file is not empty then append '\n' before first line for
                                # other lines always append '\n' before appending line
                                if appendEOL == True:
                                        file_object.write("\n")
                                else:
                                        appendEOL = True
                                # Append element at the end of file
                                file_object.write(line)
                else:
                        print('Error writing log: please provide a string or a list.')




## CONVERT ALL AUDIO FILES IN A FOLDER
def convert_folder(params):
        print("Processing Folder: " + str( params.input_path))
        for file_name in sorted(Path.iterdir(params.input_path)):
                if params.config_listfile is not None:
                        if Path(file_name).name in params.config_listfile:
                                launch_task(file_name, params)
                else:
                        launch_task(file_name, params)




def launch_task(file_name, params):
        print(f"Processing File {str(file_name)}")
        if Path(file_name).suffix in tuple(params.config_supported_types):
                file_name = Path(file_name)
                file_name_ext = Path(file_name).suffix.replace('.','')
                without_ext = Path(file_name).stem
                if params.config_omit_suffix is False:
                        without_ext += " (was " + file_name_ext + ")"
                input_file = Path( PurePath.joinpath(params.input_path, file_name))
                output_file_name = "".join([without_ext, "." + params.config_container])
                output_file = Path( PurePath.joinpath(params.output_path, Path( output_file_name)))
                params.output_file = str(output_file)
                ExecuteFFMpeg(input_file, output_file, params)
                print("Finished Converting File: "+str(input_file) + " to " + params.config_container)

                return
        else:
                return

## CONVERT A SINGLE FILE
def convert_file(params):
        print("Processing single audio file:" + str( params.input_path))
        input_file = params.input_path.name
        input_file_ext = params.input_path.suffix.replace('.','')
        without_ext = params.input_path.stem
        if params.config_omit_suffix is False:
                without_ext += " (was "+ input_file_ext + ")"
        output_file_name = "".join([without_ext, '.' + params.config_container])
        output_file =Path(PurePath.joinpath(params.output_path, output_file_name))
        params.output_file = str(output_file)
        ExecuteFFMpeg(input_file, output_file, params)
        print("Finished Converting File: "+str(input_file) + " to " + params.config_container)


## FUNCTION THAT CALLS FFMPEG ##
def ExecuteFFMpeg(input_file, output_file, params):
        print("Calling FFMPEG..")

        ## NORMALIZE COMMAND
        if params.config_normalize is True:
                norm_cmd = '-af "loudnorm"'
        else:
                norm_cmd = None

        ## AUDIO CODEC COMMAND AND OUTPUT CONTAINER SPECIFIC SETTINGS
        if params.config_container == 'mp3':
                codecaudio_cmd = '-c:a libmp3lame'
                maxbitrate = 320
                minbitrate = 192
                bitrate_cmd = None
                faststart_cmd = None
                container_cmd = '-f mp3'
                lossless = False
        elif params.config_container == 'm4a' or params.config_container == 'mp4' or params.config_container == 'm4b' or params.config_container == 'mov':
                codecaudio_cmd = '-c:a aac'
                maxbitrate = 270
                minbitrate = 160
                bitrate_cmd = None
                faststart_cmd = "-movflags +faststart"
                # .m4a is not a recommended ISO extension
                # but is typically used by Apple. It has
                # a limited list of acceptable codecs as
                # compared to .mp4.
                # FFmpeg format flag for m4a is '-f ipod'.
                # But it is best to use '-f mp4' anyway.
                container_cmd = '-f mp4'
                lossless = False
        elif params.config_container == 'caf':
                codecaudio_cmd = '-c:a aac'
                maxbitrate = 270
                minbitrate = 160
                bitrate_cmd = None
                faststart_cmd = None
                container_cmd = '-f caf'
                lossless = False
        elif params.config_container == 'flac':
                codecaudio_cmd = '-c:a flac'
                maxbitrate = None
                minbitrate = None
                bitrate_cmd = None
                faststart_cmd = None
                container_cmd = None
                lossless = True
        else:
                print(f"ERROR : Output format {params.config_container} not supported.")
                sys.exit(1)
                


        ## BITRATE COMMAND
        if params.config_vbr is True and lossless is False:
                bitrate_cmd = '-q:a 1'
        else:
                if params.config_bitrate == 0:
                        bitrate_cmd = '-b:a '+ str(maxbitrate)+'k'
                else:
                        if params.config_bitrate > maxbitrate:
                                params.config_bitrate = maxbitrate
                        if params.config_bitrate < minbitrate:
                                params.config_bitrate = minbitrate
                        bitrate_cmd = '-b:a '+ str(params.config_bitrate)+'k'

        # FREQUENCY AND BIT DEPTH FILTERS
        # "16 and 24 bit samples" is referring to "Bit Depth",
        # as opposed to "Bit Rate". "Bit Depth" is sometimes also
        # referred to (By VLC for example) as "Bits per Sample".
        # FFmpeg's FLAC encoder supports sample bit depths of 16 and 24 bits, 
        # the latter padded to 32-bit. So for 24-bit, 
        # you will have to use a filter in-between.
        # EXAMPLES:
        # ffmpeg -i in.wav -af aformat=s16:44100 out.flac
        # ffmpeg -i in.wav -af aformat=s32:176000 out.flac
        # freq_cmd = '-af aformat=s{str(params.config_bitdepth)}:' + str(params.config_frequency)
        # 
        
        
        
        ## FREQUENCY RESAMPLING COMMAND
        if params.config_frequency == 0:
                freq_cmd = None
        else:
                freq_cmd = '-ar ' + str(params.config_frequency)
        
        ## SAMPLING FORMAT COMMAND
        if params.config_sampleformat == 'original':
                samplefmt_cmd = None
        else:
                samplefmt_cmd = '-sample_fmt '+ str(params.config_sampleformat)

        ## INPUT / OUTPUT COMMANDS
        input_file_cmd = '-i "' + str(input_file) +'"'
        output_file_cmd = '"' + str(output_file) + '"'

        # EXTENSIONS
        input_extension = Path(input_file).suffix.replace('.','').lower()
        output_extension = Path(output_file).suffix.replace('.','').lower()

        ## Do not force reencoding if the files are the same container format
        if input_extension == output_extension or params.config_try_remuxing:
                if params.config_container == 'mp3':
                        if params.config_force_reencoding is False:
                                #codecaudio_cmd = '-c:a copy'
                                codecaudio_cmd = '-c:a libmp3lame'
                                bitrate_cmd = None
                                faststart_cmd = None
                elif params.config_container == 'm4a' or params.config_container == 'mp4' or params.config_container == 'm4b' or params.config_container == 'mov':
                        if params.config_force_reencoding is False:
                                #codecaudio_cmd = '-c:a copy'
                                codecaudio_cmd = None
                                bitrate_cmd = None
                                faststart_cmd = "-movflags +faststart"
                elif params.config_container == 'caf':
                        if params.config_force_reencoding is False:
                                #codecaudio_cmd = '-c:a copy'
                                codecaudio_cmd = None
                                bitrate_cmd = None
                                faststart_cmd = None
                elif params.config_container == 'flac':
                        if params.config_force_reencoding is False:
                                #codecaudio_cmd = '-c:a copy'
                                codecaudio_cmd = None
                                bitrate_cmd = None
                                faststart_cmd = None

        exclude_video = "-vn" # avoid using this because it strips the thumbnail image along with the video.
        
        exclude_subtitles = "-sn" # no need for subtitles in audio
        
        mapping_cmd = "-map 0:v? -map -0:V? -map 0:a:0 -c:v copy" # exclude only video stream ('V') but not images, covers, and attachments.
        
        metadata_cmd = "-map_metadata g" # default mapping metadata as general metadata. (not needed for now).
        
        recast_cmd = "-recast_media" # Allow forcing a decoder of a different media type than the one detected
                                     # or designated by the demuxer. Useful for decoding media data muxed
                                     # as data streams. (not needed for now).

        print("OUTPUT FILE:  " + str(output_file))

        # EXECUTE FFMPEG
        # https://trac.ffmpeg.org/wiki/Map
        # encodings examples:
        # MP3 320k cbr = '-c:a libmp3lame -b:a 320k'
        # MP3 190-250 vbr = '-c:a libmp3lame -q:a 1'
        # MP3 auto = '-c:a libmp3lame -b:a 320k'
        # MP4 270k cbr = '-c:a aac -b:a 270k -movflags +faststart'
        # MP4 192k cbr = '-c:a aac -b:a 192k -movflags +faststart'
        # MP4 auto = '-c:a aac -b:a 270k -movflags +faststart'
        # ffmpeg -i "input.flac" -map 0 -map -0:V -c:v copy -map_metadata g -y "output.mkv"
        # ffmpeg -i "input.mp4" -map 0 -map -0:V -c:v copy -map_metadata g -y "output.flac"
        # EXAMPLE:
        # WEBM TO MP4 = ffmpeg -v verbose -i "Sia.Unstoppable.webm" -vn -c:a aac -b:a 192k -movflags +faststart -y "Sia.Unstoppable (was webm).m4a"
        command_parts = [input_file_cmd, exclude_subtitles, mapping_cmd, codecaudio_cmd, bitrate_cmd, faststart_cmd, samplefmt_cmd, norm_cmd, freq_cmd, "-y", output_file_cmd]
        command_part_one = "ffmpeg"
        command_full = command_part_one + " "

        for part in command_parts:
                if part:
                        command_full += part + " "

        print("EXECUTING : " + command_full)
        os.system(command_full)

        if Path.is_file(output_file):
                print("Done!")
                if params.config_dont_keep is True:
                        input_f = Path(input_file)
                        input_stem = input_f.stem
                        new_input_name = f"{input_stem}_old{input_f.suffix}"
                        renamed_input = input_f.rename(new_input_name)
                        output_f = Path(output_file)
                        new_output_name = f"{input_stem}{output_f.suffix}"
                        renamed_output = output_f.rename(new_output_name)
                        print("DELETING INPUT FILE " + str(renamed_input))
                        renamed_input.unlink()
                        output_file = renamed_output
                        params.output_name = str(output_file)
                        print("OUTPUT FILE RENAMED TO " + str(renamed_output))
                files_completed.add(str(input_file))
                final_files_list.add(str(output_file))
        else:
                print("Failed Converting "+str(input_file))
                files_failed.add(str(input_file))



if __name__ == '__main__':
        main()
        