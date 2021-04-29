import datetime


class ActivityData:
    def __init__(self) -> None:
        super().__init__()
        self.id = 0
        self.user_id = 0
        self.activity_date = datetime.datetime.now()
        self.device_mfgr = ""
        self.device_model = ""
        self.activity_type = ""
        self.activity_sub_type = ""


class ActivityRecord:
    def __init__(self) -> None:
        super().__init__()
        self.id = 0
        self.activity_id = 0
        self.timestamp = datetime.datetime.now()
        self.lat = ""
        self.long = ""
        self.heart_rate = 0
        self.distance = 0.0
        self.altitude = 0.0
        self.speed = 0.0
        self.temperature = 0.0


class ActivitySum:
    """
    Activity summary data
    Here are the valid keys:
    start_time (datetime)
    total_elapsed_time (float)
    total_timer_time (float)
    total_distance (float)
    total_calories (float)
    enhanced_avg_speed (float)
    enhanced_max_speed (float)
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
    """
    def __init__(self) -> None:
        super().__init__()
        self.keys = ["start_time", "total_elapsed_time", "total_timer_time", "total_distance", "total_calories",
                     "enhanced_avg_speed", "enhanced_max_speed", "avg_power", "max_power", "total_ascent", "total_descent",
                     "num_laps", "avg_heart_rate", "max_heart_rate", "avg_temperature", "max_temperature", "avg_cadence",
                     "max_cadence", "total_training_effect", "total_training_effect"]
        self.id = 0
        self.activity_id = 0
        self.kvps = {}
