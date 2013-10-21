from django.db import models
from datetime import time

class Item(models.Model):
    title = models.CharField(max_length=79)
    binary = models.CharField(max_length=2047,
                              help_text="Example: http://linux.pool/vmlinuz")
    options = models.CharField(
        max_length=2047, blank=True,
        help_text="Example: initrd=http://linux.pool/init.img")

    unique_label = models.SlugField(
        unique=True,
        help_text="""
        Internally PXELINUX uses labels to distinguish between entries. This
        field can also be useful to distinguish entries with the same
        menu-label but different binary/options.
        """)
    password = models.CharField(max_length=10, blank=True,
                                help_text="This is transferred unencrypted.")

    def __str__(self):
        return self.unique_label

    def pxelinux_representation(self):
        snippet = """
                label %s
                menu label %s
                kernel %s
        """ % (self.unique_label, self.title, self.binary)
        if self.options != '':
            snippet += """
                append %s
            """ % (self.options)
        if self.password != '':
            snippet += """
                menu passwd %s
            """ % (self.password)
        return snippet


class Menu(models.Model):
    title = models.CharField(max_length=79)
    items = models.ManyToManyField(Item, through='MenuItem', blank=True)
    menus = models.ManyToManyField('self', through='SubMenu', blank=True,
                                   symmetrical=False)

    password = models.CharField(max_length=10, blank=True,
                                help_text="This is transferred unencrypted.")
    background_image = models.URLField(blank=True)
    unique_label = models.SlugField(unique=True)

    def __str__(self):
        return self.unique_label

    def pxelinux_representation(self, visited=None, top=None):
        menu_cfg = "menu title %s\n" % (self.title)
        if visited is None:
            top = self
            visited = set([self])
        if self.password != '':
            menu_cfg += "menu master passwd %s\n" % (self.password)
        if self.background_image != '':
            menu_cfg += "menu background %s \n" % (self.background_image)
        for item in self.items.all():
            menu_cfg += item.pxelinux_representation()
        for submenu in self.menus.all():
            if submenu in visited:
                menu_cfg += """
                label %s
                menu goto %s
                menu label %s
                """ % (submenu.unique_label, '.top' if top == submenu else submenu.unique_label, submenu.title)
            else:
                visited.add(submenu)
                menu_cfg += """
                menu begin %s
                %s
                """ % (submenu.unique_label,
                    submenu.pxelinux_representation(visited=visited, top=top))
                menu_cfg += "menu end\n"
        return menu_cfg

class MachineSet(models.Model):
    name = models.CharField(max_length=1023)
    ip_from = models.IPAddressField()
    ip_to = models.IPAddressField()
    menus = models.ManyToManyField(Menu, through='TimeSlot')
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name + ' (' + self.ip_from + '-' + self.ip_to+ ')'

class MenuItem(models.Model):
    menu = models.ForeignKey(Menu)
    item = models.ForeignKey(Item)
    priority = models.IntegerField()

    class Meta:
        ordering = ['priority']

class SubMenu(models.Model):
    super_menu = models.ForeignKey(Menu, related_name='sub_menu')
    sub_menu = models.ForeignKey(Menu, related_name='super_menu')
    priority = models.IntegerField()

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

