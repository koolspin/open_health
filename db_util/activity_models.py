import datetime


class ActivityData:
    def __init__(self) -> None:
        super().__init__()
        self.id = 0
        self.user_id = 0
        self.activity_date = datetime.datetime.now()
        self.device_mfgr = None
        self.device_model = None
        self.activity_type = None
        self.activity_sub_type = None
        self.file_hash = None


class ActivityRecord:
    def __init__(self) -> None:
        super().__init__()
        self.id = 0
        self.activity_id = 0
        self.timestamp = datetime.datetime.now()
        self.lat = None
        self.long = None
        self.heart_rate = None
        self.distance = None
        self.altitude = None
        self.speed = None
        self.temperature = None


class ActivitySum:
    """
    Activity summary data
    Also known as session data in the fit documentation.
    There may be more than 1 session summaries in an activity (think triathlon).
    The same information are also stored in lap records.
    The only difference being that lap records lack the num_laps field.

    Here are the valid keys:
    start_time (datetime)
    total_elapsed_time (float)
    total_timer_time (float)
    total_distance (float)
    total_calories (float)
    avg_speed (float)
    max_speed (float)
    avg_power (float)
    max_power (float)
    total_ascent (float)
    total_descent (float)
    num_laps (int)
    avg_heart_rate (int)
    max_heart_rate (int)
    avg_temperature (float)
    max_temperature (float)
    avg_cadence (float)
    max_cadence (float)
    total_training_effect (float)
    total_anaerobic_training_effect (float)
    total_strokes (float)
    """
    def __init__(self) -> None:
        super().__init__()
        self.keys = ["start_time", "total_elapsed_time", "total_timer_time", "total_distance", "total_calories",
                     "avg_speed", "max_speed", "avg_power", "max_power", "total_ascent", "total_descent",
                     "num_laps", "avg_heart_rate", "max_heart_rate", "avg_temperature", "max_temperature", "avg_cadence",
                     "max_cadence", "total_training_effect", "total_anaerobic_training_effect", "total_strokes"]
        self.id = 0
        self.activity_id = 0
        # session_num or lap_num depending on the target table
        self.session_num = 0
        self.kvps = {}
