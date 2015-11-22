raspi-mpd-lcd
=============

A class based Python project to control a 20x04 (or 16x02) LCD via I2C. Here the framework is used to display time and mpd information, but most of the code can be reused to display any text that can be categorized into separate lines

This project requires

* Python 3
* python-mpd2 (https://github.com/Mic92/python-mpd2)
* python3-smbus (can be installed with apt-get)
