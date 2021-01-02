from django import template
import datetime

register = template.Library()

@register.filter
def weekday(date):
    arraydate = date.split('-')
    da = datetime.date(int(arraydate[0]),int(arraydate[1]),int(arraydate[2]))
    weekdays = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    return str(weekdays[da.weekday()]) + " " + arraydate[2]

@register.filter
def onlyweekday(date):
    arraydate = date.split('-')
    da = datetime.date(int(arraydate[0]),int(arraydate[1]),int(arraydate[2]))
    weekdays = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    return str(weekdays[da.weekday()])

@register.filter
# Covert deci/float to int
def toInt(value):
    return int(value)

@register.filter
def icon(code):
    if code>=200 and code<=233:
        return '../static/images/common/icons/thunderstorm.svg'
    if code>=200 and code<=233:
        return '../static/images/common/icons/thunderstorm.svg'
    if code>=300 and code<=302:
        return '../static/images/common/icons/drizzle.svg'
    if code>=500 and code<=522:
        return  '../static/images/common/icons/rain.svg'
    if code>=600 and code<=610:
        return  '../static/images/common/icons/snow.svg'
    if code>=611 and code<=612:
        return  '../static/images/common/icons/rain.svg'
    if code>=621 and code<=623:
        return  '../static/images/common/icons/snow.svg'
    if code>=700 and code<=751:
        return  '../static/images/common/icons/mist.svg'
    if code==800:
        return  '../static/images/common/icons/sunny.svg'
    if code>=801 and code<=802:
        return  '../static/images/common/icons/cloudy.svg'
    if code>=803 and code<=804:
        return  '../static/images/common/icons/clouds.svg'
    if code==900:
        return  '../static/images/common/icons/rain.svg'
    else:
        return '../static/images/common/icons/error.svg'