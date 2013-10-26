from datetime import datetime
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response
from iptools.ipv4 import hex2ip as ip4_hex_to_grouped_decimal
from pxelinux.models import MachineSet

def generate_config_from_x_real_ip(request):
    ip = request.META.get('X-Real-IP')
    if ip is None:
        ip = request.META.get('REMOTE_ADDR')
    return generate_config(request, ip)

def generate_config_from_hex(request, hex_str):
    return generate_config(request, ip4_hex_to_grouped_decimal(hex_str))

def generate_config(request, ip):
    now = datetime.now().time()

    for machines in MachineSet.objects.all():
        if ip in machines.ip_ranges:
            timeslot = machines.timeslot_set.filter(
                time_start__lte=now,
                time_end__gte=now
            )[0]
            break
    menu = timeslot.menu

    if timeslot.ui != 'none':
        context = {
            'menu_binary': settings.STATIC_URL + (
                'menu.c32' if timeslot.ui == 'text' else 'vesamenu.c32'),
            'menu_body': "timeout %s\n%s" % (
                timeslot.timeout, menu.pxelinux_representation())
        }
        return render_to_response("menu.cfg", context)
    else:
        item = menu.items.all()[0]
        return HttpResponse(
            "DEFAULT %s\n%s" %
            (item.unique_label, item.pxelinux_representation()))
