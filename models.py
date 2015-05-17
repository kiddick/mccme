from django.db import models


class Problem(models.Model):
    pid = models.IntegerField(default=0)
    submits = models.IntegerField(default=0)

    def __unicode__(self):
        return '#{} - {}'.format(self.pid, self.submits)
