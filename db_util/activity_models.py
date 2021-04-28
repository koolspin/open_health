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

