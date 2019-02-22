from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.forms.utils import ValidationError

from cxdiagnosis.models import (ClientUser, User, Domain, Organisation, CxSuperUser, CsgUser, Question, Answer, MaturityLevel, ClientUserAnswer, CsgUserAnswer)


class ClientUserSignUpForm(UserCreationForm):
    domains = forms.ModelChoiceField(
        queryset=Domain.objects.all().order_by('name'),
        # widget=forms.Select,
        required=True
    )
    organisations = forms.ModelChoiceField(
        queryset=Organisation.objects.all().order_by('name'),
        # widget=forms.Select,
        required=True
    )
    username = forms.CharField(help_text=False)
    password1 = forms.CharField(widget=forms.PasswordInput, help_text=False)
    password2 = forms.CharField(widget=forms.PasswordInput, help_text=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'email', 'organisations', 'domains', 'username', 'password1', 'password2',)

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_clientuser = True
        user.save()
        clientuser = ClientUser.objects.create(user=user)
        clientuser.organisations = self.cleaned_data.get('organisations')
        clientuser.domains = self.cleaned_data.get('domains')
        clientuser.save()
        return user

class CsgUserSignUpForm(UserCreationForm):
    domains = forms.ModelChoiceField(
        queryset=Domain.objects.all().order_by('name'),
        # widget=forms.Select,
        required=True
    )
    organisations = forms.ModelChoiceField(
        queryset=Organisation.objects.all().order_by('name'),
        # widget=forms.Select,
        required=True
    )
    username = forms.CharField(help_text=False)
    password1 = forms.CharField(widget=forms.PasswordInput, help_text=False)
    password2 = forms.CharField(widget=forms.PasswordInput, help_text=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'email', 'organisations', 'domains', 'username', 'password1', 'password2',)

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        # user.is_clientuser = True
        user.is_csguser = True
        user.change_pass = True
        user.save()
        csguser = CsgUser.objects.create(user=user)
        csguser.organisations = self.cleaned_data.get('organisations')
        csguser.domains = self.cleaned_data.get('domains')
        csguser.save()
        return user

class CxSuperUserSignUpForm(UserCreationForm):
    domains = forms.ModelChoiceField(
        queryset=Domain.objects.all().order_by('name'),
        # widget=forms.Select,
        required=True
    )
    organisations = forms.ModelChoiceField(
        queryset=Organisation.objects.all().order_by('name'),
        # widget=forms.Select,
        required=True
    )
    username = forms.CharField(help_text=False)
    password1 = forms.CharField(widget=forms.PasswordInput, help_text=False)
    password2 = forms.CharField(widget=forms.PasswordInput, help_text=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'email', 'organisations', 'domains', 'username', 'password1', 'password2',)

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        # user.is_clientuser = True
        user.is_cxsuperuser = True
        user.change_pass = True
        user.save()
        cxsuperuser = CxSuperUser.objects.create(user=user)
        cxsuperuser.organisations = self.cleaned_data.get('organisations')
        cxsuperuser.domains = self.cleaned_data.get('domains')
        cxsuperuser.save()
        return user

class ClientUserDomainForm(forms.ModelForm):
    class Meta:
        model = ClientUser
        fields = ('domains', )

class QuestionForm(forms.ModelForm):
    weightage = forms.FloatField(required=True)

    class Meta:
        model = Question
        fields = ('text', 'weightage', )

class BaseAnswerInlineFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()

        maturitylevel = forms.ModelChoiceField(
            queryset=MaturityLevel.objects.all().order_by('name'),
            required=True
        )

class CompletedCapabilityForm(forms.ModelForm):
    answer = forms.ModelChoiceField(
        queryset=Answer.objects.none(),
        widget=forms.RadioSelect(),
        required=True,
        empty_label=None)

    class Meta:
        model = ClientUserAnswer
        fields = ('answer', )

    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question')
        super().__init__(*args, **kwargs)
        self.fields['answer'].queryset = question.answers.order_by('pk')

class CsgCompletedCapabilityForm(forms.ModelForm):
    answer = forms.ModelChoiceField(
        queryset=Answer.objects.none(),
        widget=forms.RadioSelect(),
        required=True,
        empty_label=None)

    class Meta:
        model = CsgUserAnswer
        fields = ('answer', )

    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question')
        super().__init__(*args, **kwargs)
        self.fields['answer'].queryset = question.answers.order_by('pk')
