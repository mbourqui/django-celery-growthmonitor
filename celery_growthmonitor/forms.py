import importlib
from abc import ABCMeta

from django import forms
from django.utils.translation import ugettext_lazy as _

crispy_forms = importlib.util.find_spec("crispy_forms")
if crispy_forms:
    from crispy_forms.helper import FormHelper
    from crispy_forms.layout import Layout, Hidden, Submit


class ACrispyJobForm(forms.ModelForm):
    __metaclass__ = ABCMeta

    def __init__(self, *args, fix_initial=[], **kwargs):
        super(ACrispyJobForm, self).__init__(*args, **kwargs)
        for field in fix_initial:
            if "instance" in kwargs and not (
                "initial" in kwargs and field in kwargs["initial"]
            ):
                # Fix instance overriding field with same name
                self.initial[field] = self.fields[field].initial
        if crispy_forms:
            self.helper = FormHelper()
            self.helper.form_tag = False
            self.helper.disable_csrf = True


class ACrispyJobSubmissionForm(forms.Form):
    __metaclass__ = ABCMeta

    # TODO if needed: use identifier from CombineJob

    def __init__(self, *args, add_honeypot=False, **kwargs):
        super(ACrispyJobSubmissionForm, self).__init__(*args, **kwargs)
        if crispy_forms:
            self.helper = FormHelper()
            self.helper.form_tag = False
            self.helper.disable_csrf = True
            if add_honeypot:
                from django.conf import settings

                self.helper.add_input(
                    Hidden(settings.HONEYPOT_FIELD_NAME, settings.HONEYPOT_VALUE)
                )
            self.helper.layout = Layout(
                # Job identifier could be asked here
                Submit("submit", _("Submit"), css_class="btn-submit",),
            )
