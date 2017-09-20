from abc import ABCMeta

from django.contrib import admin


class AJobAdmin(admin.ModelAdmin):
    __metaclass__ = ABCMeta

    # Change list specifications
    list_display = ('__str__', 'identifier', 'slug', 'timestamp', 'state', 'status', 'duration', 'closure')
    list_filter = ('timestamp', 'state', 'status', 'duration', 'closure')
    search_fields = ('identifier', 'slug')
    # Instance specifications
    fields = ('timestamp', 'identifier', 'state', 'status', 'duration', 'slug', 'closure')
    readonly_fields = ('timestamp', 'state', 'status', 'duration')

    def has_add_permission(self, request):
        return False


class AFieldsForDataFileInlineModelAdmin(admin.options.InlineModelAdmin):
    __metaclass__ = ABCMeta

    fields = ('data',)
    readonly_fields = ('data',)
    can_delete = False

    def has_add_permission(self, request):
        return False
