from db_util.activity_models import ActivitySum


class ActivityLoad:
    """
    Loads activity data from the database
    """
    def __init__(self, db) -> None:
        super().__init__()
        self._db = db


    def load_session_sum(self, act_id: int) -> ActivitySum:
        """
        Note this only loads the first session summary
        :param act_id:
        :return: An ActivitySum object
        """
        act_sum = ActivitySum()
        activity_sum_select = "select summary_key, summary_value, summary_value_int, summary_value_real, summary_value_date " \
                              "from session_sum where activity_id = ? and session_num = 1"
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

    def get_summed_column(self, act_id: int, key: str) -> float:
        """
        Load the total distance of all sessions
        :param act_id: The activity id to query
        :param key: The key of the floating point data value to retrieve
        :return: The total distance of all sessions summed
        """
        summed_column = "select sum(summary_value_real) " \
                              "from session_sum where activity_id = ? and summary_key = ?"
        cur = self._db.cursor()
        cur.execute(summed_column, (act_id, key))
        row = cur.fetchone()
        return row[0]
