#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
  GET YOUTUBE AUDIO FILE
    by Fmuaddib

FILENAME: get_youtube_audio_file.py
VERSION: 1.5.3
AUTHOR: Fmuaddib
LICENSE: MIT
'''


import os
import sys
import re
import argparse
from io import StringIO
from pathlib import Path
import urllib
import urllib.request
from time import sleep
import yt_dlp
from pydantic import BaseModel, HttpUrl, ValidationError
import embed_cover
import enc2mp3

class InputURL(BaseModel):
    input_url: HttpUrl


APP_NAME = "get_youtube_audio_file.py"
APP_AUTHOR = "Fmuaddib"
VERSION = "1.5.3"

SUBTITLES_REGEX_CODES = 'en.*,fr.*,de.*,it.*,pt.*,es.*,ar.*,ja.*,ko.*,zh.*,da.*,nl.*,ca.*,el.*,he.*,hi.*,no.*,pl.*,ro.*,ru.*,sv.*,ua.*,vi.*,tr.*,th.*,id.*,is.*,hu.*,ga.*,fa.*,et.*,cs.*,hr.*,eu.*,bg.*,sq.*,af.*,be.*,lt.*,ms.*,mk.*,ku.*,ml.*,nn.*,nb.*,rm.*,sr.*,sk.*,sl.*,sb.*,ur.*,cy.*,ji.*,zu.*,tn.*,xh.*,ve.*,ts.*,pa.*,mt.*,lv.*,-live_chat'
SUBTITLES_DEFAULT_REGEX_CODES = '"en.*,it.*,fr.*,ja.*,zh.*,-live_chat"'

OUTPUT_FILES_SUFFIXES = {'.mov', '.mp4', '.m4a', '.m4b', '.MOV', '.MP4', '.M4A', '.M4B','.mp3', '.MP3','.webm', '.WEBM','.mkv', '.MKV','.caf','.CAF'}
FORMATS_SUPPORTING_THUMB_EMBED = {'.mov', '.mp4', '.m4a', '.m4b', '.MOV', '.MP4', '.M4A', '.M4B','.mp3', '.MP3','.mkv', '.MKV'}


## RETRY DECORATOR CLASS
## Example:
##  1) First you decorate a function like this:
##
##  @catch(max=10, callback=callback)
##  def test(cls, ok, **kwargs):
##      raise ValueError('ok')
##
##  2) Then you define your custom callback function:
##
##  def callback(cls, error, args, kwargs):
##      print('func args', args, 'func kwargs', kwargs)
##      print('error', repr(error), 'trying', cls.index)
##
##  3) Finally you just call the function:
##
##  test(1, message='hello')
##
class catch:
        def __init__(self, max=1, callback=None):
                self.max = max
                self.callback = callback

        def set_max(self, max):
                self.max = max

        def handler(self, *args, **kwargs):
                self.index = 0
                while self.index < self.max:
                        self.index += 1
                        try:
                                print("\nTry Number {}".format(self.index))
                                return self.func(*args, **kwargs)

                        except KeyboardInterrupt:
                                sys.exit()


                        except Exception as error:
                                if callable(self.callback):
                                        self.callback(self, error, args, kwargs)

        def __call__(self, func):
                self.func = func
                return self.handler


def callback(cls, error, args, kwargs):
        print('func args', args, 'func kwargs', kwargs)
        print('error', repr(error), '\nFailed Try Number ', cls.index)
        if cls.index == 2:
                return
        else:
                sleep(1)

# END RETRY DECORATOR


## Name of the log file
log_file_name = "filenames.txt"
final_output_list_filename = "final_output_list.txt"


## Console messages
class MyLogger(object):
        def debug(self, msg):
        #     pass
                if ("ETA" in msg) and ("[download]" in msg):
                        print(msg,end='\r')
                else:
                        print(msg)

        def warning(self, msg):
        #     pass
                print(msg)

        def error(self, msg):
                print(msg)


## Logger
def write_filename_to_txt_final_output_log(filePath, full_path=False):
        outputFile = Path(filePath)
        if full_path is False:
                filename = str(outputFile.name)
        else:
                filename = str(outputFile.absolute())
        append_lines_to_log_file(final_output_list_filename, filename)

## Logger
def write_filename_to_txt_log(filePath, full_path=False):
        outputFile = Path(filePath)
        if full_path is False:
                filename = str(outputFile.name)
        else:
                filename = str(outputFile.absolute())
        append_lines_to_log_file(log_file_name, filename)

## Logger helper
def append_lines_to_log_file(log_file_name, lines_to_append):
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


@catch(max=5, callback=callback)
def download_url(url, ydl_opts):
                print("\nTrying to Download Audio From {}.".format(url))
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

completed_files = set()
completed_files_abspath = set()
final_files_list = set()

def match_format_type_suffix(input_text):
    #print(f"DEBUG: >{input_text}< match test regex:")
    pattern = re.compile(r"^\.f[0-9]+$", re.IGNORECASE)
    if pattern.match(input_text):
        #print("SUFFIX IS TRUE MATCH")
        return True
    else:
        #print("SUFFIX IS NO MATCH")
        return False
    
def remove_format_suffix(file_name):
    #print(f"ORIGINAL FILENAME: {file_name}")
    extens=Path(file_name).suffix
    #print(f"ORIGINAL EXTENSION: {extens}")
    original_filename = Path(file_name)
    file_name = Path(file_name).with_suffix("")
    #print(f"REMOVED SUFFIX: {file_name}")
    if match_format_type_suffix(file_name.suffix):
        file_name = Path(file_name).with_suffix("")
    file_name = Path(str(file_name)+extens)
    #print(f"READDED SUFFIX: {file_name}")
    return file_name

def my_hook(d):

        if d['status'] == 'finished':
                file_tuple = os.path.split(os.path.abspath(d['filename']))
                file_name = file_tuple[1]
                print("Done downloading {}".format(file_name))
                file_name = remove_format_suffix(file_name)
                write_filename_to_txt_log(file_name)
                if Path(file_name).suffix in OUTPUT_FILES_SUFFIXES:
                    print()
                    #print(f"ADDING {file_name} to COMPLETED_FILES list.")
                    completed_files.add(file_name)
                    #print(f"ADDING {os.path.abspath(d['filename'])} to COMPLETED_FILES_ABSPATH list.")
                    completed_files_abspath.add(os.path.abspath(d['filename']))
                    print()

        if d['status'] == 'downloading':
                file_tuple = os.path.split(os.path.abspath(d['filename']))
                file_name = file_tuple[1]
                #print("{} {} {}".format(d['filename'], d['_percent_str'], d['_eta_str']), end='\r')


def get_list_of_urls_from_file(file_name):
        with open(file_name, 'r') as fh:
                urls_list = [line for line in fh]
        return urls_list
        
        
def replace_extension(filename, ext, expected_real_ext=None):
    name, real_ext = os.path.splitext(filename)
    return '{0}.{1}'.format(name if not expected_real_ext or real_ext[1:] == expected_real_ext else filename, ext)
    
def change_filename_extension(filename, new_ext):
    name, old_ext = os.path.splitext(filename)
    return '{0}.{1}'.format(name, new_ext)


# Specify command line options here
# EXAMPLE:
# ydl_opts = {
#   'format': 'bestaudio/best',
#   'postprocessors': [{
#     'key': 'FFmpegExtractAudio',
#     'preferredcodec': 'mp3',
#     'preferredquality': '192',
#   }],
#  'logger': MyLogger(),
#  'progress_hooks': [my_hook],
# }
#
ydl_opts = {
            "format":"bestaudio[protocol^=http]",
            "verbose":False,
            "outtmpl":"%(title)s.%(ext)s",
            "source_address":"0.0.0.0",
            "sleep_interval":5,
            "sleep_interval_requests":10,
            "sleep_interval_subtitles": 15,
            "max_sleep_interval":12,
            "restrictfilenames":False,
            "hls_prefer_native":False,
            "prefer_ffmpeg":True,
            "geo_bypass":True,
            "ignoreerrors":False,
            "updatetime":False,
            "retries": 256,
            "continuedl":False,
            "cachedir":False,
            "no_color": True,
            "fixup": "detect_or_warn",
            "download_archive":"downloaded.txt",
            'logger': MyLogger(),
            'progress_hooks': [my_hook],
            "consoletitle": False,
            "forcedescription": False,
            "forcefilename": False,
            "forceformat": False,
            "forcethumbnail": True,
            "forcetitle": False,
            "forceurl": False,
            "listformats": None,
            "logtostderr": False,
            "matchtitle": None,
            "max_downloads": None,
            "noplaylist": True,
            "nooverwrites": False,
            "nopart": False,
            "noprogress": False,
            "password": None,
            "playliststart": 1,
            "prefer_free_formats": False,
            "quiet": False,
            "ratelimit": None,
            "rejecttitle": None,
            "simulate": False,
            "subtitleslang": None,
            "subtitlesformat": "best",
            "test": False,
            "usenetrc": False,
            "username": None,
            "writedescription": False,
            "writeinfojson": False,
            "writesubtitles": False,
            "writethumbnail": True,
            "allsubtitles": False,
            "listsubtitles": False,
            "socket_timeout": 20,
            "postprocessors": [{
#                'key': 'FFmpegVideoRemuxer',
#                'preferedformat': 'mp4',
#            },{
#                'key': 'EmbedThumbnail',
#                'already_have_thumbnail': False,
#            },{
                'key': 'FFmpegMetadata',
                'add_chapters': True,
                'add_metadata': True,
            }],
        }


def input_and_output_format_matches(savedfile, file_format):
        # EXTENSION
        input_extension = Path(savedfile).suffix.replace('.','').lower()
        
        #SETS OF FORMATS
        mp4_set = {'mov', 'mp4', 'm4a', 'm4b', 'MOV', 'MP4', 'M4A', 'M4B'}
        mp3_set = {'mp3', 'MP3'}
        webm_set = {'webm', 'WEBM'}
        mkv_set = {'mkv', 'MKV'}
        
        if file_format in mp4_set and input_extension in mp4_set:
            return True
        elif file_format in mp3_set and input_extension in mp3_set:
            return True
        elif file_format in webm_set and input_extension in webm_set:
            return True
        elif file_format in mkv_set and input_extension in mkv_set:
            return True
        elif file_format.lower() == input_extension.lower():
            return True
        else:
            return False
            

def rename_audio_file_if_needed(file_path):
        original_file = Path(file_path)
        renamed_file = Path(file_path)
        
        mp4_set = {'.m4a', '.m4b', '.M4A', '.M4B'}
        
        if original_file.suffix in mp4_set:
            renamed_file = original_file.rename(original_file.with_suffix('.mp4'))
        
        return renamed_file
            

if __name__ == '__main__':
        print("GET YOUTUBE AUDIO FILE by Fmuaddib")
        print("Version: {}".format(VERSION))
        print("USAGE:")
        print("       SINGLE: get_youtube_audio_file.py <YOUTUBE URL>")
        print("       BATCH:  get_youtube_audio_file.py urls.txt")
        print()

        '''Parse arguments from command line'''
        parser = argparse.ArgumentParser(
            prog="get_youtube_audio_file.py",
            description='A Python CLI program for downloading audio files from Youtube videos.')
        parser.add_argument('input', type=str, help='URL of the Youtube video or playlist. Alternatively the path to a .txt file containing a list of URLS.')
        parser.add_argument('-k', '--keep_thumbs', default=False, help='Do not delete the thumb image files after embedding them in the audio files (default: False)', action="store_true")
        parser.add_argument('-c', '--continue_mode', default=False, help='If a "downloaded.txt" file is found, do not redownload the files recorded in it as already downloaded (default: False)', action="store_true")
        parser.add_argument('-f', '--format_conversion', default='original', help='Force conversion to specific container file format (original, mp3, m4a, caf, mp4video, mkvvideo) (default: original)', choices=["original", "mp3", "m4a", "caf", "mp4video", "mkvvideo"], metavar="original/mp3/m4a/caf/mp4video/mkvvideo")
        parser.add_argument('-m', '--try_remuxing', default=False, help='When converting to a different format try to use stream copy to remux audio leaving the original codec (avoiding re-encoding if possible) (default: False)', action="store_true")
        parser.add_argument('-b', '--bitrate', default=0, type=int, help='Preferred constant bitrate for audio files in kb/s (default: auto)')
        parser.add_argument('-v', '--vbr', default=False, help='Encode audio with variable bitrate (default: False)', action="store_true")
        parser.add_argument('-s', '--subtitles', default=False, help='Embed ALL subtitles available when downloading video (default: False)', action="store_true")
        args = parser.parse_args()

        # Read the arguments from the parser
        url = args.input
        keep_thumbs = args.keep_thumbs
        continue_mode = args.continue_mode
        format_conversion =  args.format_conversion.lower()
        bitrate = args.bitrate
        vbr_mode = args.vbr
        try_remuxing = args.try_remuxing
        embed_all_subtitles = args.subtitles
        

        if format_conversion == "mp4video":
            ydl_opts['format'] = "bv*[ext=mp4][height<=1080]+ba[ext=m4a]/b[ext=mp4][height<=1080] / bv*[height<=1080]+ba/b[height<=1080]"
            ydl_opts['merge_output_format'] = 'mp4'
            ydl_opts['writeautomaticsub'] = True
            if embed_all_subtitles:
                ydl_opts['allsubtitles'] = True
            else:
                ydl_opts['subtitleslangs'] = "en" #SUBTITLES_DEFAULT_REGEX_CODES
            ydl_opts['embedsubtitles'] = True
            ydl_opts['writesubtitles'] = True
            ydl_opts['forcethumbnail'] = False
            ydl_opts['extractaudio'] = False
            ydl_opts['final_ext'] = 'mp4'
            ydl_opts['writeinfojson'] = True
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegVideoRemuxer',
                'preferedformat': 'mp4',
            },{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            },{
                'key': 'FFmpegEmbedSubtitle',
                'already_have_subtitle': False,
            },{
                'key': 'FFmpegMetadata',
                'add_chapters': True,
                'add_metadata': True,
                'add_infojson': False,
            },{
                'key': 'EmbedThumbnail',
                'already_have_thumbnail': False,
            }]

        if format_conversion == "mkvvideo":
            ydl_opts['format'] = "bv*[ext=mkv]+ba[ext=mkv]/b[ext=mkv] / bv*+ba/b"
            ydl_opts['merge_output_format'] = 'mkv'
            ydl_opts['writeautomaticsub'] = True
            if embed_all_subtitles:
                ydl_opts['allsubtitles'] = True
            else:
                ydl_opts['subtitleslangs'] = "en" #SUBTITLES_DEFAULT_REGEX_CODES
            ydl_opts['embedsubtitles'] = True
            ydl_opts['writesubtitles'] = True
            ydl_opts['forcethumbnail'] = False
            ydl_opts['extractaudio'] = False
            ydl_opts['final_ext'] = 'mkv'
            ydl_opts['writeinfojson'] = True
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegVideoRemuxer',
                'preferedformat': 'mkv',
            },{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mkv',
            },{
                'key': 'FFmpegEmbedSubtitle',
                'already_have_subtitle': False,
            },{
                'key': 'FFmpegMetadata',
                'add_chapters': True,
                'add_metadata': True,
                'add_infojson': True,
            },{
                'key': 'EmbedThumbnail',
                'already_have_thumbnail': False,
            }]
            

        ## If previous log files exist, delete them ##
        if os.path.isfile(log_file_name):
                os.remove(log_file_name)
        if os.path.isfile(final_output_list_filename):
                os.remove(final_output_list_filename)
        if continue_mode is False:
                if os.path.isfile("downloaded.txt"):
                        os.remove("downloaded.txt")


        ## If the argument passed was a file containing a list of url,
        ## get them all.
        if str(url).endswith('.txt'):
                if os.path.isfile(Path(url)):
                    urls_list = get_list_of_urls_from_file(Path(url))
                    for yt_url in urls_list:
                            if yt_url and not yt_url.isspace():
                                    download_url(yt_url, ydl_opts)
                else:
                    print("ARGUMENT ERROR - file " + str(url) + " not found!" )

        else:
            # If the argument was an url, get it.
            try:
                InputURL(input_url=str(url))
            except ValidationError as e:
                print("ARGUMENT ERROR - Invalid URL: "+ str(url))
                print(e)
            else:
                download_url(url, ydl_opts)
                
                
        # OPTIONALLY CONVERT AND EMBED COVER ART
        for savedfile in completed_files:
            #print(str(completed_files))
            savedfile = remove_format_suffix(savedfile)
            if format_conversion == 'mp4video':
                savedfile = change_filename_extension(savedfile, 'mp4')
            if format_conversion == 'mkvvideo':
                savedfile = change_filename_extension(savedfile, 'mkv')
            if os.path.isfile(savedfile):
                savedfile = str(savedfile)
                if format_conversion == "original" or input_and_output_format_matches(savedfile, format_conversion):
                    savedfile = rename_audio_file_if_needed(savedfile)
                    if Path(savedfile).suffix in FORMATS_SUPPORTING_THUMB_EMBED:
                        embed_cover.embed_with_ffmpeg(savedfile, keep_thumbs)
                    else:
                        print("Cannot embed cover image in '" + str(savedfile) + "' Embedding is only supported for the following formats: mp3, mp4, m4a, m4b, mov, mkv")
                    final_files_list.add(savedfile)
                else:
                    if format_conversion == "mp4" or format_conversion == "m4a" or format_conversion == "m4b" or format_conversion == "mov":
                            savedfile = enc2mp3.convert_to_format(savedfile, 'mp4', vbr_mode, bitrate, try_remuxing)
                            print("EMBEDDING cover in file: " + savedfile)
                            embed_cover.embed_with_ffmpeg(savedfile, keep_thumbs)
                            savedfile = rename_audio_file_if_needed(savedfile)
                            final_files_list.add(savedfile)
                    elif format_conversion == "mp3":
                            savedfile = enc2mp3.convert_to_format(savedfile, 'mp3', vbr_mode, bitrate, try_remuxing)
                            print("EMBEDDING cover in file: " + savedfile)
                            embed_cover.embed_with_ffmpeg(savedfile, keep_thumbs)
                            savedfile = rename_audio_file_if_needed(savedfile)
                            final_files_list.add(savedfile)
                    elif format_conversion == "mp4video":
                            #  MP4 video format, no conversion needed
                            #embed_cover.embed_with_ffmpeg(savedfile, keep_thumbs)
                            #savedfile = rename_audio_file_if_needed(savedfile)
                            #savedfile = change_filename_extension(savedfile, 'mp4')
                            final_files_list.add(savedfile)
                    elif format_conversion == "mkvvideo":
                            #  MKV video format, no conversion needed
                            #embed_cover.embed_with_mkv(savedfile, keep_thumbs)
                            #savedfile = rename_audio_file_if_needed(savedfile)
                            #savedfile = change_filename_extension(savedfile, 'mkv')
                            final_files_list.add(savedfile)
                    else:
                            print("ERROR: conversion in '" + format_conversion + "' format not supported.")
                            final_files_list.add(savedfile)
            else:
                print("ERROR - file not found: " + str(savedfile))
                        
        for filename_record in final_files_list:
                print(f"FILE {str(filename_record)} successfully SAVED.")
                if Path(filename_record).suffix in OUTPUT_FILES_SUFFIXES:
                        write_filename_to_txt_final_output_log(filename_record)
                    


        print("\nSCRIPT ENDED.\n")




        