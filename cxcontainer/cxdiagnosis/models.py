from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.html import escape, mark_safe

# Create your models here.
class User(AbstractUser):
    is_clientuser = models.BooleanField(default=False)
    is_csguser = models.BooleanField(default=False)
    is_cxsuperuser = models.BooleanField(default=False)
    change_pass = models.BooleanField(default=False)

class Domain(models.Model):
    name = models.CharField(max_length=30)

    def get_html_badge(self):
        name = escape(self.name)
        html = '<span class="badge badge-primary">%s</span>' % (name)
        return mark_safe(html)

    def __str__(self):
        return self.name

class Organisation(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Capability(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='capabilities')
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Question(models.Model):
    capability = models.ForeignKey(Capability, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField('Question', max_length=300)
    weightage = models.FloatField()

    def __str__(self):
        return self.text

class MaturityLevel(models.Model):
    name = models.CharField('MaturityLevel', max_length=10)
    score = models.FloatField()

    def __str__(self):
        return self.name

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    maturitylevel = models.ForeignKey(MaturityLevel, on_delete=models.CASCADE, related_name='maturitylevels')
    text = models.CharField('Answer', max_length=600)
    # is_correct = models.BooleanField('Correct answer', default=False)

    def __str__(self):
        return self.text

class ClientUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    capabilities = models.ManyToManyField(Capability, through='CompletedCapability')
    domains = models.ForeignKey(Domain, on_delete=models.SET_NULL, null=True, related_name='domains_clientusers')
    organisations = models.ForeignKey(Organisation, on_delete=models.SET_NULL, null=True)

    def get_unanswered_questions(self, capability):
        answered_questions = self.capability_answers \
            .filter(answer__question__capability=capability) \
            .values_list('answer__question__pk', flat=True)
        questions = capability.questions.exclude(pk__in=answered_questions).order_by('text')
        return questions

    def __str__(self):
        return self.user.username

class CsgUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    # capabilities = models.ManyToManyField(Capability, through='ResultsOfCapability')
    domains = models.ForeignKey(Domain, on_delete=models.SET_NULL, null=True)
    organisations = models.ForeignKey(Organisation, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.user.username

class CxSuperUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    domains = models.ForeignKey(Domain, on_delete=models.SET_NULL, null=True)
    organisations = models.ForeignKey(Organisation, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.user.username

class CompletedCapability(models.Model):
    clientuser = models.ForeignKey(ClientUser, on_delete=models.CASCADE, related_name='completed_capabilities')
    capability = models.ForeignKey(Capability, on_delete=models.CASCADE, related_name='completed_capabilities')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='completed_capabilities')
    score = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)


class ClientUserAnswer(models.Model):
    clientuser = models.ForeignKey(ClientUser, on_delete=models.CASCADE, related_name='capability_answers')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='+')
