# Vamos

## Installation Guide

### Backend Setup

#### First Time Setup

1. Install Python 3.10.
    If on Mac, it is recommended this is done via (`Homebrew`)[https://brew.sh/].
    Install Homebrew, add it to your `PATH` as it directs you, then run `brew install python@3.10`.
2. Create a (virtual environment)[https://realpython.com/python-virtual-environments-a-primer/] with `python3.10 -m venv venv` in the `backend` directory.
   Make sure you do this in `python3.10`.
3. Activate the virtual environment via `source venv/bin/activate` on Mac/Linux or `venv\Scripts\activate` on Windows.
   If this worked correctly, you should see `(venv)` pop up on the left of your terminal prompt.
4. Run `pip install -r requirements.txt` to install needed packages. This will take a while.
   Note if you have an Nvidia GPU with CUDA, you can instead install `requirements_cuda.txt`.
<!-- 5. After you're done, deactivate the virtual environment with `deactivate`. -->

After the first time, on you only need to do step 3.

#### Running the Server

Use `python server.py` in the backend directory to run the server.
When you do this, make sure the virtual environment is active (run `which python` to confirm you are running the virtual environment's installation of python.)

### Frontend Setup

#### First Time Setup

1. Install `npm`, the (Node Package Manager)[https://www.npmjs.com/].
   Again, if on Mac, the recommended way to do this is via `brew install node`.
2. Run `npm install` in the `frontend` directory.
   This will install the required Javascript packages.

Run `npm run dev` in the `frontend` directory from then on to start the webserver.

## Putting Them Together

Now open multiple tabs in your terminal, with one running the backend and another running the frontend.
When you run `npm run dev`, vite should output a message like
```
❯ npm run dev

> frontend@0.0.1 dev
> vite dev


  VITE v6.0.7  ready in 1525 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```
If you visit `http://localhost:5173/` in your browser, you should be able to see the frontend.
Then click the upload button, upload a test `mp3` file (there are some in the `data` directory), and hit submit.
In the terminal running the backend, you should see a POST request with code 200 (indicating a success) like this:
```
127.0.0.1 - - [21/Jan/2025 00:39:22] "POST /upload HTTP/1.1" 200 -
```
and the frontend terminal should log `File uploaded successfully!`.
You should then be able to see the file copied to the `backend/uploads` directory.

## Downloading Test Data

You can use (`yt-dlp`)[https://github.com/yt-dlp/yt-dlp?tab=readme-ov-file#installation] to download Youtube videos as test `mp3` files.

Example command:
`yt-dlp --extract-audio --audio-format mp3 '{youtube_url}'`
