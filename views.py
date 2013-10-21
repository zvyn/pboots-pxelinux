from struct import pack as struct_pack
from socket import inet_ntoa as ip_pack_to_str
from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import render_to_response
# from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from pxelinux.models import MachineSet
from pxelinux.settings import PXE_BINARIES_URL as menu_binary_path

def IPv4_hex_to_dec(hex_ip_string):
    return ip_pack_to_str(struct_pack(">L", int(hex_ip_string, 16)))

def generate_config(request, hex_ip_string):
    ip = IPv4_hex_to_dec(hex_ip_string)
    now = datetime.now().time()
    timeslot = MachineSet.objects.get(
        ip_from__lte=ip, ip_to__gte=ip
    ).timeslot_set.filter(
        time_start__lte=now,
        time_end__gte=now
    )[0]
    menu = timeslot.menu

    # TODO: define fallback-behaviour for the following exceptions:
    #except:
        # IndexError: No menu in this timeslot.
        # ObjectDoesNotExist: IP-Address not found in machine-sets
        # MultipleObjectsReturned: Overlapping machine-sets match

    if timeslot.ui != 'none':
        context = {
            'menu_binary': menu_binary_path + (
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
