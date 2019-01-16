from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.html import escape, mark_safe

# Create your models here.
class User(AbstractUser):
    is_clientuser = models.BooleanField(default=False)
    is_csguser = models.BooleanField(default=False)
    is_cxsuperuser = models.BooleanField(default=False)

class Domain(models.Model):
    name = models.CharField(max_length=30)
    # color = models.CharField(max_length=7, default='#007bff')

    def get_html_badge(self):
        name = escape(self.name)
        html = '<span class="badge badge-primary">%s</span>' % (name)
        return mark_safe(html)

    def __str__(self):
        return self.name

class CapabilityArea(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='capabilityareas')
    name = models.CharField(max_length=255)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, related_name='capabilityareas')

    def __str__(self):
        return self.name

class Question(models.Model):
    capabilityarea = models.ForeignKey(CapabilityArea, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField('Question', max_length=255)

    def __str__(self):
        return self.text

class ClientUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    capabilityareas = models.ManyToManyField(CapabilityArea, through='ResultsOfCapabilityArea')
    domains = models.ManyToManyField(Domain, related_name='clientuser_domains')

    # def get_unanswered_questions(self, quiz):
    #     answered_questions = self.quiz_answers \
    #         .filter(answer__question__quiz=quiz) \
    #         .values_list('answer__question__pk', flat=True)
    #     questions = quiz.questions.exclude(pk__in=answered_questions).order_by('text')
    #     return questions

    def __str__(self):
        return self.user.username

class ResultsOfCapabilityArea(models.Model):
    clientuser = models.ForeignKey(ClientUser, on_delete=models.CASCADE, related_name='result_of_capability_areas')
    capabilityarea = models.ForeignKey(CapabilityArea, on_delete=models.CASCADE, related_name='result_of_capability_areas')
    score = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)
