from django.db import models


class BaseAuditModel(models.Model):
    report = models.TextField(blank=True, default='')
    result = models.NullBooleanField()
    submitted = models.DateTimeField(auto_now=True)
    tracking = models.CharField(max_length=100)
    author = models.CharField(max_length=100)

    class Meta:
        abstract = True


class Audit(BaseAuditModel):
    contract = models.TextField()


class GithubAudit(BaseAuditModel):
    repo = models.CharField(max_length=200)
    contracts = models.TextField(blank=True, default='')


class ZipAudit(BaseAuditModel):
    contracts = models.TextField(blank=True, default='')
