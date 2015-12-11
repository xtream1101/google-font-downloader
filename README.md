# google-font-downloader

This was made so you can use google fonts locally and not have to rely on an internet connection. 

*This script still needs to catch invalid links and errors that may occur.

You must pass it a link from the google fonts api like this link here http://fonts.googleapis.com/css?family=PT+Sans:400,700,400italic,900%7CLato:300,400

It will zip all of the font files along with a css file that will automatically download once it has completed.

## Usage
This is created using a flask api. By default it is listening on all interfaces on port `7001`. To change this, edit the last line in `app.py` to reflect your new values.

Start by running: `$ python3 app.py`
