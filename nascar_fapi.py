from lib2to3.pgen2 import driver
from fastapi import FastAPI
import requests
import re
from datetime import datetime

app = FastAPI()

la_clash_id = 5143
daytona_500_id = 5146
# last reg. seas. id -> 5173
curr_race_id = 5169 # current id -> 5169

manu_points_url = "https://cf.nascar.com/cacher/2022/1/final/1-manufacturer-points.json" # url to pull manufacturer points
owners_points_url = "https://cf.nascar.com/cacher/2022/1/final/1-owners-points.json" # url to pull owners points
drivers_points_url = "https://cf.nascar.com/cacher/2022/1/final/1-drivers-points.json" # url to pull drivers and driver points
race_results_url = f"https://cf.nascar.com/cacher/2022/1/{curr_race_id}/weekend-feed.json" # url to pull race results
advanced_driver_stats = f"https://cf.nascar.com/cacher/2022/1/deep-driver-stats.json" # url to pull advanced driver stats
live_feed = "https://cf.nascar.com/cacher/live/live-feed.json"

@app.get("/")
@app.get("/home")
@app.get("/help")
def help():
    """
    Help page. Provides all routes and associated functionality.
    """
    return {
        "/get-drivers": "Get all drivers",
        "/get-manufacturer-data": "Get all manufacturer",
        "/get-manufacturer-by-name/{manu_name}": "Get manufacturer by name, ex: [Chevrolet]]",
        "/get-manufacturer-by-pos/{pos}": "Get manufacturer by position, ex: [1]",
        "/get-race/{race_id}": "Get race by id, ex: [5155]",
        "/get-race-id/{race_name}": "Get race id with race_name, ex: [Daytona 500]",
        "/get-race-results/{race_id}": "Get race results with race id, ex: [5155]",
        "/get-{driver_name}-standing-position": "Get driver standing position with name, ex: [Chase Elliott]",
        "/{driver_name}/{race_id}/result": "Get driver result with name and race id, ex: [Chase Elliott, 5155]",
        "/get-{driver_name}-avg-finish": "Get driver average finish with name, ex: [Chase Elliott]",
    }

@app.get("/get-drivers")
def get_drivers():
    """
    Get all drivers
    """
    driver_json = requests.request("GET", drivers_points_url)
    driver_data = driver_json.json()

    return driver_data

@app.get("/get-manufacturer-data")
def get_manufacturer_data():
    """
    Get all manufacturer data.
    """

    headers = {
        "authority": "cf.nascar.com",
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-language": "en-US,en;q=0.9",
        "if-modified-since": "Wed, 03 Aug 2022 02:00:21 GMT",
        "if-none-match": "^\^05ac0365b19cc9af6be4e7f383b39b33^^",
        "origin": "https://www.nascar.com",
        "referer": "https://www.nascar.com/",
        "sec-ch-ua": "^\^Chromium^^;v=^\^104^^, ^\^"
    }

    manu_json = requests.request("GET", manu_points_url, headers=headers)

    manu_data = manu_json.json()

    return manu_data

@app.get("/get-manufacturer-by-name/{manu_name}")
def get_manufacturer_by_name(manu_name: str):
    """
    Get manufacturer data based on manufacturer name.
    """

    manus = get_manufacturer_data()

    for manu in manus:
        if manu["manufacturer"].lower() == manu_name.lower():
            return manu
    else:
        return "Manufacturer does not exist."

@app.get("/get-manufacturer-by-pos/{pos}")
def get_manufacturer_by_name(pos: int):
    """
    Get manufacturer data by standings position.
    """

    if pos > 3: # check if the integer is valid. If it is over 3 it is not valid because there are only 3 manufacturers in NASCAR
        return "Invalid integer"

    manus = get_manufacturer_data()

    for manu in manus:
        if int(manu["position"]) == pos:
            return manu

@app.get("/get-race/{race_id}")
def get_race(race_id: int):
    """
    Get race data from race_id.
    """
    
    race_url = f"https://cf.nascar.com/cacher/2022/1/{race_id}/weekend-feed.json"
    
    race_json = requests.request("GET", race_url)

    race_data = race_json.json()

    race_date = race_data["weekend_race"][0]["race_date"]
    race_date = re.sub('T[0-9]*\:[0-9]*\:[0-9]*', '', race_date)
    race_date = datetime.strptime(race_date, "%Y-%m-%d").date()

    race_dict = {
        "race_date": race_date,
        "track_name": race_data["weekend_race"][0]["track_name"],
        "race_name": race_data["weekend_race"][0]["race_name"]
    }

    return race_dict

@app.get("/get-race-id-by-race-name/{race_name}")
def get_race_id_by_race_name(race_name: str):
    """
    Get race id from race name.
    """
    
    for race_id in range(la_clash_id, curr_race_id + 1):
        race_data = get_race(race_id)
        retrieved_name = race_data["race_name"].lower()
        if race_name.lower() == retrieved_name:
            return race_id
    
    return "Race not found."

@app.get("/get-race-id-by-track-name/{track_name}")
def get_race_id_by_track_name(track_name: str):
    """
    Get race id from track name.
    """

    all_races = []

    for race_id in range(la_clash_id, curr_race_id + 1):
        race_data = get_race(race_id)
        retrieved_name = race_data["track_name"].lower()
        if track_name.lower() == retrieved_name:
            all_races.append(race_id)
    
    if len(all_races) > 0:
        return all_races
    
    return "No race(s) found."
            
@app.get("/get-race-results/{race_id}")
def get_race_results(race_id: int):
    """
    Get race results from given race id.
    """

    race_results_url = f"https://cf.nascar.com/cacher/2022/1/{race_id}/weekend-feed.json"

    race_json = requests.request("GET", race_results_url)

    race_data = race_json.json()

    race_results_len = len(race_data["weekend_race"][0]["results"])

    race_results_dict = {
        "results": {race_data["weekend_race"][0]["results"][result]["driver_fullname"]: race_data["weekend_race"][0]["results"][result]["finishing_position"] for result in range(race_results_len)},
        "race_name": race_data["weekend_race"][0]["race_name"],
        "track_name": race_data["weekend_race"][0]["track_name"]
        }

    return race_results_dict

@app.get("/get-{driver_name}-standing-position")
def get_driver_standing_position(driver_name: str):
    """
    Get driver's position in the standings by name.
    """

    ds_json = requests.request("GET", drivers_points_url)

    ds_data = ds_json.json()

    for driver in ds_data:
        if driver["driver_name"] == driver_name:
            return driver

@app.get("/{driver_name}/{race_id}/result")
def get_driver_race_result(driver_name: str, race_id: int):
    """
    Get driver results from given driver name and race id.
    """
    
    race_results = get_race_results(race_id)

    if driver_name not in race_results["results"].keys():
        return "Driver has no result for given race id."
    
    driver_result = race_results["results"][driver_name]

    return driver_result

@app.get("/get-{driver_name}-avg-finish")
def get_driver_avg_finish(driver_name: str):
    """
    Get average finish for given driver.
    """

    stats_json = requests.request("GET", advanced_driver_stats)
    stats_data = stats_json.json()
    for driver in range(len(stats_data)):
        if stats_data[driver]["driver_name"] == driver_name:
            return stats_data[driver]["average_finish_position"]

@app.get("/get-live-results")
def get_live_results():
    live_json = requests.request("GET", live_feed)

    live_data = live_json.json()

    return live_data

