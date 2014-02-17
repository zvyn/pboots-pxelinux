from django.contrib import admin
from pxelinux.models import *


def has_change_and_delete_permission(request, obj):
    """
    True if the user in request is a superuser or the owner of obj.
    """
    if request.user.is_superuser or obj.owner == request.user:
        return True
    return False


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 1


class MenuRelationInline(admin.TabularInline):
    model = MenuRelation
    fk_name = 'sub_menu'


class MenuAdmin(admin.ModelAdmin):
    """
    MenuItems and MenuRelations are shown as tables in the Menu configuration.
    Only essential fields are shown as default. All others hide behind an
    'Advanced'-link. Labels are generated from the value in title.
    """
    prepopulated_fields = {'label': ('title',)}
    inlines = [
        MenuItemInline,
        MenuRelationInline,
    ]
    fieldsets = (
        (None, {
            'fields': ('title', 'owner'),
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('label', 'password',
                       'background_image')
        })
    )

    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return request.user.is_superuser
        return has_change_and_delete_permission(request, obj)

    def menu_content(self, instance):
        return instance.pretty_print()

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        elif obj is None or has_change_and_delete_permission(request, obj):
            return ['owner']
        return ('title', 'label', 'owner', 'menu_content')

    def get_prepopulated_fields(self, request, obj=None):
        if obj is None or has_change_and_delete_permission(request, obj):
            return {'label': ('title',)}
        return {}

    def get_fieldsets(self, request, obj=None):
        if obj is None or has_change_and_delete_permission(request, obj):
            return self.fieldsets
        return ((None, {'fields': ('title', 'label', 'owner', 'menu_content'),
                        }), )

    def get_inline_instances(self, request, obj=None):
        if obj is None or has_change_and_delete_permission(request, obj):
            return super(MenuAdmin, self).get_inline_instances(request, obj)
        return ()

    def save_model(self, request, obj, form, change):
        if not change and not request.user.is_superuser:
            obj.owner = request.user
        obj.save()


class TimeSlotInline(admin.TabularInline):
    model = MachineSet.menus.through
    extra = 1


class MachineSetAdmin(admin.ModelAdmin):
    inlines = [
        TimeSlotInline,
    ]

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser or obj is None:
            return []
        return ['name', 'owner', 'ip_ranges']

    def get_inline_instances(self, request, obj=None):
        if has_change_and_delete_permission(request, obj):
            return super(MachineSetAdmin, self).get_inline_instances(request,
                                                                     obj)
        return ()


class ItemAdmin(admin.ModelAdmin):
    prepopulated_fields = {'label': ('menu_label',)}
    fieldsets = (
        (None, {
            'fields': ('menu_label', 'kernel', 'initrd', 'append')
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('label', 'password', 'ipappend')
        })
    )


admin.site.register(Menu, MenuAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(MachineSet, MachineSetAdmin)
