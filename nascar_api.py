from dataclasses import dataclass
import pandas as pd
import requests
import sqlite3
from datetime import datetime
import re

# first id -> 5143
# last reg. seas. id -> 5173
curr_race_id = 5169 # current id -> 5169

manu_points_url = "https://cf.nascar.com/cacher/2022/1/final/1-manufacturer-points.json" # url to pull manufacturer points
owners_points_url = "https://cf.nascar.com/cacher/2022/1/final/1-owners-points.json" # url to pull owners points
drivers_points_url = "https://cf.nascar.com/cacher/2022/1/final/1-drivers-points.json" # url to pull drivers and driver points
race_results_url = f"https://cf.nascar.com/cacher/2022/1/{curr_race_id}/weekend-feed.json" # url to pull race results


def get_drivers() -> pd.DataFrame:
    """
    Establishes and returns a pandas dataframe of NASCAR drivers 
    """
    driver_json = requests.request("GET", drivers_points_url)
    driver_data = driver_json.json()

    driver_df = pd.json_normalize(driver_data).set_index("position").sort_index()
    return driver_df


def get_manufacturer_data() -> pd.DataFrame:

    """
    Establishes and returns a pandas dataframe of NASCAR manufacturer data
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

    df = pd.json_normalize(manu_data).set_index("position")
    df.drop("url", axis=1, inplace=True)
    df.drop("logo", axis=1, inplace=True)

    return df


def get_manufacture_by_name(manu_name: str):

    """
    Get data about a specific manufacturer using the name of the manufacturer
    """

    manu_df = get_manufacturer_data()

    if manu_name in manu_df.columns: # check for manufacturer name in dataframe columns
        return "Manufacturer does not exist"

    return manu_df.loc[manu_df["manufacturer"] == manu_name]


def get_manufacturer_by_pos(pos: int) -> str:

    """
    Get data about a specific manufacturer using the position of the manufacturer.

    :param pos: Parameter for which manufacturer standings position you would like to see
    """

    if pos > 3: # check if the integer is valid. If it is over 3 it is not valid because there are only 3 manufacturers in NASCAR
        return "Invalid integer"
    
    pos = str(pos) # after check convert integer argument

    manu_df = get_manufacturer_data()

    return manu_df.loc[pos].to_string()

def get_race(race_id):

    """
    Get specific race data using race_id

    :param race_id: Parameter for which race you would like data for
    """

    race_results_url = f"https://cf.nascar.com/cacher/2022/1/{race_id}/weekend-feed.json"
    
    race_results = get_race_results(race_results_url)
    
    race_json = requests.request("GET", race_results_url)

    race_data = race_json.json()

    race_results_len = len(race_data["weekend_race"][0]["results"])

    race_date = race_data["weekend_race"][0]["race_date"]
    race_date = re.sub('T[0-9]*\:[0-9]*\:[0-9]*', '', race_date)
    race_date = datetime.strptime(race_date, "%Y-%m-%d").date()

    race_dict = {
        "race_date": [race_date],
        "track_name": [race_data["weekend_race"][0]["track_name"]],
        "race_name": [race_data["weekend_race"][0]["race_name"]]
    }

    race_df = pd.DataFrame(data=race_dict)

    return [race_df, race_results]


def get_race_results(race_url):

    """
    Helper function for get_race().

    Gets race results for specified race.

    :param race_url: Take race_url that is created from parent function get_race()
    """

    race_json = requests.request("GET", race_url)

    race_data = race_json.json()

    race_results_len = len(race_data["weekend_race"][0]["results"])

    race_results_dict = {
        "finishing_position": [race_data["weekend_race"][0]["results"][result]["finishing_position"] for result in range(race_results_len)],
        "driver_name": [race_data["weekend_race"][0]["results"][result]["driver_fullname"] for result in range(race_results_len)]}

    race_results_df = pd.DataFrame(data=race_results_dict).set_index("finishing_position")
    return race_results_df


race = get_race(5145)
print(race[0])
print("---------------------------------")
print(race[1])