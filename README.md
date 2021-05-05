# timelapse

This is a repository that contains code that converts your RaspBerry Pi and a webcam into a tool to create a timelapse.

![til](example.gif)

## Instructions
## Jupyter Notebook on Raspberry Pi:

Make sure [poetry](https://python-poetry.org/docs/) and Python 3.7 are installed. Install the environment with `poetry install` and then start a jupyter notebook session on your Raspberry Pi:

```
screen -s jupyter
conda activate timelapse
jupyter notebook --no-browser --port=PORT
```

Where PORT is an arbitrary port on your Raspberry Pi. You can access the notebook session on your local machine with the command
```
ssh -L PORT:localhost:PORT USER@IP
```
Where IP and USER are the ip-address and the user of your Raspberry Pi respectively.

Run the cells in the notebook `main-capture.ipynb`, and the Raspberry Pi will capture an image with the webcam every minute and place it in the images directory. To copy files from RaspberryPi to your local machine over SSH:

```
scp USER@IP:home/USER/timelapse/images/\* /home/USER_LOCAL/timelapse/images/
```

Then, run the notebook `notebooks/main-convert.ipynb` to convert the images into a timelapse.
