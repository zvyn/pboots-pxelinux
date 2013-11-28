from django.contrib import admin
from pxelinux.models import Item, Menu, MachineSet, MenuItem, MenuRelation, TimeSlot

#region Menu
class MenuItemInline(admin.TabularInline):
    model = Menu.items.through
    extra = 1

class MenuRelationInline(admin.TabularInline):
    model = Menu.menus.through
    fk_name = 'sub_menu'
    extra=1

class MenuAdmin(admin.ModelAdmin):
    prepopulated_fields = {'label': ('title',)}
    inlines = [
        MenuItemInline,
        MenuRelationInline,
    ]
    fieldsets = (
        (None, {
            'fields': ('title',),
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('label', 'password',
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
    prepopulated_fields = {'label': ('menu_label',)}
    fieldsets = (
        (None, {
            'fields': ('menu_label', 'kernel', 'initrd', 'append')
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('label', 'password')
        })
    )
#endregion

admin.site.register(Menu, MenuAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(MachineSet, MachineSetAdmin)
