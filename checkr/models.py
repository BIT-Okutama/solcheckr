from django.db import models


STATUS_CHOICES = ((1, 'Finished'), (2, 'Error'), (3, 'Expired'),
                  (4, 'Performing'), (5, 'Queued'))


class Audit(models.Model):
    email = models.EmailField()
    contract = models.TextField()
    report = models.TextField(blank=True, default='')
    submitted = models.DateTimeField(auto_now=True)
    status = models.PositiveIntegerField(default=5, choices=STATUS_CHOICES)
