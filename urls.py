from django.conf.urls import patterns, url

from pxelinux import views

urlpatterns = patterns(
    '',
    url(r'(?:pxelinux.cfg/)?((?:[A-F]|[0-9]){8})/?$', views.generate_config),
)
