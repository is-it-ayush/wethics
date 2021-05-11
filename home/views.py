import json
from re import template
import re
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


    #g = GeoIP2()
    #ip  = get_client_ip(request)d
    #city = g.city(ip)['city']
    #country = g.country_code(ip)


    #weather api url
    # 09f2b33e311b403386d52c018ec8bbae

    #DEPLOYMENT EDIT IMPORTANT ----- Change "lucknow" to city and "India" to country
    url = 'https://api.weatherbit.io/v2.0/forecast/daily?city=' + "Lucknow" + "&key=15b6cc7dd80e4efbbd317566c35fa74a" + "&country=" + "India" + "&lang=en" + "&days=16"
    #------------------------------------------------------------------------------------------------------



    #Response Object
    response = requests.get(url).json()
    #Date Part Monday 23
    forecast = response['data']

    #DEPLOYMENT EDIT IMPORTANT ----- Change "lucknow" to city and "India" to country
    return render(request,'forecast.html',{'bgurl': bgimg(),'days': forecast, 'location': "Lucknow" + ", " + "India"})
    #------------------------------------------------------------------------------------------------------


def today(request):
    g = GeoIP2()
    ip  = get_client_ip(request)
    city = g.city(ip)['city']
    country = g.country_code(ip)
    url = 'https://api.weatherbit.io/v2.0/forecast/daily?city=' + city + "&key=15b6cc7dd80e4efbbd317566c35fa74a" + "&country=" + country  + "&lang=en" + "&days=1"
    aqiurl = 'https://api.weatherbit.io/v2.0/current/airquality?' + '&city=' + city + '&country=' + country + '&key=15b6cc7dd80e4efbbd317566c35fa74a' + "&lang=en"
    #Response Object
    response = requests.get(url).json()
    aqires = requests.get(aqiurl).json()
    #Getting 'data' feild of the objects
    forecast = response['data'][0]
    if requests.get(aqiurl).status_code != 200:
        ren404(request)
    aqid = aqires['data'][0]

    #Temperature
    temp_high = int(forecast['max_temp'])
    temp_low = int(forecast['min_temp'])
    feels_like = int(forecast['temp'])
    
    #Humidity and precipitation
    precipitation = int(forecast['precip'])
    humidity = int(forecast['rh'])

    #Wind Date
    wind_speed = int(forecast['wind_spd'])
    gust_speed = int(forecast['wind_gust_spd'])
    wind_direction = forecast['wind_cdir']
    wind_degree = int(forecast['wind_dir'])
    #Visibility 
    vis = int(forecast['vis'])
    
    # Date 
    valid_date = forecast['valid_date']
    da = datesplit(valid_date)
    date = da[2]
    month = da[1]
    year =  da[0]


    # AQI data from aqid obj
    aqi = aqid['aqi']


    url = 'https://api.weatherapi.com/v1/forecast.json?key=d5d9fd8eaaab4ee8be5162449210201&q=' + city + '&days=1'
    response = requests.get(url).json()

    data = response['forecast']['forecastday'][0]['hour']
    cdata = []
    for i in data:
        t =i['time']
        yeara,montha,day,hour,min = dateandtime(t)
        o = int(hour)
        lis = [o,converttoint(str(i['temp_c'])),converttoint(str(i['dewpoint_c']))]
        cdata.append(lis)

        # data.addRows([
    #      [new Date(2021,1,2,0,0), 3],
    #     [new Date(2021,1,2,1,0), 1],
    #    [new Date(2021,1,2,2,0), 4],

    return render(request, 'today.html',{
        'bgurl': bgimg(),
        'location': city + ", " + country, 

        'th': temp_convert_to_c(temp_high),
        'tl': temp_convert_to_c(temp_low),
        'fl': temp_convert_to_c(feels_like),

        'vis': vis,

        'ws': wind_speed,
        'gs': gust_speed,
        'wdi': wind_direction,
        'wde': wind_degree,

        'hum': humidity,
        'pre': precipitation,

        'date': date,
        'month': month,
        'year': year,
        'day': valid_date,

        'aqi': aqi,
        'aqi_text': aqitextre(aqi)[0],
        'aqi_text_color': aqitextre(aqi)[1],

        'cd': cdata
    })




# Helper Functions

def dateandtime(t):
    array = t.split(' ')
    #2020-12-12
    date = array[0]
    #21:30
    time = array[1]
    #['2020','12','12']
    datearray = date.split('-')
    #['21','30']
    timearray = time.split(':')

    return datearray[0],datearray[1],datearray[2],timearray[0],timearray[1]


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
    da = date.split('-')
    return da

def converttoint(c):
    a = c.split('.')
    return int(a[0])

def temp_convert_to_c(temp):
    return str(temp)+" ℃"

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
