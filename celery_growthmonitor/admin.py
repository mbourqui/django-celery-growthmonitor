from abc import ABCMeta

from django.contrib import admin


class AJobAdmin(admin.ModelAdmin):
    __metaclass__ = ABCMeta

    fields = ('timestamp', 'identifier', 'state', 'status', 'duration', 'slug', 'closure')
    readonly_fields = ('timestamp', 'state', 'status', 'duration')
    list_display = ('__str__', 'timestamp', 'state', 'status', 'duration', 'closure')


class AFieldsForDataFileAdmin(admin.options.InlineModelAdmin):
    __metaclass__ = ABCMeta

    fields = ('data',)
    readonly_fields = ('data',)
    can_delete = False

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, *args, **kwargs):
        return False
