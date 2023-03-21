![Music Grabber](https://i.ibb.co/VBgX7bk/Music-Grabber-Shortcut.png)

**MUSIC GRABBER** is a shortcut to download music files from YouTube and optionally convert them to MP3 or M4A.  
  
How to use it  
===========
Make sure to have installed all requirements. Then:   
  
  - Use the share menu from a Youtube page to send the url of the **video** (or the url of a public **playlist**) to the shortcut.  
  - Alternatively, if you run Music Grabber alone, without sharing a link, an input box will appear and you will be given the option to manually type (or paste from the clipboard) a list of **Youtube links** (or **Shazam links**) for **batch downloading** them. Each link must be on a new line. Lines beginning with # will be ignored (so you can comment out links or add comments). **WARNING**: When using **batch downloading** mode, remember to set **DISPLAY AUTOLOCK on 'Never'** on your iOS device, otherwise the shortcut will be interrupted before finishing the task.  
  - You will be asked to select a folder where to save the audio files.  
  - The shortcut will open the a-Shell Mini app and will start downloading the songs. Don't touch anything and wait.  
  - Since the shortcut is configured to download the **'best quality' version** of an audio track, and that is usually .webm or .ogg, **you can choose to convert the files to MP3 or M4A**. The log messages can be verbose sometimes, just ignore them. You will also need to select the conversion quality. You can choose among 3 options: **remux original (when possible), optimize for quality** and **optimize for file size**.  
  - Once it has completed the downloads (and the optional conversions), the audio files will be saved in a subfolder of the folder you selected previously. The name of the subfolder is: *"Music Grabber Output (current date)"*.  
  - Since there are temporary files created and deleted, iOS will bug you with some confirmation dialogs. Especially at the end. Just confirm them.  
  - Thumbnails and cover images will be downloaded from YouTube and embedded in the audio files. Files with the extensions '.m4a' and '.m4b' will be renamed with the extension '.mp4', because iOS apparently only parses thumbs for the latters.  
  - **(NEW!!!)** You can now choose to download the entire **VIDEO** (without extracting the audio). You can choose between saving it in MP4 format (resolution up tp 1080p) or MKV format (resolution up to 8K). You can also choose to embed ALL the available **SUBTITLES** in both video formats. **WARNING:** downloading the subtitles is going to take A VERY LONG TIME because a 15 seconds pause is needed between each subtitle file to avoid your IP from being banned! Be sure to keep your device connected to a power source.  
  - DONE! :D  
  
Enjoy the songs in your favourite audio player. My favourite on iOS is [**Flacbox**](https://itunes.apple.com/us/app/flacbox-flac-player-music/)  
  

KNOWN ISSUES
============
Some m4a files downloaded from Youtube have a DASH header (with an empty seek table) instead of a standard mp4 header. The DASH format is not supported by many audio players, so this usually causes the m4a file to have wrong duration and to sound silent for half of the time. This has been solved in Music Grabber version 1.1.1 or greater. But if you have already downloaded m4a files with this issue in the past, you can use my small shortcut  [**Fixup DASH m4a headers**](https://routinehub.co/shortcut/12614/) to easily fix them.  
  

REQUIREMENTS  
=============
 - You need the [a-Shell Mini](https://apps.apple.com/ao/app/a-shell-mini/\id1543537943) app installed.  
 - If you want to enable the **support for Shazam links**, you should install my other shortcut [**Shazam Link Converter**](https://routinehub.co/shortcut/12313/).  
  

  
ACKNOWLEDGEMENTS  
===================
This shortcut was inspired by [Music Downloader](https://routinehub.co/shortcut/6400/) (author: @creepyeyesOO).  

  
INFO  
====
 - First Release 2022-07-17 v1.0.0  
 - Latest Release 2023-03-20 v1.5.2  
 - Author: [u/fremenmuaddib](https://www.reddit.com/user/fremenmuaddib/)  
 - This shortcut is canonically available on RoutineHub at https://routinehub.co/shortcut/12578/  
 
 