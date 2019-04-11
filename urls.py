from django.conf.urls import url
from pxelinux import views

"""
Pattern to match all IPv6-Notations described in rfc5952. Inspired by
http://stackoverflow.com/a/17871737/2349767.
"""
_IPv6_PATTERN = r'^(?:pxelinux.cfg/)?((?:[0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})|:(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(?::[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(?:ffff(?::0{1,4}){0,1}:){0,1}(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9]).){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])|(?:[0-9a-fA-F]{1,4}:){1,4}:(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9]).){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9]))/?$'

"""
Defines patterns to search for in request-URLs and passes matches to functions
in views.py.
"""
urlpatterns = [
    url(r'^(?:pxelinux.cfg/)?default/?$',
        views.generate_config_from_x_real_ip),
    url(r'^(?:pxelinux.cfg/)?((?:[A-F]|[0-9]){8})/?$',
        views.generate_config_from_hex),
    url(r'^(?:pxelinux.cfg/)?((?:[1-2]?[0-9]?[0-9]\.?){4})/?$',
        views.generate_config),
    url(_IPv6_PATTERN,
        views.generate_config),
    url(r'^(?:pxelinux.cfg/)?set/(.*)/?$',
        views.generate_config_from_machine_set_name),
]
