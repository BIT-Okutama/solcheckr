from django.db import models
from django.utils.crypto import get_random_string


class TrackingMixin(object):
    def save(self, *args, **kwargs):
        if not self.tracking:
            rand_str = get_random_string()
            while self.__class__.objects.filter(tracking=rand_str).exists():
                rand_str = get_random_string()

            self.tracking = rand_str.strip()
        super().save(*args, **kwargs)


class Audit(TrackingMixin, models.Model):
    contract = models.TextField()
    report = models.TextField(blank=True, default='')
    result = models.NullBooleanField()
    submitted = models.DateTimeField(auto_now=True)
    tracking = models.CharField(max_length=100, null=True, blank=True)


class GithubAudit(TrackingMixin, models.Model):
    repo = models.CharField(max_length=200)
    contracts = models.TextField(blank=True, default='')
    report = models.TextField(blank=True, default='')
    result = models.NullBooleanField()
    submitted = models.DateTimeField(auto_now=True)
    tracking = models.CharField(max_length=100, null=True, blank=True)
