from fastapi import FastAPI
import requests
import re
from datetime import datetime

app = FastAPI()

# first id -> 5143
# last reg. seas. id -> 5173
curr_race_id = 5169 # current id -> 5169

manu_points_url = "https://cf.nascar.com/cacher/2022/1/final/1-manufacturer-points.json" # url to pull manufacturer points
owners_points_url = "https://cf.nascar.com/cacher/2022/1/final/1-owners-points.json" # url to pull owners points
drivers_points_url = "https://cf.nascar.com/cacher/2022/1/final/1-drivers-points.json" # url to pull drivers and driver points
race_results_url = f"https://cf.nascar.com/cacher/2022/1/{curr_race_id}/weekend-feed.json" # url to pull race results

@app.get("/get-drivers")
def get_drivers():
    driver_json = requests.request("GET", drivers_points_url)
    driver_data = driver_json.json()

    return driver_data

@app.get("/get-manufacturer-data")
def get_manufacturer_data():

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
def get_manufacture_by_name(manu_name: str):
    manus = get_manufacturer_data()

    for manu in manus:
        if manu["manufacturer"] == manu_name:
            return manu
    else:
        return "Manufacturer does not exist."

@app.get("/get-manufacturer-by-pos/{pos}")
def get_manufacture_by_name(pos: int):

    if pos > 3: # check if the integer is valid. If it is over 3 it is not valid because there are only 3 manufacturers in NASCAR
        return "Invalid integer"

    manus = get_manufacturer_data()

    for manu in manus:
        if int(manu["position"]) == pos:
            return manu

@app.get("/get-race/{race_id}")
def get_race(race_id: int):
    
    race_results_url = f"https://cf.nascar.com/cacher/2022/1/{race_id}/weekend-feed.json"
    
    race_results = get_race_results(race_results_url)
    
    race_json = requests.request("GET", race_results_url)

    race_data = race_json.json()

    # race_results_len = len(race_data["weekend_race"][0]["results"])

    race_date = race_data["weekend_race"][0]["race_date"]
    race_date = re.sub('T[0-9]*\:[0-9]*\:[0-9]*', '', race_date)
    race_date = datetime.strptime(race_date, "%Y-%m-%d").date()

    race_dict = {
        "race_date": race_date,
        "track_name": race_data["weekend_race"][0]["track_name"],
        "race_name": race_data["weekend_race"][0]["race_name"]
    }

    return race_dict

@app.get("/get-race-results/{race_id}")
def get_race_results(race_id: int):

    race_results_url = f"https://cf.nascar.com/cacher/2022/1/{race_id}/weekend-feed.json"

    race_json = requests.request("GET", race_results_url)

    race_data = race_json.json()

    race_results_len = len(race_data["weekend_race"][0]["results"])

    race_results_dict = {
        "results": [{race_data["weekend_race"][0]["results"][result]["driver_fullname"]: race_data["weekend_race"][0]["results"][result]["finishing_position"] for result in range(race_results_len)}],
        "race_name": race_data["weekend_race"][0]["race_name"],
        "track_name": race_data["weekend_race"][0]["track_name"]
        }

    return race_results_dict

@app.get("/get-{driver_name}-standing-position")
def get_driver_standing_position(driver_name: str):

    ds_json = requests.request("GET", drivers_points_url)

    ds_data = ds_json.json()

    for driver in ds_data:
        if driver["driver_name"] == driver_name:
            return driver