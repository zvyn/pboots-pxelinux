from django.conf.urls import patterns, url
from pxelinux import views

urlpatterns = patterns(
    '',
    url(r'^(?:pxelinux.cfg/)?default/?$',
        views.generate_config_from_x_real_ip),
    url(r'^(?:pxelinux.cfg/)?((?:[A-F]|[0-9]){8})/?$',
        views.generate_config_from_hex),
    url(r'^(?:pxelinux.cfg/)?((?:[1-2]?[0-9]?[0-9]\.?){4})/?$',
        views.generate_config),
    url(r'^(?:pxelinux.cfg/)?set/(.*)/?$',
        views.generate_config_from_machine_set_name),
)
