import fitdecode

from db_util.activity_models import ActivityRecord, ActivityData, ActivitySum


class FitHandler:
    """
    Handler for the .fit format used by Garmin
    """
    # Garmin stores lat long in a 32 bit int. 2^32 / 360 = 11930464.7111, which is the constant defined below
    GARMIN_LOC_DIVISOR = 11930464.7111

    def __init__(self, source_file, db_persistence) -> None:
        super().__init__()
        self._source_file = source_file
        self._db_persistence = db_persistence
        self._activity = None
        self._activity_id = 0
        self._activity_saved = False
        self._current_lap_number = 0
        self._current_session_number = 0

    def handle_file(self) -> None:
        """
        Note that we parse the .fit file twice - once to capture all of the session information and the 2nd
        time to capture the records with the fitness samples.

        :return: None
        """
        # First pass
        with fitdecode.FitReader(self._source_file) as fit_file:
            frame_num = 0
            for frame in fit_file:
                print('First pass Frame # {0}'.format(frame_num))
                frame_num += 1
                if isinstance(frame, fitdecode.records.FitHeader):
                    # TODO: Validate the protocol version
                    print("FitHeader")
                    print("FIT profile version: {0}".format(frame.profile_ver))
                    print("FIT proto version: {0}".format(frame.proto_ver))
                if isinstance(frame, fitdecode.records.FitDataMessage):
                    print("FitDataMessage: {0}".format(frame.name))
                    print("Global Msg Num: {0}".format(frame.global_mesg_num))
                    print("Local Msg Num: {0}".format(frame.local_mesg_num))
                    if frame.mesg_type is not None:
                        print("Mesg Type: {0}".format(frame.mesg_type.name))
                        if frame.mesg_type.name == "file_id":
                            self.handle_file_id(frame)
                        if frame.mesg_type.name == "session":
                            if self.handle_activity_save(frame):
                                break
                    # for field in frame.fields:
                    #     if isinstance(field, fitdecode.types.FieldData):
                    #         print('FitDataMessage, K, V: {0}, {1}'.format(field.name, field.value))
        # Second pass
        with fitdecode.FitReader(self._source_file) as fit_file:
            frame_num = 0
            for frame in fit_file:
                print('Frame # {0}'.format(frame_num))
                frame_num += 1
                if isinstance(frame, fitdecode.records.FitHeader):
                    # TODO: Validate the protocol version
                    print("FitHeader")
                    print("FIT profile version: {0}".format(frame.profile_ver))
                    print("FIT proto version: {0}".format(frame.proto_ver))
                if isinstance(frame, fitdecode.records.FitDataMessage):
                    print("FitDataMessage: {0}".format(frame.name))
                    print("Global Msg Num: {0}".format(frame.global_mesg_num))
                    print("Local Msg Num: {0}".format(frame.local_mesg_num))
                    if frame.mesg_type is not None:
                        print("Mesg Type: {0}".format(frame.mesg_type.name))
                        if frame.mesg_type.name == "record":
                            self.handle_record(frame)
                        if frame.mesg_type.name == "session":
                            self.handle_session(frame)
                        if frame.mesg_type.name == "lap":
                            self.handle_lap(frame)
                    # for field in frame.fields:
                    #     if isinstance(field, fitdecode.types.FieldData):
                    #         print('FitDataMessage, K, V: {0}, {1}'.format(field.name, field.value))
                if isinstance(frame, fitdecode.records.FitDefinitionMessage):
                    print("FitDefinitionMessage: {0}".format(frame.name))
                    print("Def Global Msg Num: {0}".format(frame.global_mesg_num))
                    print("Def Local Msg Num: {0}".format(frame.local_mesg_num))
                    if frame.mesg_type is not None:
                        print("Def Mesg Type: {0}".format(frame.mesg_type.name))
                    for field_def in frame.field_defs:
                        print('FitDefinitionMessage: K, T: {0}, {1}'.format(field_def.name, field_def.type.name))
                if isinstance(frame, fitdecode.records.FitCRC):
                    print("FitCRC")

    def handle_file_id(self, f) -> None:
        self._activity = ActivityData()
        self._activity.activity_date = f.get_value("time_created")
        self._activity.device_mfgr = f.get_value("manufacturer", fallback=None)
        self._activity.device_model = f.get_value("garmin_product", fallback=None)

    def handle_activity_save(self, f) -> bool:
        """
        Handles saving of the activity record.
        Note this only looks at the first session record so may be misleading for multi-session activities
        :param f: The frame to parse
        :return: True if the activity has been saved, false if not
        """
        if f.has_field("start_time"):
            self._activity.activity_date = f.get_value("start_time")
        if f.has_field("sport"):
            self._activity.activity_type = f.get_value("sport")
            self._activity.activity_sub_type = f.get_value("sub_sport", fallback=None)
            self._db_persistence.save_acvitity(self._activity)
            self._activity_id = self._activity.id
            return True
        else:
            return False

    def save_unknown_activity(self) -> None:
        """
        If we've completed our first pass and haven't encountered a session record, we save this as an unknown activity
        :return: None
        """
        self._activity.activity_type = "Unknown"
        self._db_persistence.save_acvitity(self._activity)
        self._activity_id = self._activity.id

    def handle_record(self, f) -> None:
        act_rec = ActivityRecord()
        act_rec.activity_id = self._activity_id
        act_rec.timestamp = f.get_value("timestamp")
        # Note we limit the precision on lat / long to 5 digits. 5 digits give 1m accuracy at the equator
        # This is good enough for our purposes.
        fit_lat = f.get_value("position_lat", fallback=None)
        if fit_lat is not None:
            act_rec.lat = round(fit_lat / FitHandler.GARMIN_LOC_DIVISOR, 5)
        fit_long = f.get_value("position_long", fallback=None)
        if fit_long is not None:
            act_rec.long = round(fit_long / FitHandler.GARMIN_LOC_DIVISOR, 5)
        #
        act_rec.heart_rate = f.get_value("heart_rate", fallback=None)
        act_rec.distance = f.get_value("distance", fallback=None)
        act_rec.altitude = f.get_value("enhanced_altitude", fallback=None)
        act_rec.speed = f.get_value("enhanced_speed", fallback=None)
        act_rec.temperature = f.get_value("temperature", fallback=None)
        self._db_persistence.save_acvitity_record(act_rec)

    def handle_session(self, f) -> None:
        act_sum = ActivitySum()
        act_sum.activity_id = self._activity_id
        act_sum.session_num = self._current_session_number
        for key in act_sum.keys:
            if f.has_field(key):
                act_sum.kvps[key] = f.get_value(key)
        self._db_persistence.save_session_sum(act_sum)
        self._current_session_number += 1

    def handle_lap(self, f) -> None:
        act_sum = ActivitySum()
        act_sum.activity_id = self._activity_id
        act_sum.session_num = self._current_lap_number
        for key in act_sum.keys:
            if f.has_field(key):
                act_sum.kvps[key] = f.get_value(key)
        self._db_persistence.save_lap_sum(act_sum)
        self._current_lap_number += 1
