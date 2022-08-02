import requests, os, json

def main(latLon: dict) -> float:
    params = {}
    params['appid'] = os.environ["WEATHER_API_KEY"]
    params['lat'] = latLon['lat']
    params['lon'] = latLon['lon']
    params['units'] = 'metric'

    response = requests.get('https://api.openweathermap.org/data/2.5/weather', params=params)
    result = json.loads(response.text)
    
    temp = 0
    if 'main' in result:
        temp = result['main']['temp']

    return temp
