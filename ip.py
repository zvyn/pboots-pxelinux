from ast import literal_eval
from django.core.exceptions import ValidationError
from django.utils.six import with_metaclass
from django.db import models
from django import forms
from iptools import IpRangeList


class IPRanges(IpRangeList):
    """
    Extends the IpRangeList class by an equality-operator, basic validation and
    a human-friendly string-representation.
    """
    def __init__(self, value, store_text):
        self.initial_string = value if store_text else None
        range_list = literal_eval("[%s]" % value)
        if type(range_list) != list:
            raise TypeError("Not a list.")
        super(IPRanges, self).__init__(*range_list)

    def __str__(self):
        if self.initial_string is None:
            return super(IPRanges, self).__str__()[1:-1]
        else:
            return self.initial_string

    def __eq__(self, other):
        return repr(self) == repr(other)


class IPRangesField(with_metaclass(models.SubfieldBase, models.TextField)):
    """
    Database field to store IP-address ranges in different syntax but
    unambiguous meaning. Supported notation derives from the possible
    parameters to iptools.IpRangeList
    (see http://python-iptools.readthedocs.org/en/latest/).
    """
    def __init__(self, *args, **kwargs):
        defaults = {
            'store_text': True,
        }
        defaults.update(kwargs)
        self.store_text = defaults.pop('store_text')
        super(IPRangesField, self).__init__(*args, **defaults)

    def to_python(self, value):
        """
        input: string as stored in the database or entered in a form.
        output: IPRanges-object constructed with the input-string
        """
        if isinstance(value, IPRanges):
            return value
        try:
            ip_range_list = IPRanges(value, self.store_text)
            return ip_range_list
        except Exception as e:
            raise ValidationError(
                'Invalid value: %s' % value,
                code='invalid',
            )

    def db_type(self, connection):
        return 'text'

    def formfield(self, **kwargs):
        """
        This needs to be defined for django.admin to do the validation in the
        IPRangesFieldForm-class below.
        """
        defaults = {'form_class': IPRangesFieldForm}
        defaults.update(kwargs)
        return super(IPRangesField,
                     self).formfield(**defaults)


class IPRangesFieldForm(forms.CharField):
    """
    Standard CharField extended by custom validation.
    """
    def validate(self, value):
        try:
            IPRanges(value, True)
        except Exception as e:
            raise ValidationError(
                "Could not interpret this as a Ip-Range-List! (Error: %s)" % e)
