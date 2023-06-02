import smtplib
import ssl
import os
import schedule
import time
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

api_url = "https://api.open-meteo.com/v1/forecast?latitude=40.80&longitude=-96.67&daily=weathercode,temperature_2m_max,temperature_2m_min,sunrise,sunset,uv_index_max,precipitation_sum,precipitation_hours,precipitation_probability_max,windspeed_10m_max,winddirection_10m_dominant&temperature_unit=fahrenheit&windspeed_unit=mph&precipitation_unit=inch&forecast_days=1&timezone=America%2FChicago"


def processDailyData(data):

    # Daily Weather Data
    dailyData = {
        "date": data['daily']['time'][0],
        "tempHigh": data['daily']['temperature_2m_max'][0],
        "tempMin": data['daily']['temperature_2m_min'][0],
        "sunrise": data['daily']['sunrise'][0],
        "sunset": data['daily']['sunset'][0],
        "UVIndexMax": data['daily']['uv_index_max'][0],
        "precipitationSumMM": data['daily']['precipitation_sum'][0],
        "precipitationHours": data['daily']['precipitation_hours'][0],
        "windspeedMax": data['daily']['windspeed_10m_max'][0],
        "windspeedDirection": data['daily']['winddirection_10m_dominant'][0],
        "rainChanceMax": data['daily']['precipitation_probability_max'][0],
    }
    return dailyData


def send_weather_update(subject, destination):

    degree_sign = u'\N{DEGREE SIGN}'
    percent_sign = u'\N{PERCENT SIGN}'

    response = requests.get(api_url)
    weatherData = response.json()

    processedData = processDailyData(weatherData)

    today = processedData["date"]
    tempHigh = processedData["tempHigh"]
    tempLow = processedData["tempMin"]
    sunrise = processedData["sunrise"]
    sunset = processedData["sunset"]
    UVIndexMax = processedData["UVIndexMax"]
    precipSum = processedData["precipitationSumMM"]
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

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    # msg.attach(part1)
    msg.attach(part2)

    port = 465
    my_mail = os.getenv('BOT_EMAIL')
    my_password = os.getenv('BOT_PASSWORD')
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', port, context=context) as server:
        server.login(my_mail, my_password)
        server.sendmail(my_mail, destination, msg.as_string())


schedule.every().day.at("09:00", "US/Central").do(send_weather_update,
                                                  subject='Here is your morning weather update!', destination=os.getenv('DESTINATION_EMAIL'))

# For testing
# schedule.every(1).minutes.do(send_weather_update,
#                              subject='Here is your daily weather update!', destination=os.getenv('DESTINATION_EMAIL'))

while True:
    schedule.run_pending()
    time.sleep(60)
