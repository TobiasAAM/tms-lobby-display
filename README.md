## TMS Lobby Display

Above the ticket sales booth is normally a few tv screens with upcoming film times, these are usually supplied by the point of sale (POS, i.e. the ticket sales system). 
In theory we have a lot of the data required to make a screen for this in the TMS itself so that is the project which does it!

### Installation

Python 2.6.x is required, pip is useful or look in the requirements.txt to grab the dependencies.

`pip install -r requirements.txt`

### Next Steps
Take a copy of `settings-template.json`, name it `settings.json` and change the settings to your needs.

To start the app, run:
`python tms_lobby_display.py`