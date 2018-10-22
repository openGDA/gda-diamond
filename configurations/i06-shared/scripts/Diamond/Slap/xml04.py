

#To get the local weather forcast from the Yahoo Weather channel:
#For Didcot: http://weather.yahooapis.com/forecastrss?w=18162&u=c
#For the RSS feed info, see: http://developer.yahoo.com/weather/


#Didcot WOEID: 18162, Temperature Unit: C


import urllib
from xml.dom import minidom

WEATHER_URL = 'http://weather.yahooapis.com/forecastrss'
WEATHER_NS = 'http://xml.weather.yahoo.com/ns/rss/1.0' #xmlns:yweather="http://xml.weather.yahoo.com/ns/rss/1.0"
GDO_NS = 'http://www.w3.org/2003/01/geo/wgs84_pos#'    #xmlns:geo="http://www.w3.org/2003/01/geo/wgs84_pos#"

def getWeather(WOEID):
	url = WEATHER_URL + '?w='+ str(WOEID) + '&u=c'
	doc = minidom.parse( urllib.urlopen(url) )

	print "-----------------------------------------"
	walk(doc.documentElement, outFile=sys.stdout, level=0);

	print "-----------------------------------------"

	ycondition = doc.getElementsByTagNameNS(WEATHER_NS, 'condition')[0]

	forecasts = []
	for node in doc.getElementsByTagNameNS(WEATHER_NS, 'forecast'):
		forecasts.append({ 	'date': node.getAttribute('date'),
				            'low': node.getAttribute('low'),
							'high': node.getAttribute('high'),
							'condition': node.getAttribute('text')
							} )

	return {
        'current_condition': ycondition.getAttribute('text'),
        'current_temp': ycondition.getAttribute('temp'),
        'forecasts': forecasts,
        'title': doc.getElementsByTagName('title')[0].firstChild.data
	}


from pprint import pprint
pprint(getWeather(18162))

