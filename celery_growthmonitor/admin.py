from abc import ABCMeta

from django.contrib import admin


class AJobAdmin(admin.ModelAdmin):
    __metaclass__ = ABCMeta

    # Change list specifications
    list_display = ('__str__', 'user', 'identifier', 'slug', 'timestamp', 'state', 'status', 'duration', 'closure')
    list_filter = ('user', 'timestamp', 'state', 'status', 'closure')
    search_fields = ('user', 'identifier', 'slug')
    # Instance specifications
    fields = ('user', 'timestamp', 'identifier', 'slug', 'state', 'status', 'duration', 'closure', 'error')
    readonly_fields = ('user', 'timestamp', 'state', 'status', 'duration', 'error')

    def has_add_permission(self, request):
        return False


class AFieldsForDataFileInlineModelAdmin(admin.options.InlineModelAdmin):
    __metaclass__ = ABCMeta

    fields = ('data',)
    readonly_fields = ('data',)
    can_delete = False

    def has_add_permission(self, request):
        return False
