import base64
import zlib

from django.db import models
from django.utils.crypto import get_random_string

STATUS_CHOICES = ((1, 'Finished'), (2, 'Error'), (3, 'Expired'),
                  (4, 'Performing'), (5, 'Queued'))


class Audit(models.Model):
    email = models.EmailField(null=True, blank=True)
    contract = models.TextField()
    report = models.TextField(blank=True, default='')
    result = models.NullBooleanField()
    submitted = models.DateTimeField(auto_now=True)
    status = models.PositiveIntegerField(default=5, choices=STATUS_CHOICES)
    tracking = models.CharField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.tracking:
            rand_str = get_random_string()
            while self.__class__.objects.filter(tracking=rand_str).exists():
                rand_str = get_random_string()

            self.tracking = rand_str.strip()
        super().save(*args, **kwargs)
