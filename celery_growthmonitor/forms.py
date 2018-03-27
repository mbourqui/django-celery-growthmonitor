import importlib
from abc import ABCMeta

from django import forms

crispy_forms = importlib.util.find_spec('crispy_forms')
if crispy_forms:
    from crispy_forms.helper import FormHelper


class ACrispyJobForm(forms.ModelForm):
    __metaclass__ = ABCMeta

    def __init__(self, *args, fix_initial=[], **kwargs):
        super(ACrispyJobForm, self).__init__(*args, **kwargs)
        for field in fix_initial:
            if 'instance' in kwargs and not ('initial' in kwargs and field in kwargs['initial']):
                # Fix instance overriding field with same name
                self.initial[field] = self.fields[field].initial
        if crispy_forms:
            self.helper = FormHelper()
            self.helper.form_tag = False
            self.helper.disable_csrf = True
