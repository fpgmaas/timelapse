from setuptools import setup, find_packages

setup(
    name='timelapse',
    version='1.0.0',
    url='https://github.com/fpgmaas/timelapse',
    author='Florian Maas',
    author_email='flo12392@gmail.com',
    description='Capture images on Raspberry Pi with webcam and create a timelapse',
    packages=find_packages(),    
    install_requires=['numpy','pillow'],
    python_requires="~=3.6"
)