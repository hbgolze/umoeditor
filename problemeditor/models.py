from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.
STATUS_CHOICES = (
    ('NP', 'New Problem'),
    ('PN', 'Propose for Current Year'),
    ('PL', 'Propose for Future Year'),
    ('MI', 'Has Potential'),
    ('MJ', 'Needs Major Revision'),
    ('TR', 'Trash'),
    )

class StatusTopic(models.Model):
    topic = models.CharField(max_length=20,blank=True)
    short_topic = models.CharField(max_length=2,blank=True)
    status = models.CharField(max_length = 2,blank = True)
    status_description = models.CharField(max_length = 30,blank = True)
    order = models.IntegerField()
    def __str__(self):
        return self.status_description + ": " + self.topic
    class Meta:
        ordering = ['order','topic']

class Topic(models.Model):
    topic = models.CharField(max_length=20,blank=True)
    short_topic = models.CharField(max_length=2,blank=True)
    def __str__(self):
        return self.topic

class ProblemStatus(models.Model):
    status = models.CharField(max_length = 2,blank = True)
    description = models.CharField(max_length = 30,blank = True)
    def __str__(self):
        return self.description

class Solution(models.Model):
    solution_text = models.TextField()
    solution_latex = models.TextField()
    solution_number = models.IntegerField(default=1)
    problem_label = models.CharField(max_length=20,blank=True)
    authors = models.ManyToManyField(User,blank=True)
    author_name = models.CharField(max_length=50,blank=True)
    created_date = models.DateTimeField(default = timezone.now)
    def __str__(self):
        return self.problem_label+' sol '+str(self.solution_number)+str(self.authors.all())

class Comment(models.Model):
    comment_text = models.TextField()
    problem_label = models.CharField(max_length=20,blank=True)
    comment_number = models.IntegerField(default=1)
    author = models.ForeignKey(User,blank=True,null=True,on_delete=models.SET_NULL)
    author_name = models.CharField(max_length=50,blank=True)
    created_date = models.DateTimeField(default = timezone.now)
    def __str__(self):
        return self.problem_label+' comment '+str(self.created_date)+', '+str(self.author)

class ProblemVersion(models.Model):
    DIFFICULTY_CHOICES = (
        ('1','1'),
        ('2','2'),
        ('3','3'),
        ('4','4'),
        ('5','5'),
        ('6','6'),
        )
    difficulty = models.CharField(max_length = 1,choices=DIFFICULTY_CHOICES,blank=False,default='1')
    problem_text = models.TextField(blank=True)
    problem_latex = models.TextField(blank=True)
    solutions = models.ManyToManyField(Solution,blank=True)
    deleted_solutions = models.ManyToManyField(Solution,blank=True,related_name="deleted_solutions")
    top_solution_number = models.IntegerField(default=0)
    version_number = models.IntegerField(default=0)
    author_name = models.CharField(max_length=50,blank=True)
    created_date = models.DateTimeField(default = timezone.now)
    label = models.CharField(max_length=20,blank=True)
    authors = models.ManyToManyField(User,blank=True)

class Problem(models.Model):
    topic_new = models.ForeignKey(Topic,blank=True,null=True,on_delete=models.SET_NULL)
    problem_status_new = models.ForeignKey(ProblemStatus,blank=True,null=True,on_delete=models.SET_NULL)
    TOPIC_CHOICES = (
        ('Algebra','Algebra'),
        ('Combinatorics','Combinatorics'),
        ('Games','Games'),
        ('Geometry','Geometry'),
        ('Number Theory','Number Theory'),
        ('Other','Other'),
        )
    topic = models.CharField(max_length = 20,choices=TOPIC_CHOICES,blank=False,default='Algebra')
    DIFFICULTY_CHOICES = (
        ('1','1'),
        ('2','2'),
        ('3','3'),
        ('4','4'),
        ('5','5'),
        ('6','6'),
        )
    difficulty = models.CharField(max_length = 1,choices=DIFFICULTY_CHOICES,blank=False,default='1')
    label = models.CharField(max_length=20)
    problem_text = models.TextField(blank=True)
    problem_latex = models.TextField(blank=True)
    solutions = models.ManyToManyField(Solution,blank=True)
    top_solution_number = models.IntegerField(default=0)
#    author = models.ForeignKey(User,related_name='author',blank=True,null=True)
    author_name = models.CharField(max_length=50,blank=True)
    created_date = models.DateTimeField(default = timezone.now)
    comments = models.ManyToManyField(Comment,blank=True)
    problem_status = models.CharField(max_length=2,default='NP')#ManyToManyField(ProblemStatus,blank=True)
    versions = models.ManyToManyField(ProblemVersion,blank=True,related_name='problem_version')
    top_version_number = models.IntegerField(default=0)
    current_version = models.ForeignKey(ProblemVersion,blank=True,related_name='current_version', null=True,on_delete = models.SET_NULL)
    status_topic = models.ForeignKey(StatusTopic,blank=True, related_name="problems", null=True,on_delete=models.SET_NULL)
    def __str__(self):
        return self.label
    def publish_it(self):
        self.problem_status = 'XX'
        self.problem_status_new = ProblemStatus.objects.get(status = "XX")
        self.topic_new = Topic.objects.get(topic = self.topic)
        self.status_topic = StatusTopic.objects.get(status = 'XX',topic = self.topic)
        self.save()

class FinalTest(models.Model):
    problems=models.ManyToManyField(Problem,blank=True)
    year = models.CharField(max_length=4)
    def __str__(self):
        return self.year+' UMO'
#Probably useless
class UserProfile(models.Model):
    # This line is required. Links UserProfile to a User model instance.
    user = models.OneToOneField(User,null=True,on_delete=models.SET_NULL)
    def __unicode__(self):
        return self.user.username

class ShortList(models.Model):
    problems = models.ManyToManyField(Problem, blank=True)
    name = models.CharField(max_length=50)
    archived = models.BooleanField(default=False)
    created_date = models.DateTimeField(default = timezone.now)
    author = models.ForeignKey(User,blank=True,null=True,on_delete=models.SET_NULL)
    def __str__(self):
        return self.name

def get_or_create_up(user):
    userprofile,boolcreated=UserProfile.objects.get_or_create(user=user)
    if boolcreated==False:
        userprofile.save()
    return userprofile
