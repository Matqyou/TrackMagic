# TrackMagic: YouTube downloader for personal use
### Why do I need this thing
Idk maybe u want to download a few videos to keep them or smth
### How it work??
Open the `TrackMagic` file and follow the instructions by giving a video/playlist link and the application will start downloading from youtube.
The output folders are `./Video/` and `./Audio/`

## Setup this thing
### First of all, what do you need?
- You need a working `Python interpreter`
- And you need `ffmpeg`

To setup literally just open `TrackMagic` and it will setup itself.
### You need Python
If you're met with the message \
`'py' is not recognized as an internal or external command,` \
`operable program or batch file.` \
Install a [Python Interpreter](https://www.python.org/downloads/)
### If that doesn't work, then you might need be missing `pip` from the PATH
Maybe you're asking questions like... wtf is pip and why are you screaming PATH. \
Bro, just don't question it..
### How to pip if has no pip
1. Install python if not already installed. \
 1.1 If you don't have python and you're installing, then enable the option `Add to %PATH%` and you will get the pip.
2. Now if you already had python and pip is missing, head over to windows search and type `Edit the system enviroment variables`.
3. Click the first result that shows up and in the next window select `Enviroment Variables...`.
4. Another window should appear, now just click `Path` or `PATH` in the `User variables for X` section.
5. Select the option `Edit` and another window should appear.
6. Now select `New` and we will have to add the path to the directory that contains `pip.exe`. \
 6.1 Head over to `C:\Users\%USERNAME%\AppData\Local\Programs\Python`. \
 6.2 Find the python version that you just installed and enter the `Scripts` folder. \
 6.3 Copy the path to this directory, should look something like `C:\Users\%USERNAME%\AppData\Local\Programs\Python\PythonYOURVERSION\Scripts`
7. Now you should have pip added, you can exit all the windows by clicking `Ok`.
### If that doesn't work, then you might need be missing `ffmpeg` from the PATH
Basically download [ffmpeg for windows](https://www.gyan.dev/ffmpeg/builds/) and add it to path like in the pip tutorial above ^ ^ ^ \
It's recommended to download the `ffmpeg full` version(haven't tested the essentials version)
### If it still doesn't work, it's ggs
Well whatever it is you can try messaging the creator with the logs files (good luck)
