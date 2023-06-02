# weather-bot
An email bot that sends me daily forecasts and up to date weather alerts using python and the [Open Meteo API](https://open-meteo.com/).
This bot is currently hosted on a PythonAnywhere console and sends approximately 2 updates per day to my personal email at 9:00AM US Central and 23:00 US Central. The second update is an 'accuracy' calculation.
It gives the day's forecast and contains temperature, precipitation, wind, and sunrise / sunset data. 

## Set up notes
If you want to clone and use this script for yourself, you'll need to create an ENV file in the src directory that has:
- the gmail address you want the bot to send from
- the app password generated for the gmail account
- the destination email

## The accuracy calculation
I had become mildly interested in seeing how the forecast I get from the API would fare each day, so I added in a second API call at the end of the day that collects
that whole day's weather data (for the fields already mentioned above) by the hour. I then aggregate the hourly data by subject and make my own judgements on it. I do not 
claim to be making any real statistical inferences from the judgements or the resulting 'accuracy' value, as this is purely for my own entertainment, but maybe in the 
future that will be subject to change. 
