# GetYouTubeAudioFile  
"Get Youtube Audio File" is a Python script to download music files from YouTube using yt-dlp.  
  
It is set to download the maximum quality audio file available (usually webm or m4a), but you can choose to convert the file to some other format (i.e. mp4/m4a, mp3).  
The cover image will be automatically embedded as thumbnail.
  
I have included an handy [Siri Shortcut](https://github.com/Emasoft/GetYouTubeAudioFile/tree/main/siri%20shortcut) to use the script even on iOS/iPad OS.  

# Requirements
You need ffmpeg installed.
You also need some python libraries.
To install them, run the following commands before executing the python scripts:

    python -m pip -v install --upgrade pip
    pip -v install -U yt-dlp
    pip -v install -U pydantic
    pip -v install -U mutagen
    
 







