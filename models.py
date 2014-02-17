from datetime import time
from django.db import models
from django.contrib.auth.models import User
from pxelinux.ip import IPRangesField


class Item(models.Model):
    """
    Collection of data needed for a boot loader to start an operating system
    or to present it to the user.
    """
    menu_label = models.CharField(
        max_length=79,
        help_text="Title of the item. Used as representation in boot menus.")
    kernel = models.CharField(
        max_length=2047,
        help_text=
        "Path to the operating system binary (mostly a Linux-Kernel, more at "
        "http://www.syslinux.org/wiki/index.php/SYSLINUX#KERNEL_file).")
    initrd = models.CharField(
        max_length=2047,
        blank=True,
        help_text="Path to an initramfs, if any.")
    append = models.CharField(
        max_length=2047,
        blank=True,
        help_text="Command-line arguments for the kernel.")
    label = models.SlugField(
        unique=True,
        help_text=
        "Unique descriptive identifier for the item. Used by admins and "
        "PXELINUX to re-identify items.")
    password = models.CharField(
        max_length=10,
        blank=True,
        help_text=
        "If set, users have to type the given password to boot this item.")
    ipappend = models.CharField(
        max_length=3,
        choices=(
            ('', 'no'),
            ('1', 'yes'),
        ),
        blank=True,
        default=''
    )

    def __str__(self):
        return self.label

    def pxelinux_representation(self):
        """
        Generates a PXELINUX-Configuration containing only the given item.
        """
        lines = ['', ]
        lines.append('label %s' % self.label)
        lines.append('menu label %s' % self.menu_label)
        if self.kernel == 'LOCALBOOT':
            lines.append('localboot 0')
            return "\n".join(lines)
        else:
            lines.append('kernel %s' % self.kernel)
            if len(self.initrd):
                lines.append('initrd %s' % self.initrd)
            if len(self.append):
                lines.append('append %s' % self.append)
            if len(self.password):
                lines.append('menu passwd %s' % self.password)
            if len(self.ipappend):
                lines.append('ipappend %s' % self.ipappend)
        return "\n".join(lines)


class Menu(models.Model):
    """
    Database-representation of a boot menu.
    """
    title = models.CharField(
        max_length=79,
        help_text="Used as entry-title when used as sub-menu.")
    items = models.ManyToManyField(
        Item,
        through='MenuItem',
        blank=True,
        help_text="Items to show in this menu.")
    menus = models.ManyToManyField(
        'self',
        through='MenuRelation',
        blank=True,
        symmetrical=False,
        help_text="Sub-menus to show at the end of this menu.")
    password = models.CharField(
        max_length=10,
        blank=True,
        help_text=
        "If set the user has to type in the given password to switch into "
        "this menu (if it is used as sub-menu) or go to the PXELINUX command "
        "prompt (if this menu is set as main-menu).")
    background_image = models.URLField(
        blank=True,
        help_text=
        "HTTP-URL to an Image of the size 640x480 in PNG or JPEG format.")
    label = models.SlugField(
        unique=True,
        help_text=
        "Unique descriptive identifier for the menu. Used by admins and "
        "PXELINUX to re-identify menus.")
    owner = models.ForeignKey(
        User,
        help_text="Only the given user and super-users can modify this menu.")

    def __str__(self):
        return "%s from %s" % (self.label, self.owner)

    def pxelinux_representation(self, visited=None, top=None):
        """
        Generates a menu-structure in PXELINUX configuration syntax. All linked
        sub-menus get included (exactly once).
        """
        lines = ['', ]
        lines.append("menu title %s" % self.title)
        if visited is None:
            top = self
            visited = set([self])
            if self.password != '':
                lines.append("menu master passwd %s" % self.password)
        if self.background_image != '':
            lines.append("menu background %s" % self.background_image)
        for menu_item in self.menuitem_set.all():
            lines.append(menu_item.item.pxelinux_representation())
        for menu_relation in self.sub_menu.all():
            submenu = menu_relation.super_menu
            if submenu in visited:
                lines.append('label %s' % submenu.label)
                if top == submenu:
                    lines.append('menu goto .top')
                else:
                    lines.append('menu goto %s' % submenu.label)
                lines.append('menu label %s' % submenu.title)
            else:
                visited.add(submenu)
                lines.append('menu begin %s' % submenu.label)
                if submenu.password != '':
                    lines.append("menu passwd %s" % submenu.password)
                lines.append(submenu.pxelinux_representation(
                    visited=visited, top=top))
                lines.append('menu end')
        return "\n".join(lines)

    def pretty_print(self):
        """
        Presentation of the menu in text format. Shows a list of all entries
        grouped in Items and Sub-menus.
        """
        lines = ['Items:', ]
        for menu_item in self.menuitem_set.all():
            lines.append('"%s" (%s)' % (menu_item.item.menu_label,
                                        menu_item.item))
        lines.append('Sub-menus:')
        for menu_relation in self.sub_menu.all():
            lines.append('"%s" (%s)' % (menu_relation.super_menu.title,
                                        menu_relation.super_menu))
        return "\n".join(lines)


class MachineSet(models.Model):
    """
    Represents a set of clients, identified by their IP-addresses, and their
    relation to TimeSlot-Objects and owner.
    """
    name = models.CharField(
        max_length=1023,
        help_text="Descriptive name.")
    ip_ranges = IPRangesField(
        max_length=1024,
        store_text=True,
        blank=True,
        help_text=
        "List of IP-addresses or IP-address-ranges. For example:\" "
        "'127.0.0.1', '192.168/16', ('10.0.0.1', '10.0.0.19'), '::1', "
        "'fe80::/10', '::ffff:172.16.0.2'\"")
    menus = models.ManyToManyField(Menu, through='TimeSlot')
    owner = models.ForeignKey(User, related_name='machine_sets')

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    """
    Specifies the relation between an item and a menu.
    """
    menu = models.ForeignKey(Menu)
    item = models.ForeignKey(Item)
    priority = models.IntegerField()

    class Meta:
        ordering = ['priority']


class MenuRelation(models.Model):
    """
    Specifies relations between menus.
    """
    super_menu = models.ForeignKey(Menu, related_name='super_menu')
    sub_menu = models.ForeignKey(Menu, related_name='sub_menu')
    priority = models.IntegerField()

    def __str__(self):
        return "%s\%s" % (self.super_menu, self.sub_menu)

    class Meta:
        ordering = ['priority']


class TimeSlot(models.Model):
    """
    Specifies the relation between a menu and a machine-set and defines a
    time-span in which the relation should be interpreted as active (causing
    machines to boot according to it).
    """
    machine_set = models.ForeignKey(MachineSet)
    menu = models.ForeignKey(Menu)
    time_start = models.TimeField(default=time(hour=0, minute=0, second=0))
    time_end = models.TimeField(default=time(hour=23, minute=59, second=59))
    priority = models.IntegerField(default=50)
    ui = models.CharField(
        max_length=4,
        choices=(
            ('none', 'Direct Boot'),
            ('vesa', 'Graphical Menu'),
            ('text', 'Text Menu')))
    timeout = models.SmallIntegerField(
        default=100,
        help_text="in deciseconds")

    class Meta:
        ordering = ['priority', 'time_start', 'time_end']
