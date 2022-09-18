#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
  GET YOUTUBE AUDIO FILE
	by Fmuaddib

FILENAME: get_youtube_audio_file.py
VERSION: 1.1.4
AUTHOR: Fmuaddib
LICENSE: MIT
'''


import os
import sys
import argparse
from io import StringIO
from pathlib import Path
import urllib
import urllib.request
from time import sleep
import youtube_dl



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
				youtube_dl.YoutubeDL(ydl_opts).download([url])



def my_hook(d):

		if d['status'] == 'finished':
				file_tuple = os.path.split(os.path.abspath(d['filename']))
				file_name = file_tuple[1]
				print("Done downloading {}".format(file_name))
				write_filename_to_txt_log(file_name)

		if d['status'] == 'downloading':
				file_tuple = os.path.split(os.path.abspath(d['filename']))
				file_name = file_tuple[1]
				#print("{} {} {}".format(d['filename'], d['_percent_str'], d['_eta_str']), end='\r')


def get_list_of_urls_from_file(file_name):
		with open(file_name, 'r') as fh:
				urls_list = [line for line in fh]
		return urls_list



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
			"verbose":True,
			"outtmpl":"%(title)s.%(ext)s",
			"source_address":"0.0.0.0",
			"sleep_interval":5,
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
			# The following are left with the DEFAULT value:
			"consoletitle": False,
			"forcedescription": False,
			"forcefilename": False,
			"forceformat": False,
			"forcethumbnail": False,
			"forcetitle": False,
			"forceurl": False,
			"listformats": None,
			"logtostderr": False,
			"matchtitle": None,
			"max_downloads": None,
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
			"allsubtitles": False,
			"listsubtitles": False,
			"socket_timeout": 20
		}




if __name__ == '__main__':
		# Read the URL from the command line
		url = sys.argv[1]


		## If previous log files exist, delete them ##
		if os.path.isfile(log_file_name):
				os.remove(log_file_name)
		if os.path.isfile("downloaded.txt"):
				os.remove("downloaded.txt")


		## If the argument passed was a file containing a list of url,
		## get them all.
		if url in "urls.txt":
				urls_list = get_list_of_urls_from_file(url)
				for yt_url in urls_list:
						if yt_url and not yt_url.isspace():
								download_url(yt_url, ydl_opts)
		else:
				# If the argument was an url, get it.
				download_url([url], ydl_opts)

		print("\nDone!\n")



