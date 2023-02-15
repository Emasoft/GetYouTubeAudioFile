#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
  EMBED COVER IN AUDIO FILES
  by Fmuaddib

FILENAME: embed_cover.py
VERSION: 1.2.2
AUTHOR: Fmuaddib
LICENSE: MIT
'''

import os
import sys
import argparse
from io import StringIO
from pathlib import Path
from mutagen.mp4 import MP4Tags, MP4, MP4Cover, AtomDataType, MP4FreeForm, MP4MetadataError
from mutagen.id3 import ID3, APIC
from mutagen import MutagenError

APP_NAME = "embed_cover.py"
APP_AUTHOR = "Fmuaddib"
VERSION = "1.2.2"

files_failed = set()
files_successully_processed = set()
        
def replace_extension(filename, ext, expected_real_ext=None):
    name, real_ext = os.path.splitext(filename)
    return '{0}.{1}'.format(name if not expected_real_ext or real_ext[1:] == expected_real_ext else filename, ext)

def get_mime_type(art_path):
    if art_path.lower().endswith('.png'):
        return 'image/png'
    elif art_path.lower().endswith('.jpg') or art_path.lower().endswith('.jpeg'):
        return 'image/jpeg'
    else:
        print('ERROR - image format not supported. Must be ".jpg" or ".png". Exiting.')
        sys.exit()
        
    return None
    

def get_cover_image_file_from_audio_filename(filename):
    thumbnail_jpg = replace_extension(filename, 'jpg')
    thumbnail_jpeg = replace_extension(filename, 'jpeg')
    thumbnail_png = replace_extension(filename, 'png')
    thumbnail_webp = replace_extension(filename, 'webp')
    
    if os.path.isfile(str(Path(thumbnail_jpg))):
        thumbnail_filename = thumbnail_jpg
    elif os.path.isfile(str(Path(thumbnail_jpeg))):
        thumbnail_filename = thumbnail_jpeg
    elif os.path.isfile(str(Path(thumbnail_png))):
        thumbnail_filename = thumbnail_png
    elif os.path.isfile(str(Path(thumbnail_webp))):
        os.system(f'ffmpeg -y -i "{thumbnail_webp}" -qmin 1 -q:v 1 -bsf:v mjpeg2jpeg "{thumbnail_jpg}"')
        thumbfile = Path(thumbnail_webp)
        thumbfile.unlink()
        thumbnail_filename = thumbnail_jpg
    else:
        print("ERROR - cover image not found. Exiting.")
        sys.exit()
    return thumbnail_filename


def embed_mp3_cover_with_mutagen(filename, keep_thumbs=False, cover_image=None):
    print("Adding thumbnail to " + filename)
    filename = str(filename)
    
    if cover_image is None:
        thumbnail_filename = get_cover_image_file_from_audio_filename(filename)
    else:
        cover_image = str(cover_image)
        if os.path.isfile(str(Path(cover_image))):
            thumbnail_filename = cover_image
        else:
            print("ERROR - cover image not found. Exiting.")
            sys.exit()

    thumb_mime_type = get_mime_type(thumbnail_filename)
        
    #EMBED COVER WITH MUTAGEN
    try:
        audio = ID3(filename)
        with open(str(Path(thumbnail_filename)), 'rb') as albumart:
            audio['APIC'] = APIC(
                      encoding=3,
                      thumb_mime=thumb_mime_type,
                      type=3, desc=u'Cover',
                      data=albumart.read()
                      )
        audio.save()
        if keep_thumbs is False:
            thumbfile = Path(thumbnail_filename)
            thumbfile.unlink()
        print("SUCCESSFULLY ADDED COVER TO MP3 FILE "+filename)
    except MutagenError as err:
        print("ERROR ADDING COVER TO：" + filename)
        print(err)
        sys.exit(1)
        
        
def embed_mp4_cover_with_mutagen(filename,keep_thumbs=False, cover_image=None):
    print("Adding thumbnail to " + filename)
    filename = str(filename)
    
    if cover_image is None:
        cover_image = str(cover_image)
        thumbnail_filename = get_cover_image_file_from_audio_filename(filename)
    else:
        if os.path.isfile(str(Path(cover_image))):
            thumbnail_filename = cover_image
        else:
            print("ERROR - cover image not found. Exiting.")
            sys.exit()

    if thumbnail_filename.lower().endswith('jpg') or thumbnail_filename.lower().endswith('jpeg'):
        thumb_format = MP4Cover.FORMAT_JPEG
    elif thumbnail_filename.lower().endswith('png'):
        thumb_format = MP4Cover.FORMAT_PNG
    else:
        print('ERROR - image format not supported. Must be ".jpg" or ".png". Exiting.')
        sys.exit()
    
    
    #EMBED COVER WITH MUTAGEN
    try:
        #mp4 = MP4(audio_file)
        #mp4.tags["covr"] = [MP4Cover(data=pic_data, imageformat=MP4Cover.FORMAT_JPEG)]
        #[bytes(albumart)]
        MP4file = MP4(filename)
        with open(thumbnail_filename, 'rb') as f:
            albumart = MP4Cover(data=f.read(), imageformat=thumb_format)
        if MP4file.tags is None:
            MP4file.add_tags()
        MP4file.tags['covr'] = [(albumart)]
        MP4file.save()
        if keep_thumbs is False:
            thumbfile = Path(thumbnail_filename)
            thumbfile.unlink()
        print("SUCCESSFULLY ADDED COVER TO MP4 FILE "+filename)
    except MutagenError as err:
        print("ERROR ADDING COVER TO：" + filename)
        print(err)
        sys.exit(1)


def embed_mp4_cover_with_ffmpeg(filename, keep_thumbs=False, cover_image=None):
    print("Adding thumbnail to " + filename)
    filename = str(filename)
    
    if cover_image is None:
        cover_image = str(cover_image)
        thumbnail_filename = get_cover_image_file_from_audio_filename(filename)
    else:
        if os.path.isfile(str(Path(cover_image))):
            thumbnail_filename = cover_image
        else:
            print("ERROR - cover image not found. Exiting.")
            sys.exit()

    if thumbnail_filename.lower().endswith('jpg') or thumbnail_filename.lower().endswith('jpeg'):
        cover_extension = "jpg"
    elif thumbnail_filename.lower().endswith('png'):
        cover_extension = "png"
    else:
        print('ERROR - image format not supported. Must be ".jpg" or ".png". Exiting.')
        sys.exit()
    
    ## FFMPEG INPUT / OUTPUT COMMANDS
    ## Original command line for mp4 cover embedding using ffmpeg:
    ## ffmpeg -y -vn -i "{audiofilename}" -i "{imagefilename}" -map 0:a -map 1:v -c:a copy -c:v:1 mjpeg -id3v2_version 3 -write_id3v1 1  -metadata:s:v "title=Album cover" -metadata:s:v "comment=Cover (front)"  -disposition:v:1 attached_pic "{audiofilename}_cover.{extension}"

    input_extension = Path(filename).suffix.replace('.','').lower()
    output_filename = replace_extension(filename, f'out.{input_extension}')
    output_file = Path(output_filename)
    input_filename = str(filename)
    input_file = Path(input_filename)
    input_file_cmd = '-i "' + str(input_file) +'"'
    input_thumb_file_cmd = '-i "' + str(thumbnail_filename) +'"'
    output_file_cmd = '"' + str(output_file) + '"'
    other_args_cmd = '-map 0:a -map 1:v -c:a copy -c:v:1 mjpeg -id3v2_version 3 -write_id3v1 1 -metadata:s:v "title=Album cover" -metadata:s:v "comment=Cover (front)" -disposition:v:1 attached_pic'

    #FFMPEG ARGS
    command_parts = [input_file_cmd, input_thumb_file_cmd, other_args_cmd, output_file_cmd]
    command_part_one = "ffmpeg -y"
    command_full = command_part_one + " "
    for part in command_parts:
        if part:
            command_full += part + " "
    print("INPUT FILE: " + filename)
    print("INPUT IMAGE FILE: "+thumbnail_filename)
    print("OUTPUT FILE: " + output_filename)
    print("----EXECUTING FFMPEG : " + command_full)
    os.system(command_full)


    if Path.is_file(output_file):
        input_f = Path(input_file)
        input_stem = input_f.stem
        new_input_name = f"{input_stem}_old{input_f.suffix}"
        renamed_input = input_f.rename(new_input_name)
        output_f = Path(output_file)
        new_output_name = f"{input_stem}{output_f.suffix}"
        renamed_output = output_f.rename(new_output_name)
        renamed_input.unlink()
        output_file = renamed_output
        print('Merged thumbnail to "%s"' % filename)
        if keep_thumbs is False:
            thumbfile = Path(thumbnail_filename)
            thumbfile.unlink()
        print("SUCCESSFULLY ADDED COVER TO MP4 FILE "+filename)
        files_successully_processed.add(str(output_file))
    else:
        print("Failed Embedding cover in "+str(input_file))
        files_failed.add(str(input_file))





def embed_mp3_cover_with_ffmpeg(filename, keep_thumbs=False, cover_image=None):
    print("Adding thumbnail to " + filename)
    filename = str(filename)
    
    if cover_image is None:
        thumbnail_filename = get_cover_image_file_from_audio_filename(filename)
    else:
        cover_image = str(cover_image)
        if os.path.isfile(str(Path(cover_image))):
            thumbnail_filename = cover_image
        else:
            print("ERROR - cover image not found. Exiting.")
            sys.exit()

    thumb_mime_type = get_mime_type(thumbnail_filename)
    
    ## FFMPEG INPUT / OUTPUT COMMANDS
    ## Original command line for mp4 cover embedding using ffmpeg:
    ## ffmpeg -y -i "coverfilename" -i "audiofilename" -c:a copy -c:v copy -map 0:v -map 1:a -id3v2_version 3 -write_id3v1 1 -map_metadata 0:g -map_metadata 1:g -metadata:s:v 'title="Album cover"' -metadata:s:v 'comment="Cover (front)"' -disposition:v:0 attached_pic "{audiofilename}_cover.{extension}"


    input_extension = Path(filename).suffix.replace('.','').lower()
    output_filename = replace_extension(filename, f'out.{input_extension}')
    output_file = Path(output_filename)
    input_filename = str(filename)
    input_file = Path(input_filename)
    input_file_cmd = '-i "' + str(input_file) +'"'
    input_thumb_file_cmd = '-i "' + str(thumbnail_filename) +'"'
    output_file_cmd = '"' + str(output_file) + '"'
    other_args_cmd = '-c:a copy -c:v copy -map 0:v -map 1:a -id3v2_version 3 -write_id3v1 1 -map_metadata 0:g -map_metadata 1:g -metadata:s:v \'title="Album cover"\' -metadata:s:v \'comment="Cover (front)"\' -disposition:v:0 attached_pic'

    #FFMPEG ARGS
    command_parts = [input_thumb_file_cmd, input_file_cmd, other_args_cmd, output_file_cmd]
    command_part_one = "ffmpeg -y"
    command_full = command_part_one + " "
    for part in command_parts:
        if part:
            command_full += part + " "
            
    print("INPUT FILE: " + filename)
    print("INPUT IMAGE FILE: "+thumbnail_filename)
    print("OUTPUT FILE: " + output_filename)
    print("----EXECUTING FFMPEG : " + command_full)
    os.system(command_full)

    if Path.is_file(output_file):
        input_f = Path(input_file)
        input_stem = input_f.stem
        new_input_name = f"{input_stem}_old{input_f.suffix}"
        renamed_input = input_f.rename(new_input_name)
        output_f = Path(output_file)
        new_output_name = f"{input_stem}{output_f.suffix}"
        renamed_output = output_f.rename(new_output_name)
        renamed_input.unlink()
        output_file = renamed_output
        print('Merged thumbnail to "%s"' % filename)
        if keep_thumbs is False:
            thumbfile = Path(thumbnail_filename)
            thumbfile.unlink()
        print("SUCCESSFULLY ADDED COVER TO MP3 FILE "+filename)
        files_successully_processed.add(str(output_file))
    else:
        print("Failed Embedding cover in "+str(input_file))
        files_failed.add(str(input_file))




#EXTERNAL - EMBED COVER IMAGE WITH FFMPEG
def embed_with_ffmpeg(audio_file, keep_thumbs=False, thumb_file=None):
    audio_file = str(audio_file)
    if audio_file.lower().endswith('mp3'):
        embed_mp3_cover_with_ffmpeg(audio_file,keep_thumbs, thumb_file)
    elif audio_file.lower().endswith('mp4') or audio_file.lower().endswith('m4a') or audio_file.lower().endswith('mov') or audio_file.lower().endswith('m4b'):
        embed_mp4_cover_with_ffmpeg(audio_file,keep_thumbs, thumb_file )
    else:
        print("ERROR: audio file format not supported. Must be mp3, mp4, m4a, m4b or mov. Exiting.")
        sys.exit(1)

#EXTERNAL - EMBED COVER IMAGE WITH MUTAGEN
def embed_with_mutagen(audio_file, keep_thumbs=False, thumb_file=None):
    audio_file = str(audio_file)
    if audio_file.lower().endswith('mp3'):
        embed_mp3_cover_with_mutagen(audio_file,keep_thumbs, thumb_file, )
    elif audio_file.lower().endswith('mp4') or audio_file.lower().endswith('m4a') or audio_file.lower().endswith('mov') or audio_file.lower().endswith('m4b'):
        embed_mp4_cover_with_mutagen(audio_file,keep_thumbs, thumb_file, )
    else:
        print("ERROR: audio file format not supported. Must be mp3, mp4, m4a, m4b or mov. Exiting.")
        sys.exit(1)


if __name__ == '__main__':
    print("EMBED COVERS by Fmuaddib")
    print("Version: {}".format(VERSION))
    print("USAGE:")
    print("       SINGLE: get_youtube_audio_file.py <YOUTUBE URL>")
    print("       BATCH:  get_youtube_audio_file.py urls.txt")
    print()
        
    '''Parse arguments from command line'''
    parser = argparse.ArgumentParser(
        prog="embed_cover.py",
        description='A Python CLI program for embedding covers into MP3 or MP4 (.m4a, .m4b, .mp4, .mov) audio files.')
    parser.add_argument('input', type=str, help='Input MP3 (.mp3) or MP4 (.m4a, .m4b, .mp4, .mov) audio file (can include folder path)')
    parser.add_argument('-c', '--cover_image', type=str, default=None, help='Path to .jpg or .png image file to embed as cover art (default: assuming same name as the audio file)')
    parser.add_argument('-e', '--encoder', type=str, default='ffmpeg', help='Encoder to use. Options are "ffmpeg" or "mutagen" (default: ffmpeg)')
    parser.add_argument('-o', '--output', type=str, default=None, help='Output folder (default: current folder, overwriting original file)')
    parser.add_argument('-k', '--keep_thumbs', default=False, help='Do not delete the thumb image files after embedding them in the audio files (default: False)', action="store_true")

    args = parser.parse_args()
    
    # Read the arguments from the parser
    audio_file = args.input
    thumb_file = args.cover_image
    encoder = args.encoder
    output_folder = args.output
    keep_thumbs = args.keep_thumbs

    if audio_file.lower().endswith('mp3'):
        if encoder == "ffmpeg":
            embed_mp3_cover_with_ffmpeg(audio_file,keep_thumbs, thumb_file )
        elif encoder == "mutagen":
            embed_mp3_cover_with_mutagen(audio_file,keep_thumbs, thumb_file)
    elif audio_file.lower().endswith('mp4') or audio_file.lower().endswith('m4a') or audio_file.lower().endswith('mov') or audio_file.lower().endswith('m4b'):
        if encoder == "ffmpeg":
            embed_mp4_cover_with_ffmpeg(audio_file,keep_thumbs, thumb_file )
        elif encoder == "mutagen":
            embed_mp4_cover_with_mutagen(audio_file,keep_thumbs, thumb_file )
    else:
        print("ERROR: audio file format not supported. Must be mp3, mp4, m4a, m4b or mov. Exiting.")
        sys.exit(1)

    print("SCRIPT ENDED.")

        
        
    