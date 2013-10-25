from ast import literal_eval
from django.db import models
from django.forms import ValidationError
from iptools import IpRangeList
from iptools.ipv4 import hex2ip as ip4_hex_to_grouped_decimal

class IPRangesField(models.TextField):

    description = "TODO"

    def __init__(self, *args, **kwargs):
        kwargs["help_text"] = 'TODO'
        super(IPRangesField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if isinstance(value, IpRangeList):
            return value
        elif value == '':
            return None
        try:
            return IpRangeList(*literal_eval(value))
        except (TypeError, ValueError, SyntaxError):
            raise ValidationError('Invalid IpRange-Syntax.')

    def get_internel_type(self):
        return 'TextField'

    def get_prep_value(self, value):
        return str(value)

    def db_type(self, connection):
        return 'text'
