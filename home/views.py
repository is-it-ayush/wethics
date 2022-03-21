import os
from django.shortcuts import render 
from django.contrib.gis.geoip2 import GeoIP2
from ip2geotools.databases.noncommercial import DbIpCity
import ipinfo
import asyncio
from dotenv import load_dotenv

# Create your views here.
import requests

def home(request):
    """Renders the landing page of Wethics Application.
    
    Arguements:
        request: The Request object.
    """
    #Loading the .env file with environemnt variables.
    load_dotenv()

    # Getting the request data.
    data = ip_data(request)

    # Setting up the response.
    parameters = ["temperature","weatherCode"]
    unit = "metric"
    timestep = "current"

    # Getting the resposne of current data.
    response = getJSONdata(data,parameters,unit,timestep)

    # Getting the tempearature from response (Response is a JSON)
    temperature = int(response["data"]["timelines"][0]["intervals"][0]["values"]['temperature'])
    # Getting the time when the current data was Updated.
    last_updated = str(response["data"]["timelines"][0]["intervals"][0]['startTime'])
    # Getting the weather code and its respective text.
    weather_code = int(response["data"]["timelines"][0]["intervals"][0]["values"]['weatherCode'])
    weather_code_text = str(weathercode(weather_code))

    # Render the Index Page
    return render(request, 'index.html',{'location': data.city + ", " + data.country_name , 'temperature' : add_celsius_symbol(temperature), 'weather':  weather_code_text, 'bgurl': bgimg(), 'last_updated': format_time_from_ISO8601(last_updated)})
  


def forecast(request):
    """Renders the forecast page with weather forecast of upto 16 days.

    Arguement:
        reuqest: The Request Object.
    """
    #Loading the .env file with environemnt variables.
    load_dotenv()

    # Getting the request data.
    data = ip_data(request)

    # Getting the URL to fetch from API.
    url = 'https://api.weatherbit.io/v2.0/forecast/daily?city=' + data.city + "&key=15b6cc7dd80e4efbbd317566c35fa74a" + "&country=" + data.country + "&lang=en" + "&days=16"

    # Fetching and storing it in response as a JSON.
    response = requests.get(url).json()
    
    # Getting our forecast of next 16 Days.
    forecast = response['data']

    # Rendering our forecast page with the now available variables.
    return render(request,'forecast.html',{'bgurl': bgimg(), 'days': forecast, 'location': data.city + ", " + data.country_name})


def today(request):
    """Renders the today page with extra information about today.

    Arguement:
        reuqest: The Request Object.
    """

    #Loading the .env file with environemnt variables.
    load_dotenv()

    # Getting the request data.
    data = ip_data(request)
    
    # Setting up the response.
    parameters = ["temperature","temperatureApparent","humidity","precipitationProbability","windSpeed","windDirection","windGust","visibility","epaIndex","epaHealthConcern","weatherCode"]
    unit = "metric"
    timestep = "current"

    # Getting the resposne of current data.
    response = getJSONdata(data,parameters,unit,timestep)

    # Setting up our various required variables which will be passed later to page.
    temp_high = int(response["data"]["timelines"][0]["intervals"][0]["values"]['temperature']) # HighestTemperature.
    feels_like = int(response["data"]["timelines"][0]["intervals"][0]["values"]['temperatureApparent']) # The current felt temperature.
    precipitation = int(response["data"]["timelines"][0]["intervals"][0]["values"]['precipitationProbability']) # The Precipitation.
    humidity = int(response["data"]["timelines"][0]["intervals"][0]["values"]['humidity']) # The humidity of the day.
    wind_speed = int(response["data"]["timelines"][0]["intervals"][0]["values"]['windSpeed']) # The Wind Speed.
    gust_speed = int(response["data"]["timelines"][0]["intervals"][0]["values"]['windGust']) # The Gust Speed.
    wind_direction = str(response["data"]["timelines"][0]["intervals"][0]["values"]['windDirection'])+"°" # The Direction of Wind.
    vis = int(response["data"]["timelines"][0]["intervals"][0]["values"]['visibility']) # The Visibility of the day.    
    aqi = int(response["data"]["timelines"][0]["intervals"][0]["values"]['epaIndex']) # The AQI Data

    valid_date = datesplit(str(response["data"]["timelines"][0]["intervals"][0]['startTime'])) # The Splitted date array.
    date = valid_date[2] # The Date
    month = valid_date[1] # The Month
    year =  valid_date[0] # The Year

    # Rendering the page with the now available data.
    return render(request, 'today.html',{
        'bgurl': bgimg(),
        'location': data.city + ", " + data.country_name, 
        'th': add_celsius_symbol(temp_high),
        'fl': add_celsius_symbol(feels_like),
        'vis': vis,
        'ws': wind_speed,
        'gs': gust_speed,
        'wdi': wind_direction,
        'hum': humidity,
        'pre': precipitation,
        'date': date,
        'month': month,
        'year': year,
        'day': valid_date,
        'aqi': aqi,
        'aqi_text': aqi_helper_function(aqi)[0],
        'aqi_text_color': aqi_helper_function(aqi)[1],
    })


# Helper Functions

