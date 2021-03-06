# TODO: For the future - dataclasses from Python 3.7, SQLAlchemy
from datetime import datetime
from db_util.activity_models import ActivityData, ActivityRecord, ActivitySum


class ActivitySave:
    """
    Persists a full health activity to the database
    """
    def __init__(self, db, file_hash: str, user_id: int) -> None:
        super().__init__()
        # self._db = sqlite3.connect('/Users/cturner/Documents/personal/projects/open_health/docs/open_health.sqlite')
        self._db = db
        self._file_hash = file_hash
        self._user_id = user_id

    def is_previously_uploaded(self) -> bool:
        # Determine if the same file hash has already been uploaded by the user
        select_by_hash = "select id from activity where file_hash = ? and user_id = ?"
        cur = self._db.cursor()
        cur.execute(select_by_hash, (self._file_hash, self._user_id))
        id_list = cur.fetchall()
        return len(id_list) > 0

    def save_acvitity(self, act: ActivityData) -> None:
        activity_insert = "insert into activity (user_id, activity_date, device_mfgr, device_model, activity_type, activity_sub_type, file_hash) values(?, ?, ?, ?, ?, ?, ?)"
        act.file_hash = self._file_hash
        act.user_id = self._user_id
        cur = self._db.cursor()
        cur.execute(activity_insert, (act.user_id, act.activity_date, act.device_mfgr, act.device_model, act.activity_type, act.activity_sub_type, act.file_hash))
        act.id = cur.lastrowid
        cur.close()
        self._db.commit()

    def save_acvitity_record(self, act_rec: ActivityRecord) -> None:
        activity_record_insert = "insert into activity_record (activity_id, timestamp, lat, long, heart_rate, distance, altitude, speed, temperature) values(?, ?, ?, ?, ?, ?, ?, ?, ?)"
        cur = self._db.cursor()
        cur.execute(activity_record_insert, (act_rec.activity_id, act_rec.timestamp, act_rec.lat, act_rec.long, act_rec.heart_rate, act_rec.distance, act_rec.altitude, act_rec.speed, act_rec.temperature))
        cur.close()
        self._db.commit()

    def save_session_sum(self, act_sum: ActivitySum) -> None:
        session_sum_insert = "insert into session_sum (activity_id, session_num, summary_key, summary_value, summary_value_int, summary_value_real, summary_value_date) values(?, ?, ?, ?, ?, ?, ?)"
        cur = self._db.cursor()
        for key, value in act_sum.kvps.items():
            str_val = None
            int_val = None
            real_val = None
            date_val = None
            if value is not None:
                if isinstance(value, int):
                    int_val = value
                elif isinstance(value, float):
                    real_val = value
                elif isinstance(value, datetime):
                    date_val = value
                else:
                    str_val = str(value)
                cur.execute(session_sum_insert, (act_sum.activity_id, act_sum.session_num, key, str_val, int_val, real_val, date_val))
        cur.close()
        self._db.commit()

    def save_lap_sum(self, act_sum: ActivitySum) -> None:
        lap_sum_insert = "insert into lap_sum (activity_id, lap_num, summary_key, summary_value, summary_value_int, summary_value_real, summary_value_date) values(?, ?, ?, ?, ?, ?, ?)"
        cur = self._db.cursor()
        for key, value in act_sum.kvps.items():
            str_val = None
            int_val = None
            real_val = None
            date_val = None
            if value is not None:
                if isinstance(value, int):
                    int_val = value
                elif isinstance(value, float):
                    real_val = value
                elif isinstance(value, datetime):
                    date_val = value
                else:
                    str_val = str(value)
                cur.execute(lap_sum_insert, (act_sum.activity_id, act_sum.session_num, key, str_val, int_val, real_val, date_val))
        cur.close()
        self._db.commit()

    def delete_activity(self, act: ActivityData) -> None:
        activity_delete = "delete from activity where id = ? and user_id = ?"
        lap_sum_delete = "delete from lap_sum where activity_id = ?"
        activity_sum_delete = "delete from session_sum where activity_id = ?"
        activity_record_delete = "delete from activity_record where activity_id = ?"
        cur = self._db.cursor()
        cur.execute(activity_record_delete, (act.id, ))
        cur.execute(activity_sum_delete, (act.id, ))
        cur.execute(lap_sum_delete, (act.id, ))
        cur.execute(activity_delete, (act.id, act.user_id))
        self._db.commit()

