from django.apps import AppConfig

from common.UTIL import is_date


class CsvReaderConfig(AppConfig):
    name = 'csv_reader'


class FieldType:

    def __init__(self, field, selected=True,field_type=None, date_format=None, sample_data=None):
        self.field = field
        self.field_type = field_type
        self.date_format = date_format
        self.sample_data = [] if sample_data is None else sample_data
        if isinstance(selected, bool):
            self.selected = selected
        elif (selected =="1" or selected == 'true'):
            self.selected = True
        else:
            self.selected = False

    def guess_field_type(self):
        not_null_num = 0
        numeric_num = 0
        fix_length = -1
        dot_in_it = False
        for sample in self.sample_data:
            if sample is None:
                continue
            not_null_num += 1
            if fix_length == -1:
                fix_length = len(sample)
            elif fix_length != -2:
                if fix_length != len(sample):
                    fix_length = -2
            if "." in sample and not dot_in_it:
                dot_in_it = True
            try:
                float(sample)
                numeric_num += 1
            except Exception as e:
                pass
        if not_null_num == 0:
            self.field_type = 'factor'
            self.sample_data = []
        elif not_null_num == numeric_num:
            self.field_type = 'numeric'
            if not dot_in_it and fix_length > 0:
                if fix_length == 18 or fix_length == 11:
                    self.field_type = 'factor'
        else:
            date_, size_ = is_date(self.sample_data)
            if date_:
                self.field_type = 'date'
                self.date_format = size_
                self.date_size = size_
            else:
                self.field_type = 'factor'

        self.sample_data = self.sample_data[0:3]

    def add_sample_data(self, sample):
        if sample == '':
            sample = None
        self.sample_data.append(sample)

    def to_db_type(self, project_id, component_id):
        if isinstance(self.sample_data, list):
            sample_data_trim = []
            for idx, sample in enumerate(self.sample_data):
                if idx>2: break
                if sample is None:
                    break
                sample_data_trim.append(sample[:300])
            self.sample_data = ','.join(sample_data_trim)
        from csv_reader.models import CsvReaderInfotype
        return CsvReaderInfotype(project_id= project_id,
                                 component_id= component_id,
                                 field = self.field,
                                 field_type= self.field_type,
                                 date_format=self.date_format,
                                 selected = self.selected,
                                 sample_data=self.sample_data
                                 )