def aqi_helper_function(aqi):
    """Returns the AQI Warning Level from aqi data & its respective color.
    
    Arguement:
        aqi: The AQI Data Object.
    """
    # The AQI Warning Level
    warning_level = ['Good', 'Moderate','Unhealthy For Sensitive Groups','Unhealty','Very Unhealthy','Hazardous']
    
    # The Color that goes with the warning level.
    color = ['#009966', '#ffde33','#ff9933','#cc0033','#660099','#7e0023']

    # Bad Code Writing (Issue Aware)
    if aqi>=0 and aqi<=50:
        return warning_level[0],color[0]
    if aqi>=51 and aqi<=100:
        return warning_level[1],color[1]
    if aqi>=101 and aqi<=150:
        return warning_level[2],color[2]
    if aqi>=151 and aqi<=200:
        return warning_level[3],color[3]
    if aqi>=201 and aqi<=300:
        return warning_level[4],color[4]
    if aqi>300:
        return warning_level[5],color[5]


def datesplit(date):
    """Returns the Date from ISO8601 Format
    
    Arguement:
        date: Date in ISO8601 Format
    """
    f = date.split("T")
    f = f[0]
    f = f.split("-")
    return f

def add_celsius_symbol(temp):
    """Adds the °C symbol and returns in String
    
    Arguement:
        temp: Temperature.
    """
    return str(temp)+" °C"

def bgimg():
    """Returns the Background URL from BING."""

    # The URL To Retrieve from.
    bgurl = 'https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1'
    
    # Getting the JSON.
    bg = requests.get(bgurl).json()
    
    # Getting the Image URL from JSON.
    bgurl = 'https://bing.com'+bg['images'][0]['url']
    
    # Returning the Image URL
    return bgurl

def format_time_from_ISO8601(lst_updt):
    """Returns the Date from ISO8601 Format
    
    Arguement:
        lst_updt: The Last Updaed Time.
    """
    # Slicing the format.
    f = lst_updt.split("T")
    f = f[1]
    f = f[:len(f)-4]
    f = f.split(":")
    
    # Converting from 24 hours to 12 Hour's.
    if int(f[0]) >= 12:
        fTime = str(int(f[0])-12)+":"+f[1]+ " pm"
    elif int(f[0]) < 12:
        fTime = f[0]+":"+f[1] + " am"
    
    # Returing the time.
    return fTime


def get_client_ip(request):
    """Returns the Client IP from Request Header.
    
    Arguement:
        request: The Request Object.
    """
    # Gett the HTTP_X_FORWARDED_FOR request Header.
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    # Return IP
    return ip

def weathercode(wcode):
    """Returns the Weather from Weather Code.
    
    Arguement:
        wcode: The Weather Code.
    """
    # The Code List with their Respective Weathers.
    code = {
        0: "Unknown",
        1000: "Clear",
        1001: "Cloudy",
        1100: "Mostly Clear",
        1101: "Partly Cloudy",
        1102: "Mostly Cloudy",
        2000: "Fog",
        2100: "Light Fog",
        3000: "Light Wind",
        3001: "Wind",
        3002: "Strong Wind",
        4000: "Drizzle",
        4001: "Rain",
        4200: "Light Rain",
        4201: "Heavy Rain",
        5000: "Snow",
        5001: "Flurries",
        5100: "Light Snow",
        5101: "Heavy Snow",
        6000: "Freezing Drizzle",
        6001: "Freezing Rain",
        6200: "Light Freezing Rain",
        6201: "Heavy Freezing Rain",
        7000: "Ice Pellets",
        7101: "Heavy Ice Pellets",
        7102: "Light Ice Pellets",
        8000: "Thunderstorm",
    }
    
    # Return if exists, else return Not Known.
    return code.get(wcode, "Not Known")



def render_error(request,code):
    """Renders the Error Page with the specified request and code.
    
    Arguement
        request: The request object.
        code: The Error Code
    """
    return render(request,'404.html',{'bgurl': bgimg(),"error_code": code})

# Helper Function
def getJSONdata(data,parameters,unit,timestep):
    """Returns the Weather Data from the following arguements.
    
    Arguements:
        location: Location Array. Where [0] is latitude, and [1] is longitude.
        p: Requested Parameters
        u: The Unit in which the data will be returned
    """
    # The Base URL for the Tommorow API Request.
    baseURL = "https://api.tomorrow.io/v4/timelines?"
    
    # Getting the API Key
    apikey = os.environ.get("TOMMOROW_API")

    # Setting up a unit variable.
    units = str(unit)
    
    # Setting up the timesteps
    timesteps = str(timestep)

    # Formatting feilds to be used in the RequestURL from the requested parameters array.
    fstring = ""
    for i in parameters:
        fstring+= str(i)+","

    # Finalizing the Request URL
    # Format:
    # finalurl = base + location + fields + timesteps + units + apiKey 
    finalUrl = baseURL + "location=" + data.latitude + "," + data.longitude + "&" + "fields=" + fstring + "&timesteps=" + timesteps + "&units=" + units + "&apikey=" + apikey

    # Getting the response.
    response = requests.get(finalUrl).json()

    # Returns the response.
    return response

def ip_data(request):
    """Returns the information from a specific ip extracted from request header.
    
    Arguement:
        reuqest: The Request Object.
    """
    # Getting the API Key.
    access_token = os.environ.get("IPINFO_KEY")

    # Setting up the handler.
    handler = ipinfo.getHandler(access_token)
    
    # Getting the Data from IPInfo
    data = handler.getDetails()
    print(data)
    return data