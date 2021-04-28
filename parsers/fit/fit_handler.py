import fitdecode

from db_util.activity_models import ActivityRecord, ActivityData


class FitHandler:
    """
    Handler for the .fit format used by Garmin
    """
    def __init__(self, source_file, db_persistence) -> None:
        super().__init__()
        self._source_file = source_file
        self._db_persistence = db_persistence
        self._activity = None
        self._activity_id = 0

    def handle_file(self) -> None:
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
                        if frame.mesg_type.name == "file_id":
                            self.handle_file_id(frame)
                        if frame.mesg_type.name == "sport":
                            self.handle_sport(frame)
                        if frame.mesg_type.name == "record":
                            self.handle_record(frame)

                    # if frame.has_field('manufacturer'):
                    #     print('Manufacturer: {0}'.format(frame.get_value('manufacturer')))
                    # if frame.has_field('garmin_product'):
                    #     print('Garmin Product: {0}'.format(frame.get_value('garmin_product')))
                    # if frame.has_field('serial_number'):
                    #     print('Serial NUmber: {0}'.format(frame.get_value('serial_number')))
                    # if frame.has_field('time_created'):
                    #     print('Time Created: {0}'.format(frame.get_value('time_created')))
                    # if frame.has_field('speed'):
                    #     print('Speed: {0}'.format(frame.get_value('speed')))
                    # if frame.has_field('heart_rate'):
                    #     print('HR: {0}'.format(frame.get_value('heart_rate')))
                    for field in frame.fields:
                        if isinstance(field, fitdecode.types.FieldData):
                            print('FitDataMessage, K, V: {0}, {1}'.format(field.name, field.value))
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
        self._activity.user_id = 1
        self._activity.activity_date = f.get_value("time_created")
        self._activity.device_mfgr = f.get_value("manufacturer")
        self._activity.device_model = f.get_value("garmin_product")

    def handle_sport(self, f) -> None:
        self._activity.activity_type = f.get_value("sport")
        self._activity.activity_sub_type = f.get_value("sub_sport")
        self._db_persistence.save_acvitity(self._activity)
        self._activity_id = self._activity.id

    def handle_record(self, f) -> None:
        act_rec = ActivityRecord()
        act_rec.activity_id = self._activity_id
        act_rec.timestamp = f.get_value("timestamp")
        act_rec.lat = f.get_value("position_lat")
        act_rec.long = f.get_value("position_long")
        act_rec.heart_rate = f.get_value("heart_rate")
        act_rec.distance = f.get_value("distance")
        act_rec.altitude = f.get_value("enhanced_altitude")
        act_rec.speed = f.get_value("enhanced_speed")
        act_rec.temperature = f.get_value("temperature")
        self._db_persistence.save_acvitity_record(act_rec)
