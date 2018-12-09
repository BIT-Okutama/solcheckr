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


class BaseAuditModel(models.Model):
    report = models.TextField(blank=True, default='')
    result = models.NullBooleanField()
    submitted = models.DateTimeField(auto_now=True)
    tracking = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        abstract = True


class Audit(TrackingMixin, BaseAuditModel):
    contract = models.TextField()


class GithubAudit(TrackingMixin, BaseAuditModel):
    repo = models.CharField(max_length=200)
    contracts = models.TextField(blank=True, default='')


class ZipAudit(TrackingMixin, BaseAuditModel):
    contracts = models.TextField(blank=True, default='')
