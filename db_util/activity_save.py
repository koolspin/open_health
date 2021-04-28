# TODO: For the future - dataclasses from Python 3.7, SQLAlchemy
import sqlite3
#from db import get_db
from db_util.activity_models import ActivityData, ActivityRecord


class ActivitySave:
    """
    Persists a full health activity to the database
    """
    def __init__(self) -> None:
        super().__init__()
        self._db = sqlite3.connect('/Users/cturner/Documents/personal/projects/open_health/docs/open_health.sqlite')

    def save_acvitity(self, act: ActivityData) -> None:
        activity_insert = "insert into activity (user_id, activity_date, device_mfgr, device_model, activity_type, activity_sub_type) values(?, ?, ?, ?, ?, ?)"
        cur = self._db.cursor()
        cur.execute(activity_insert, (act.user_id, act.activity_date, act.device_mfgr, act.device_model, act.activity_type, act.activity_sub_type))
        print(cur.lastrowid)
        act.id = cur.lastrowid
        cur.close()
        self._db.commit()

    def save_acvitity_record(self, act_rec: ActivityRecord) -> None:
        activity_record_insert = "insert into activity_record (activity_id, timestamp, lat, long, heart_rate, distance, altitude, speed, temperature) values(?, ?, ?, ?, ?, ?, ?, ?, ?)"
        cur = self._db.cursor()
        cur.execute(activity_record_insert, (act_rec.activity_id, act_rec.timestamp, act_rec.lat, act_rec.long, act_rec.heart_rate, act_rec.distance, act_rec.altitude, act_rec.speed, act_rec.temperature))
        print(cur.lastrowid)
        cur.close()
        self._db.commit()

    def save_acvitity_sum(self, act: ActivityData) -> None:
        pass

    def close(self) -> None:
        self._db.close()
