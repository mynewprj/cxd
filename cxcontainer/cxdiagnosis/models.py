from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.html import escape, mark_safe

# Create your models here.
class User(AbstractUser):
    is_clientuser = models.BooleanField(default=False)
    is_csguser = models.BooleanField(default=False)
    is_cxsuperuser = models.BooleanField(default=False)
    change_pass = models.BooleanField(default=False)

class GeographyReasons(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class OperatingGroups(models.Model):
    name = models.CharField(max_length=50)
    geographyreason = models.ForeignKey(GeographyReasons, on_delete=models.SET_NULL, null=True, related_name='geographyreasons_operatinggroups')

    def __str__(self):
        return self.name

class IndustryGroups(models.Model):
    name = models.CharField(max_length=50)
    operatinggroup = models.ForeignKey(OperatingGroups, on_delete=models.SET_NULL, null=True, related_name='operatinggroups_industrygroups')

    def __str__(self):
        return self.name

class DeliveryGroups(models.Model):
    name = models.CharField(max_length=50)
    industrygroup = models.ForeignKey(IndustryGroups, on_delete=models.SET_NULL, null=True, related_name='industrygroups_deliverygroups')

    def __str__(self):
        return self.name

class Accounts(models.Model):
    name = models.CharField(max_length=50)
    deliverygroup = models.ForeignKey(DeliveryGroups, on_delete=models.SET_NULL, null=True, related_name='deliverygroups_accounts')

    def __str__(self):
        return self.name

class DeliveryUnits(models.Model):
    name = models.CharField(max_length=50)
    account = models.ForeignKey(Accounts, on_delete=models.SET_NULL, null=True, related_name='accounts_deliveryunits')

    def __str__(self):
        return self.name

class Projects(models.Model):
    name = models.CharField(max_length=50)
    deliveryunit = models.ForeignKey(DeliveryUnits, on_delete=models.SET_NULL, null=True, related_name='deliveryunits_projects')

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
    geographyreason = models.ForeignKey(GeographyReasons, on_delete=models.SET_NULL, null=True, related_name='geographyreasons_clientusers')
    operatinggroup = models.ForeignKey(OperatingGroups, on_delete=models.SET_NULL, null=True, related_name='operatinggroups_clientusers')
    industrygroup = models.ForeignKey(IndustryGroups, on_delete=models.SET_NULL, null=True, related_name='industrygroups_clientusers')
    deliverygroup = models.ForeignKey(DeliveryGroups, on_delete=models.SET_NULL, null=True, related_name='deliverygroups_clientusers')
    account = models.ForeignKey(Accounts, on_delete=models.SET_NULL, null=True, related_name='accounts_clientusers')
    deliveryunit = models.ForeignKey(DeliveryUnits, on_delete=models.SET_NULL, null=True, related_name='deliveryunits_clientusers')
    project = models.ForeignKey(Projects, on_delete=models.SET_NULL, null=True, related_name='projects_clientusers')
    capabilities = models.ManyToManyField(Capability, through='CompletedCapability')

    def get_unanswered_questions(self, capability):
        answered_questions = self.capability_answers \
            .filter(answer__question__capability=capability) \
            .values_list('answer__question__pk', flat=True)
        questions = capability.questions.exclude(pk__in=answered_questions).order_by('pk')
        return questions

    def get_answered_questions(self, capability):
        unanswered_questions = self.get_unanswered_questions(capability)
        questions = capability.questions.exclude(pk__in=unanswered_questions).order_by('pk')
        return questions

    def __str__(self):
        return self.user.username

class CsgUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    capabilities = models.ManyToManyField(Capability, through='CsgCompletedCapability')
    geographyreason = models.ForeignKey(GeographyReasons, on_delete=models.SET_NULL, null=True, related_name='geographyreasons_csguser')

    def get_unanswered_questions(self, capability):
        answered_questions = self.csg_capability_answers \
            .filter(answer__question__capability=capability) \
            .values_list('answer__question__pk', flat=True)
        questions = capability.questions.exclude(pk__in=answered_questions).order_by('pk')
        return questions

    def get_answered_questions(self, capability):
        unanswered_questions = self.get_unanswered_questions(capability)
        questions = capability.questions.exclude(pk__in=unanswered_questions).order_by('pk')
        return questions

    def __str__(self):
        return self.user.username

class CxSuperUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    geographyreason = models.ForeignKey(GeographyReasons, on_delete=models.SET_NULL, null=True, related_name='geographyreasons_cxsuperuser')

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

class CsgCompletedCapability(models.Model):
    csguser = models.ForeignKey(CsgUser, on_delete=models.CASCADE, related_name='csg_completed_capabilities')
    capability = models.ForeignKey(Capability, on_delete=models.CASCADE, related_name='csg_completed_capabilities')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='csg_completed_capabilities')
    score = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)

class CsgUserAnswer(models.Model):
    csguser = models.ForeignKey(CsgUser, on_delete=models.CASCADE, related_name='csg_capability_answers')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='+')
