from ..models import AJob


class TestJob(AJob):
    class Meta:
        app_label= 'TestApp'
