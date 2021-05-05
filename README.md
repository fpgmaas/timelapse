# timelapse

This is a repository that contains code that converts your RaspBerry Pi and a webcam into a tool to create a timelapse.

![til](example.gif)

## Instructions

Make sure [poetry](https://python-poetry.org/docs/) and Python 3.7 are installed. Install the environment with `poetry install` and then run the file `main.py`:

```bash
screen -S timelapse
python main.py
```

Now the Raspberry Pi will capture an image with the webcam every minute and place it in the images directory. Now, either copy the files from RaspberryPi to your local machine over SSH, or skip this step and run the next step directly on your Raspberry Pi.

```
scp USER@IP:home/USER/timelapse/images/\* /home/USER_LOCAL/timelapse/images/
```

Run `python convert.py` to laod the images and convert them into a timelapse.
