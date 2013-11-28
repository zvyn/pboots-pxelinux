from datetime import time
from django.db import models
from django.contrib.auth.models import User
from pxelinux.ip import IPRangesField

class Item(models.Model):
    menu_label = models.CharField(max_length=79)
    kernel = models.CharField(
        max_length=2047,
        help_text="Example: http://linux.pool/vmlinuz\nSee also:"
            "http://www.syslinux.org/wiki/index.php/SYSLINUX#KERNEL_file\n"
            "Use keyword 'LOCALBOOT' here for a local-boot option."
    )
    initrd = models.CharField(
        max_length=2047, blank=True,
        help_text="Example: http://linux.pool/init.img")
    append = models.CharField(
        max_length=2047, blank=True,
        help_text="Example: initrd=http://linux.pool/init.img")

    label = models.SlugField(
        unique=True,
        help_text="""
        Internally PXELINUX uses labels to distinguish between entries. This
        field can also be useful to distinguish entries with the same
        menu-label but different binary/options.
        """)
    password = models.CharField(max_length=10, blank=True,
                                help_text="This is transferred unencrypted.")

    def __str__(self):
        return self.label

    def pxelinux_representation(self):
        lines = ['',]
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
        return "\n".join(lines)


class Menu(models.Model):
    title = models.CharField(max_length=79)
    items = models.ManyToManyField(Item, through='MenuItem', blank=True)
    menus = models.ManyToManyField('self', through='MenuRelation', blank=True,
                                   symmetrical=False)

    password = models.CharField(max_length=10, blank=True,
                                help_text="This is transferred unencrypted.")
    background_image = models.URLField(blank=True)
    label = models.SlugField(unique=True)

    def __str__(self):
        return self.label

    def pxelinux_representation(self, visited=None, top=None):
        lines = ['',]
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
                lines.append(submenu.pxelinux_representation(
                    visited=visited, top=top))
                lines.append('menu end')
        return "\n".join(lines)

class MachineSet(models.Model):
    name = models.CharField(max_length=1023)
    ip_ranges = IPRangesField(max_length=1024, store_text=True, blank=True)
    menus = models.ManyToManyField(Menu, through='TimeSlot')
    owner = models.ForeignKey(User, related_name='machine_sets')

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    menu = models.ForeignKey(Menu)
    item = models.ForeignKey(Item)
    priority = models.IntegerField()

    class Meta:
        ordering = ['priority']

class MenuRelation(models.Model):
    super_menu = models.ForeignKey(Menu, related_name='super_menu')
    sub_menu = models.ForeignKey(Menu, related_name='sub_menu')
    priority = models.IntegerField()

    def __str__(self):
        return "%s\%s" % (self.super_menu, self.sub_menu)

    class Meta:
        ordering = ['priority']

class TimeSlot(models.Model):
    machine_set = models.ForeignKey(MachineSet)
    menu = models.ForeignKey(Menu)
    time_start = models.TimeField(default=time(hour=0, minute=0, second=0))
    time_end = models.TimeField(default=time(hour=23, minute=59, second=59))
    priority = models.IntegerField(default=50)
    ui = models.CharField(
        max_length=4,
        choices = (
            ('none', 'Direct Boot'),
            ('vesa', 'Graphical Menu'),
            ('text', 'Text Menu')))
    timeout = models.SmallIntegerField(default=100)

    class Meta:
        ordering = ['priority', 'time_start', 'time_end']

