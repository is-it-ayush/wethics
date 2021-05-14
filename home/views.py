import json
from re import template
from typing import List
from django.http import response
from django.http.response import HttpResponse, HttpResponseGone
from django.shortcuts import render 
from django.contrib.gis.geoip2 import GeoIP2
from ip2geotools.databases.noncommercial import DbIpCity

# Create your views here.
import requests

def ren404(request):
    return render(request,'404.html',{'bgurl': bgimg()})

# Helper Function
def getJSONdata(l,p,u,t):
    baseURL = "https://api.tomorrow.io/v4/timelines?"
    apikey = "Tyr1EgrDSiHzz5c6MHjz5qGBlkQ8zzoq"
    location = [l[0],l[1]]
    units = str(u)
    timesteps = str(t)
    #Temporary String Initialization
    fstring = ""
    for i in p:
        fstring+= str(i)+","
    finalUrl=baseURL+"location="+str(location[0])+","+str(location[1])+"&"+"fields="+fstring+"&timesteps="+timesteps+"&units="+units+"&apikey="+apikey
    response = requests.get(finalUrl).json()
    return response


def home(request):
    g = GeoIP2()
    ip  = get_client_ip(request)
    udata = DbIpCity.get(ip, api_key='free')

    
    response = getJSONdata([str(udata.latitude),str(udata.longitude)],["temperature","weatherCode"],"metric","current")

    #temperature variable
    temp = int(response["data"]["timelines"][0]["intervals"][0]["values"]['temperature'])
    #last updated temperature varible
    lst_updt = str(response["data"]["timelines"][0]["intervals"][0]['startTime'])
    #WeatherCodeToText
    wcode = int(response["data"]["timelines"][0]["intervals"][0]["values"]['weatherCode'])
    wText = str(weathercode(wcode))

    #DEPLOYMENT EDIT IMPORTANT ----- Change "lucknow" to city and "India" to country
    return render(request, 'index.html',{'location': udata.city + ", " + udata.country, 'temperature' : temp_convert_to_c(temp), 'weather':  wText, 'bgurl': bgimg(), 'last_updated': lastupdated(lst_updt)})
    #------------------------------------------------------------------------------------------------------



def forecast(request):
    g = GeoIP2()
    ip  = get_client_ip(request)
    udata = DbIpCity.get(ip, api_key='free')


    url = 'https://api.weatherbit.io/v2.0/forecast/daily?city=' + udata.city + "&key=15b6cc7dd80e4efbbd317566c35fa74a" + "&country=" + udata.country + "&lang=en" + "&days=16"
    #------------------------------------------------------------------------------------------------------



    #Response Object
    response = requests.get(url).json()
    #Date Part Monday 23
    forecast = response['data']

    #DEPLOYMENT EDIT IMPORTANT ----- Change "lucknow" to city and "India" to country
    return render(request,'forecast.html',{'bgurl': bgimg(),'days': forecast, 'location': udata.city + ", " + udata.country})
    #------------------------------------------------------------------------------------------------------


def today(request):
    g = GeoIP2()
    ip  = get_client_ip(request)
    udata = DbIpCity.get(ip, api_key='free')
    response = getJSONdata([str(udata.latitude),str(udata.longitude)],["temperature","temperatureApparent","humidity","precipitationProbability","windSpeed","windDirection","windGust","visibility","epaIndex","epaHealthConcern","weatherCode"],"metric","current")

    #Temperature
    temp_high = int(response["data"]["timelines"][0]["intervals"][0]["values"]['temperature'])
    feels_like = int(response["data"]["timelines"][0]["intervals"][0]["values"]['temperatureApparent'])
    
    #Humidity and precipitation
    precipitation = int(response["data"]["timelines"][0]["intervals"][0]["values"]['precipitationProbability'])
    humidity = int(response["data"]["timelines"][0]["intervals"][0]["values"]['humidity'])

    #Wind Date
    wind_speed = int(response["data"]["timelines"][0]["intervals"][0]["values"]['windSpeed'])
    gust_speed = int(response["data"]["timelines"][0]["intervals"][0]["values"]['windGust'])
    wind_direction = str(response["data"]["timelines"][0]["intervals"][0]["values"]['windDirection'])+"°"


    #Visibility 
    vis = int(response["data"]["timelines"][0]["intervals"][0]["values"]['visibility'])
    
    # Date 
    valid_date = str(response["data"]["timelines"][0]["intervals"][0]['startTime'])
    da = datesplit(valid_date)
    date = da[2]
    month = da[1]
    year =  da[0]


    # AQI data from aqid obj
    aqi = int(response["data"]["timelines"][0]["intervals"][0]["values"]['epaIndex'])

    return render(request, 'today.html',{
        'bgurl': bgimg(),
        'location': udata.city + ", " + udata.country, 

        'th': temp_convert_to_c(temp_high),
        'fl': temp_convert_to_c(feels_like),

        'vis': vis,

        'ws': wind_speed,
        'gs': gust_speed,
        'wdi': wind_direction,

        'hum': humidity,
        'pre': precipitation,

        'date': date,
        'month': month,
        'year': year,
        'day': da,

        'aqi': aqi,
        'aqi_text': aqitextre(aqi)[0],
        'aqi_text_color': aqitextre(aqi)[1],
    })




# Helper Functions

def aqitextre(aqi):
    aqitara = ['Good', 'Moderate','Unhealthy For Sensitive Groups','Unhealty','Very Unhealthy','Hazardous']
    color = ['#009966', '#ffde33','#ff9933','#cc0033','#660099','#7e0023']
    if aqi>=0 and aqi<=50:
        return aqitara[0],color[0]
    if aqi>=51 and aqi<=100:
        return aqitara[1],color[1]
    if aqi>=101 and aqi<=150:
        return aqitara[2],color[2]
    if aqi>=151 and aqi<=200:
        return aqitara[3],color[3]
    if aqi>=201 and aqi<=300:
        return aqitara[4],color[4]
    if aqi>300:
        return aqitara[5],color[5]


def datesplit(date):
    #2019-03-20T14:09:50Z
    f = date.split("T")
    f = f[0]
    f = f.split("-")
    return f

def converttoint(c):
    a = c.split('.')
    return int(a[0])

def temp_convert_to_c(temp):
    return str(temp)+" °C"

def bgimg():
    #Actual Backgrond JSON for image
    bgurl = 'https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1'
    #getting the json via GET method
    bg = requests.get(bgurl).json()
    #processing json/getting image ur from json
    bgurl = 'https://bing.com'+bg['images'][0]['url']
    #returning background url 
    return bgurl

def lastupdated(lst_updt):
    #2019-03-20T14:09:50Z
    f = lst_updt.split("T")
    f = f[1]
    f = f[:len(f)-4]
    f = f.split(":")
    fTime = f[0]+":"+f[1]
    return fTime


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def weathercode(wcode):
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
    return code.get(wcode, "Not Known")
