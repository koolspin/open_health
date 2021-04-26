import fitdecode


class FitHandler:
    """
    Handler for the .fit format used by Garmin
    """
    def __init__(self, source_file) -> None:
        super().__init__()
        self._source_file = source_file

    def handle_file(self) -> None:
        with fitdecode.FitReader(self._source_file) as fit_file:
            frame_num = 0
            for frame in fit_file:
                print('Frame # {0}'.format(frame_num))
                frame_num += 1
                if isinstance(frame, fitdecode.records.FitHeader):
                    print("FitHeader")
                    print("FIT profile version: {0}".format(frame.profile_ver))
                    print("FIT proto version: {0}".format(frame.proto_ver))
                if isinstance(frame, fitdecode.records.FitDataMessage):
                    print("FitDataMessage: {0}".format(frame.name))
                    print("Global Msg Num: {0}".format(frame.global_mesg_num))
                    print("Local Msg Num: {0}".format(frame.local_mesg_num))
                    if frame.mesg_type is not None:
                        print("Mesg Type: {0}".format(frame.mesg_type.name))
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

