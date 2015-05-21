from django.db import models

class Problem(models.Model):
    pid = models.IntegerField(default=0)
    submits = models.IntegerField(default=0)

    def __unicode__(self):
        return '#{} - {}'.format(self.pid, self.submits)

class UserProfile(models.Model):
    uid = models.IntegerField(default=0)
    uname = models.CharField(max_length=200, default='noname')
    solved_problems = models.ManyToManyField(Problem, related_name='solved_problems')
    unsolved_problems = models.ManyToManyField(Problem, related_name='unsolved_problems')
    tcount = models.IntegerField(default=0)
    
    def __unicode__(self):
        return '%s' % self.uid
