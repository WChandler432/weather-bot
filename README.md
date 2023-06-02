# weather-bot
An email bot that sends me daily forecasts and up to date weather alerts using python and the Open Meteo API.
This bot is currently hosted on a PythonAnywhere console and sends approximately 1 update per day to my personal email at 9:00AM US Central.
It gives the day's forecast and contains temperature, precipitation, wind, and sunrise / sunset data. 

## Set up notes
If you want to clone and use this script for yourself, you'll need to create an ENV file in the src directory that has:
- the gmail address you want the bot to send from
- the app password generated for the gmail account
- the destination email
