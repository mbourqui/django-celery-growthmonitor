from abc import ABCMeta

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _


class AJobAdmin(admin.ModelAdmin):
    __metaclass__ = ABCMeta

    # Change list specifications
    list_display = (
        "__str__",
        "identifier",
        "slug",
        "timestamp",
        "state",
        "status",
        "duration",
        "closure",
    )
    list_filter = ("timestamp", "state", "status", "closure")
    search_fields = ("identifier", "slug")
    # Instance specifications
    fields = (
        "timestamp",
        "identifier",
        "slug",
        "state",
        "status",
        "duration",
        "closure",
        "error",
    )
    readonly_fields = ("timestamp", "state", "status", "duration", "error")

    def has_add_permission(self, request):
        return False


class AFieldsForDataFileInlineModelAdmin(admin.options.InlineModelAdmin):
    __metaclass__ = ABCMeta

    fields = ("data",)
    readonly_fields = ("data",)
    can_delete = False

    def has_add_permission(self, request):
        return False


class HasJobAdminMixin:
    app_label = None
    job_model = None
    job_label = _("Job")

    list_display = ("render_job",)
    list_filter = ()
    search_fields = ("render_job",)
    fields = ("job_link",)
    readonly_fields = ("job_link",)

    def render_job(self, obj):
        return str(obj.job)

    render_job.short_description = job_label

    def job_link(self, obj):
        url = reverse(
            "admin:{}_{}_change".format(
                self.app_label, self.job_model.__name__.lower()
            ),
            args=(obj.job.pk,),
        )
        return format_html('<a href="%s">%s</a>' % (url, self.render_job(obj)))

    job_link.short_description = job_label
