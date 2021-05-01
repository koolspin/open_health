from db_util.activity_models import ActivitySum


class ActivityLoad:
    """
    Loads activity data from the database
    """
    def __init__(self, db) -> None:
        super().__init__()
        self._db = db


    def load_activity_sum(self, act_id: int) -> ActivitySum:
        act_sum = ActivitySum()
        activity_sum_select = "select summary_key, summary_value, summary_value_int, summary_value_real, summary_value_date " \
                              "from activity_sum where activity_id = ?"
        cur = self._db.cursor()
        cur.execute(activity_sum_select, (act_id, ))
        for row in cur:
            key = row[0]
            if row[1] is not None:
                val = row[1]
            elif row[2] is not None:
                val = row[2]
            elif row[3] is not None:
                val = row[3]
            else:
                val = row[4]
            act_sum.kvps[key] = val
        cur.close()
        return act_sum
