from django.apps import AppConfig


class RobotXConfig(AppConfig):
    name = 'robot_x'


class StructureClass:

    def __init__(self, field, field_type, date_format=None, selected=True):
        self.field = field
        self.field_type = field_type
        self.date_format = date_format
        # self.date_size = date_size
        # if isinstance(ignore, bool):
        #     self.ignore = ignore
        # else:
        #     self.ignore = ignore == 'true'
        # if self.ignore:
        #     self.selected = False
        if isinstance(selected, bool):
            self.selected = selected
        else:
            self.selected = selected == 'true'

