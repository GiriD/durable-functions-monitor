import requests, os, json

def main(cityName: str) -> dict:
    params = {'appid': os.environ["WEATHER_API_KEY"], 'q': cityName}
    response = requests.get('http://api.openweathermap.org/geo/1.0/direct', params=params)
    result = json.loads(response.text)
    if len(result) == 0:
        raise Exception("No city found with name: " + cityName)
    
    lat_lon = {}
    lat_lon['lat'] = result[0]['lat']
    lat_lon['lon'] = result[0]['lon']
    return lat_lon
