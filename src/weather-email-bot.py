import smtplib
import ssl
import os
import schedule
import time
import requests
import numpy as np
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

api_url_daily = "https://api.open-meteo.com/v1/forecast?latitude=40.80&longitude=-96.67&daily=weathercode,temperature_2m_max,temperature_2m_min,sunrise,sunset,uv_index_max,precipitation_sum,precipitation_hours,precipitation_probability_max,windspeed_10m_max,winddirection_10m_dominant&temperature_unit=fahrenheit&windspeed_unit=mph&precipitation_unit=inch&forecast_days=1&timezone=America%2FChicago"
api_url_end_of_day = "https://api.open-meteo.com/v1/forecast?latitude=40.80&longitude=-96.67&hourly=temperature_2m,precipitation,weathercode,windspeed_10m,winddirection_10m,uv_index&temperature_unit=fahrenheit&windspeed_unit=mph&precipitation_unit=inch&forecast_days=1&timezone=America%2FChicago"

def process_data(data, endOfDay):

    if(endOfDay == False):
        # Daily Weather Data
        daily_data = {
            "date": data['daily']['time'][0],
            "tempHigh": data['daily']['temperature_2m_max'][0],
            "tempMin": data['daily']['temperature_2m_min'][0],
            "sunrise": data['daily']['sunrise'][0],
            "sunset": data['daily']['sunset'][0],
            "UVIndexMax": data['daily']['uv_index_max'][0],
            "precipitationSum": data['daily']['precipitation_sum'][0],
            "precipitationHours": data['daily']['precipitation_hours'][0],
            "windspeedMax": data['daily']['windspeed_10m_max'][0],
            "windspeedDirection": data['daily']['winddirection_10m_dominant'][0],
            "rainChanceMax": data['daily']['precipitation_probability_max'][0],
        }
        return daily_data
    elif(endOfDay == True):
        # End of Day Weather Data
        end_of_day_data = {
            "tempData": data['hourly']['temperature_2m'],
            "UVIndexData": data['hourly']['uv_index'],
            "precipData": data['hourly']['precipitation'],
            "windspeedData": data['hourly']['windspeed_10m'],
            "windspeedDirectionData": data['hourly']['winddirection_10m'],
        }
        return end_of_day_data

def end_of_day_data_update_and_accuracy(destination):
    accuracy_total = 100
    response = requests.get(api_url_end_of_day)
    endOfDayData = response.json()
    processedData = process_data(endOfDayData, True)
    culprits = []
    if(np.max(processedData["tempData"]) > running_daily_forecast["tempHigh"]):
        accuracy_total -= 12.5
        culprits.append("The temp today reached above the high")
    if(np.min(processedData["tempData"]) < running_daily_forecast["tempMin"]):
        accuracy_total -= 12.5
        culprits.append("The temp today went below the low")    
    if(np.max(processedData["UVIndexData"]) > running_daily_forecast["UVIndexMax"]):
        accuracy_total -= 12.5
        culprits.append("The UV Index got too high")    
    if(sum(processedData["precipData"]) < running_daily_forecast["precipitationSum"]):
        accuracy_total -= 12.5
        culprits.append("There was not as much precipitation today as anticipated")    
    if(np.max(processedData["windspeedData"]) > running_daily_forecast["windspeedMax"]):
        accuracy_total -= 12.5
        culprits.append("The windspeed today was higher than the forecasted max")    
    if((running_daily_forecast["windspeedDirection"] - 10) <= np.mean(processedData["windspeedDirectionData"]) <= (running_daily_forecast["windspeedDirection"] + 10)):
        accuracy_total -= 12.5
        culprits.append("The windspeed direction was not close to the forecasted one")
        
    # Email specific vars
    today = running_daily_forecast["date"]
        
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'End of Day Weather Accuracy Report'

    # TODO: Plain text version of email
    # text = "Hi!\nThis is your daily weather report!\nData:\nEXAMPLE DATA HERE"
    html = """\
    <html>
    <head></head>
    <body>
        <p>Hi!<br>
        This is your end of day weather accuracy report for {today}!<br>
        The overall accuracy of today's forecast was: {accuracy_total}<br>
        The culprits are: {culprits}
        </p>
    </body>
    </html>
    """.format(**locals())

    # part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    msg.attach(part2)

    port = 465
    my_mail = os.getenv('BOT_EMAIL')
    my_password = os.getenv('BOT_PASSWORD')
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', port, context=context) as server:
        server.login(my_mail, my_password)
        server.sendmail(my_mail, destination, msg.as_string())
        

def send_weather_update(subject, destination):

    degree_sign = u'\N{DEGREE SIGN}'
    percent_sign = u'\N{PERCENT SIGN}'

    response = requests.get(api_url_daily)
    weatherData = response.json()

    processedData = process_data(weatherData, False)
    global running_daily_forecast
    running_daily_forecast = processedData

    today = processedData["date"]
    tempHigh = processedData["tempHigh"]
    tempLow = processedData["tempMin"]
    sunrise = processedData["sunrise"]
    sunset = processedData["sunset"]
    UVIndexMax = processedData["UVIndexMax"]
    precipSum = processedData["precipitationSum"]
    precipHours = processedData["precipitationHours"]
    windspeedMax = processedData["windspeedMax"]
    windspeedDirection = processedData["windspeedDirection"]
    rainChanceMax = processedData["rainChanceMax"]

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject

    # TODO: Plain text version of email
    # text = "Hi!\nThis is your daily weather report!\nData:\nEXAMPLE DATA HERE"
    html = """\
    <html>
    <head></head>
    <body>
        <p>Hi!<br>
        This is your daily weather report for {today}!<br>
        Temperature High: {tempHigh}{degree_sign}F<br>
        Temperature Low: {tempLow}{degree_sign}F<br>
        Sunrise Time: {sunrise}<br>
        Sunset Time: {sunset}<br>
        UV Index Max: {UVIndexMax}<br>
        Chance of Rain Today: {rainChanceMax}{percent_sign}<br>
        Sum of Precipitation: {precipSum}in<br>
        Hours of Precipitation Today: {precipHours}<br>
        Maximum Windspeed: {windspeedMax}mph<br>
        Dominant Wind Direction: {rainChanceMax}{degree_sign}<br>
        </p>
    </body>
    </html>
    """.format(**locals())

    # part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    # msg.attach(part1)
    msg.attach(part2)

    port = 465
    my_mail = os.getenv('BOT_EMAIL')
    my_password = os.getenv('BOT_PASSWORD')
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', port, context=context) as server:
        server.login(my_mail, my_password)
        server.sendmail(my_mail, destination, msg.as_string())
        

schedule.every().day.at("09:10", "US/Central").do(send_weather_update,
                                                  subject='Here is your morning weather update!', destination=os.getenv('DESTINATION_EMAIL'))

schedule.every().day.at("23:00", "US/Central").do(end_of_day_data_update_and_accuracy, destination=os.getenv('DESTINATION_EMAIL'))

# For testing
# schedule.every(1).minutes.do(send_weather_update,
#                              subject='Here is your daily weather update!', destination=os.getenv('DESTINATION_EMAIL'))

# send_weather_update('test', os.getenv('DESTINATION_EMAIL'))
# end_of_day_data_update_and_accuracy(os.getenv('DESTINATION_EMAIL'))

while True:
    schedule.run_pending()
    time.sleep(60)
