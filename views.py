import logging
from datetime import datetime
from django.conf import settings
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from iptools.ipv4 import hex2ip as ip4_hex_to_grouped_decimal
from pxelinux.models import MachineSet


logger = logging.getLogger(__name__)


def generate_config_from_machine_set_name(request, machine_set_name):
    machine_set = MachineSet.objects.get(name=machine_set_name)
    ip = machine_set.ip_ranges.ips[0][0]
    return generate_config(request, ip)


def generate_config_from_x_real_ip(request):
    """
    Get the IP-address from the HTTP-Header and generate the corresponding
    configuration. Uses REMOTE_ADDR if X-Real-IP is not set.
    """
    ip = request.META.get('X-Real-IP')
    if ip is None:
        ip = request.META.get('REMOTE_ADDR')
    return generate_config(request, ip)


def generate_config_from_hex(request, hex_str):
    """
    Convert a hexadecimal encoded IP-address to the grouped decimal
    representation and generate the corresponding configuration.
    """
    return generate_config(request, ip4_hex_to_grouped_decimal(hex_str))


def generate_config(request, ip):
    """
    Generates a PXELINUX configuration from the menu object in the active
    timeslot with  the highest rating in the machine set for the given
    IP-address or if that fails for the fallback-address '255.255.255.255'.
    """

    now = datetime.now().time()
    fallback_ip = '255.255.255.255'
    timeslots = []

    for machines in MachineSet.objects.all():
        if ip in machines.ip_ranges:
            timeslots = machines.timeslot_set.filter(
                time_start__lte=now,
                time_end__gte=now)
            break
    if not (ip == fallback_ip or len(timeslots)):
        logger.error('No timeslot for %s at %s. Trying %s instead.'
                     % (ip, now, fallback_ip))
        return generate_config(request, fallback_ip)
    elif len(timeslots):
        timeslot = timeslots[0]
    else:
        logger.error('No timeslot for %s at %s. Giving up!' % (ip, now))
        raise Http404

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
        item = menu.menuitem_set.all()[0].item
        return HttpResponse(
            "DEFAULT %s\n%s" %
            (item.label, item.pxelinux_representation()))
