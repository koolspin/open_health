# This file contains various queries and adapters for feeding Jinja directly
import math
from datetime import datetime, timedelta, date
from typing import List
from db_util.activity_load import ActivityLoad
from db_util.activity_models import ActivitySum


def miles_to_km(miles):
    miles_to_km_conversion = 1.60934
    km = miles * miles_to_km_conversion
    return km


def km_to_miles(km):
    km_to_miles_conversion = 0.621371
    miles = km * km_to_miles_conversion
    return miles


def convert_height(meters):
    meters_to_feet_conversion = 3.28084
    feet = meters * meters_to_feet_conversion
    return feet


def convert_temp(cel):
    fa = (cel * 1.8) + 32.0
    return fa


def normalize_value(k, v):
    """
    Normalize a known value by converting as necessary (km to miles, etc)
    :param k: The key of the item to possibly convert
    :param v: The raw value of the item
    :return: A tuple consisting of the normalized value of the item and the unit for the item
    """
    normalize_height_keys = ["total_ascent", "total_descent"]
    normalize_distance_keys = ["total_distance"]
    normalize_temp_keys = ["avg_temperature", "max_temperature"]
    normalize_speed_keys = ["avg_speed", "max_speed"]
    normalize_elapsed_keys = ["total_elapsed_time", "total_timer_time"]
    val = v
    unit = ""
    if k in normalize_height_keys:
        val = '{0:.2f}'.format(convert_height(v))
        unit = "feet"
    elif k in normalize_distance_keys:
        val = '{0:.2f}'.format(km_to_miles(v / 1000.0))
        unit = "miles"
    elif k in normalize_temp_keys:
        val = int(convert_temp(v))
        unit = "deg F"
    elif k in normalize_speed_keys:
        val = '{0:.2f}'.format(km_to_miles(v / 1000.0) * 3600.0)
        unit = "mph"
    elif k in normalize_elapsed_keys:
        val = str(timedelta(seconds=int(v)))
        unit = "hh:mm:ss"
    return val, unit


def query_activity_list(db, user_id) -> List:
    """
    Query the activities to display in the master activity list
    :param db: A database connection object
    :param user_id: The id of the user
    :return: An array of data objects for the main activity page
    """
    activity_sel = 'select id, activity_date as "ad [timestamp]", activity_type, activity_sub_type from activity where user_id = ? order by activity_date'
    cur = db.cursor()
    cur.execute(activity_sel, (user_id,))
    data = []
    for row in cur:
        col = []
        col.append(row[0])
        col.append(row[1])
        col.append(row[2])
        col.append(row[3])
        act_id = row[0]
        act_load = ActivityLoad(db)
        total_dist = act_load.get_summed_column(act_id, "total_distance")
        if total_dist is not None:
            col.append(km_to_miles(total_dist / 1000.0))
        else:
            col.append(None)
        total_time = act_load.get_summed_column(act_id, "total_timer_time")
        if total_time is not None:
            elapsed_time = timedelta(seconds=int(total_time))
            col.append(str(elapsed_time))
        else:
            col.append(None)
        data.append(col)
    cur.close()
    return data


def query_activity_detail(db, user_id, activity_id) -> List:
    """
    Query the activities to display in the master activity list
    :param db: A database connection object
    :param user_id: The id of the user
    :param activity_id: The id of the activity to query
    :return: An array of data objects for the activity detail page
    """
    activity_detail = 'select r.timestamp as "ad [timestamp]", r.lat, r.long, r.heart_rate, r.distance, r.altitude, r.speed, ' \
                      'r.temperature from activity_record r inner join activity a on r.activity_id = a.id ' \
                      'where a.user_id = ? and r.activity_id = ? order by r.timestamp'
    act_load = ActivityLoad(db)
    all_laps = act_load.load_lap_sum(activity_id)
    if len(all_laps) > 0:
        cur_lap_start = next(iter(all_laps))
    else:
        cur_lap_start = None
    cur = db.cursor()
    cur.execute(activity_detail, (user_id, activity_id))
    dat = []
    for row in cur:
        # Convert to km, the possibly to miles?
        col = []
        cur_start_time = row[0]
        col.append(row[0])
        col.append(row[1])
        col.append(row[2])
        col.append(row[3])
        if row[4] is not None:
            col.append(km_to_miles(row[4] / 1000.0))
        else:
            col.append(None)
        if row[5] is not None:
            # It looks like the alititude records are already scaled and offset by the fitdecode lib
            # So here we just convert to the preferred height scale
            col.append(convert_height(row[5]))
        else:
            col.append(None)
        if row[6] is not None:
            col.append(km_to_miles(row[6] / 1000.0) * 3600.0)
        else:
            col.append(None)
        if row[7] is not None:
            col.append(convert_temp(row[7]))
        else:
            col.append(None)
        if cur_lap_start is not None and cur_start_time >= cur_lap_start:
            lap = all_laps.get(cur_lap_start)
            lap_num = lap.session_num + 1
            all_laps.pop(cur_lap_start, None)
            col.append(lap_num)
            if len(all_laps) > 0:
                cur_lap_start = next(iter(all_laps))
            else:
                cur_lap_start = None
        else:
            col.append(None)
        dat.append(col)
    cur.close()
    return dat


def query_activity_summary(db, activity_id) -> List:
    """
    Query the activity summary information for a given activity
    :param db: db connection
    :param user_id: ID of the user
    :param activity_id: ID of the activity
    :return: An array of data objects for the activity summary page
    """
    act_sum = ActivitySum()
    act_load = ActivityLoad(db)
    sum = act_load.load_session_sum(activity_id)
    dat = []
    for key in act_sum.keys:
        v = sum.kvps.get(key)
        if v is not None:
            kv = []
            kv.append(key)
            val, unit = normalize_value(key, v)
            kv.append(val)
            kv.append(unit)
            dat.append(kv)
    return dat


def query_user_info(db, user_id) -> List:
    """
    Query user information for a specific user
    :param db: db connection
    :param user_id: ID of the user
    :return:
    :return: An array of data objects for the activity detail page
    """
    user_info = db.execute(
        'SELECT birth_date, target_weekly_distance, target_weekly_time FROM user WHERE id = ?', (user_id,)
    ).fetchone()
    data = []
    age = None
    for ix in range(len(user_info)):
        if ix == 0:
            if user_info[ix] is not None:
                td = timedelta(days=365.25)
                # age = datetime.date.today().year - user_info[ix].year
                age = date.today() - user_info[ix]
                age = math.trunc(age / td)
        if ix == 1:
            if user_info[ix] is not None:
                data.append(round(km_to_miles(user_info[ix]), 1))
            else:
                data.append(0)
        else:
            data.append(user_info[ix])
    data.append(age)
    return data


def update_user_info(db, user_id, birth_date, target_distance, target_time) -> None:
    """
    Updates the user info table
    :param db: Database connection
    :param user_id: ID of the user
    :param birth_date: The birthdate of the user
    :param target_distance: Target weekly distance (in miles for now)
    :param target_time: Target weekly time in minutes
    :return: None
    """
    db.execute(
        "update user set birth_date = ?, target_weekly_distance = ?, target_weekly_time = ? where id = ?",
        (birth_date, target_distance, target_time, user_id)
    )
    db.commit()
