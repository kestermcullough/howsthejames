import requests
import re
import json
from time import gmtime, strftime
from bs4 import BeautifulSoup
from tinydb import TinyDB, Query

url = "http://water.weather.gov/ahps2/hydrograph_to_xml.php?gage=rmdv2&output=tabular&time_zone=est"

def river_heights(url):
    response = requests.get(url) #requests looks like by far the best library to do this kind of pull with
    soup = BeautifulSoup(response.text, "lxml") #lxml appears to be common default here, may need to be installed 

    observed = []
    forecasted = []

    mytabs = soup.find_all('table') #there are three tables here, first is garbage, second is observed, third is forecast

    for trs in mytabs[1].find_all('tr'): #source for this:http://stackoverflow.com/questions/24593282/web-scraping-daily-tables-into-csv-with-beautifulsoup-in-python
        tds = trs.find_all('td')
        row = [elem.text.strip().encode('utf-8') for elem in tds]
        #print row
        observed.append(row)
    
    for trs in mytabs[2].find_all('tr'): #table[1] is observed data in the html, table[2] is forecasted, table[0] is junk
        tds = trs.find_all('td')
        row = [elem.text.strip().encode('utf-8') for elem in tds]
        #print row
        forecasted.append(row)
    
    observedNow = observed[2] #observed is the list of lists containing our data, observedNows is just the list with the date, height, and flow we want
    forecastedNow = forecasted[2] 

    #print observedNow[1] #observedNow[1] is the hieght in string format
    #print forecastedNow[1]
    heightNow = re.findall("\d+\.\d+", observedNow[1])[0]
    heightTomorrow = re.findall("\d+\.\d+", forecastedNow[1])[0]
    heightNow = float(heightNow)
    heightTomorrow = float(heightTomorrow)
    heightNow = format(heightNow, '.1f')
    heightTomorrow = format(heightTomorrow, '.1f')
    return heightNow, heightTomorrow
    #return re.findall("\d+\.\d+", observedNow[1])[0], re.findall("\d+\.\d+", forecastedNow[1])[0]

def riverTemps(url):
    response = requests.get(url) #requests looks like by far the best library to do this kind of pull with
    soup = BeautifulSoup(response.text, "lxml")
    
    tempString = soup(text=re.compile('recent'))[3] #search the html text for the word 'recent', this is where all the values are, 4th in list is temp in C
    #print tempString
    tempC = float(re.findall("\d+\.\d+", tempString)[0]) #regex, produces list of numbers, first is one we want, turn to float and store
    tempF = tempC * 1.8 +32
    return format(tempF, '.0f') #round to no decimal places


def darkSkyCallTemps(url):
    response = requests.get(url)

    # For successful API call, response code will be 200 (OK)
    if(response.ok):
        jData = json.loads(response.content)
        tempForecastF = jData['daily']['data'][0]['temperatureMax']
        tempNowF = jData['currently']['temperature']
        return format(tempNowF, '.0f'), format(tempForecastF, '.0f')
        #return jData
    else:
      # If response code is not ok (200), print the resulting http error code with description
        response.raise_for_status()


currentHeight, forecastedHeight = river_heights("http://water.weather.gov/ahps2/hydrograph_to_xml.php?gage=rmdv2&output=tabular&time_zone=est")
currentWater = riverTemps("http://waterdata.usgs.gov/usa/nwis/uv?02035000")
currentTemp, forecastTemp = darkSkyCallTemps("https://api.forecast.io/forecast/1999155451fa19339ca7acb65b970fcf/37.5333,-77.4667")

data = {
    'currentHeight' : currentHeight,
    'currentWater' : currentWater,
    'currentTemp' : currentTemp,
    'forecastHeight' : forecastedHeight,
    'forecastWater' : 0,
    'forecastTemp' : forecastTemp,
    'dateFetched' : strftime("%Y-%m-%d %H:%M:%S")
}

with open('public_html/data.json', 'w') as f:
     json.dump(data, f)

db = TinyDB('db.json')
db.insert(data)
