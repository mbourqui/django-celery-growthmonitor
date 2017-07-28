from abc import ABCMeta

from django.contrib import admin


class AJobAdmin(admin.ModelAdmin):
    __metaclass__ = ABCMeta

    fields = ('timestamp', 'identifier', 'state', 'status', 'duration', 'slug', 'closure')
    readonly_fields = ('timestamp', 'state', 'status', 'duration')
