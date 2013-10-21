from django.contrib import admin
from pxelinux.models import Item, Menu, MachineSet, MenuItem, SubMenu, TimeSlot

#region Menu
class MenuItemInline(admin.TabularInline):
    model = Menu.items.through
    extra = 1

class SubMenuInline(admin.TabularInline):
    model = Menu.menus.through
    fk_name = 'sub_menu'
    extra=1

class MenuAdmin(admin.ModelAdmin):
    prepopulated_fields = {'unique_label': ('title',)}
    inlines = [
        MenuItemInline,
        SubMenuInline,
    ]
    fieldsets = (
        (None, {
            'fields': ('title',),
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('unique_label', 'password',
                       'background_image')
        })
    )
#endregion

#region MachineSet
class TimeSlotInline(admin.TabularInline):
    model = MachineSet.menus.through

class MachineSetAdmin(admin.ModelAdmin):
    inlines = [
        TimeSlotInline,
    ]
#endregion

#region Item
class ItemAdmin(admin.ModelAdmin):
    prepopulated_fields = {'unique_label': ('title',)}
    fieldsets = (
        (None, {
            'description': """
            Note: Special PXELINUX values can be used. 'Binary' corralates to
            the 'KERNEL'-command and 'Options' to 'APPEND'.
            """,
            'fields': ('title', 'binary', 'options',)
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('unique_label', 'password')
        })
    )
#endregion

admin.site.register(Menu, MenuAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(MachineSet, MachineSetAdmin)
