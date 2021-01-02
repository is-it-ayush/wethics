import json
from re import template
import re
from typing import List
from django.http import response
from django.http.response import HttpResponse, HttpResponseGone
from django.shortcuts import render 
from django.contrib.gis.geoip2 import GeoIP2
# Create your views here.
import requests
import datetime, time
import geoip2.webservice

def home(request):
    g = GeoIP2()
    ip  = get_client_ip(request)
    city = g.city(ip)
    country = g.country_code(ip)
    #weather api url
    url = 'https://api.weatherapi.com/v1/current.json?key=d5d9fd8eaaab4ee8be5162449210201&q=' + city
    #Response Object
    response = requests.get(url).json()
    #temperature variable
    temp = int(response['current']['temp_c'])
    #last updated temperature varible
    lst_updt = response['current']['last_updated']
    
    return render(request, 'index.html',{'location': city + ", " + country, 'temperature' : temp_convert_to_c(temp), 'weather':  response['current']['condition']['text'], 'bgurl': bgimg(), 'last_updated': lastupdated(lst_updt)})



def forecast(request):
    g = GeoIP2()
    ip  = get_client_ip(request)
    city = g.city(ip)
    country = g.country_code(ip)
    #weather api url
    # 09f2b33e311b403386d52c018ec8bbae
    url = 'https://api.weatherbit.io/v2.0/forecast/daily?city=' + city + "&key=b7ab2955200341809f383396cc34e944" + "&country=" + country + "&lang=en" + "&days=16"
    #Response Object
    response = requests.get(url).json()
    #Date Part Monday 23
    forecast = response['data']
    return render(request,'forecast.html',{'bgurl': bgimg(),'days': forecast, 'location': response.city.name + ", " + country})


def today(request):
    g = GeoIP2()
    ip  = get_client_ip(request)
    city = g.city(ip)
    country = g.country_code(ip)
    url = 'https://api.weatherbit.io/v2.0/forecast/daily?city=' + city + "&key=b7ab2955200341809f383396cc34e944" + "&country=" + country  + "&lang=en" + "&days=1"
    aqiurl = 'https://api.weatherbit.io/v2.0/current/airquality?' '&city=' + city + '&country=' + country + '&key=b7ab2955200341809f383396cc34e944' + "&lang=en"
    #Response Object
    response = requests.get(url).json()
    aqires = requests.get(aqiurl).json()
    #Getting 'data' feild of the objects
    forecast = response['data'][0]
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
    # Getting the time in this format(format is from API): 25-12-2020 00:00    
    # Splitting the string from whitespace(" ")
    x = lst_updt.split(" ")
    # Now in 1st indice we have got the time while in 0th indice we have date..(we dont need date) hence splitting the 1st indice again from colon
    x = x[1].split(':')
    #Now x=['00','00'], so checking if hour is greater than 12 and subtracting it to convert from 24 hour format to 12
    # No need to change the minute part. 
    if int(x[0])>=12:
       return str(int(x[0])-12)+":"+x[1]+" P.M."
    elif int(x[0])<12:
       return str(int(x[0])-12)+":"+x[1]+" A.M."


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip