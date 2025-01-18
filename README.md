# Vamos

## Installation Guide

### Backend Setup

#### First Time Setup

Note: you must have an Nvidia GPU to install the Whisper model.

1. Install Python at least 3.8 but at most 3.11 (this has only been tested on Python3.10, however).
2. Create a virtual environment with `python3 -m venv venv` in the `backend` directory
3. Activate the virtual environment via `source venv/bin/activate` on Mac/Linux or `venv\Scripts\activate` on Windows.
4. Run `pip install -r requirements.txt` to install needed packages. This will take a while.
5. After you're done, deactivate the virtual environment with `deactivate`.

After the first time, on you only need to do step 3 and 5.

#### Running the Server

Use `python server.py` to run the server.

### Frontend Setup

#### First Time Setup

1. Install npm 10
2. Run `npm install` in the `frontend` directory

Run `npm run dev` from then on to start the webserver.

## Downloading Test Data

You can use `yt-dlp` to download Youtube videos.
https://github.com/yt-dlp/yt-dlp?tab=readme-ov-file#installation

Example command:
`yt-dlp --extract-audio --audio-format mp3 '{youtube_url}'`
