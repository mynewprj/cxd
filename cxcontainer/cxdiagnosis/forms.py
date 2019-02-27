from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.forms.utils import ValidationError

from cxdiagnosis.models import (ClientUser, User, GeographyReasons, OperatingGroups, IndustryGroups, DeliveryGroups, Accounts, DeliveryUnits, Projects, CxSuperUser, CsgUser, Question, Answer, MaturityLevel, ClientUserAnswer, CsgUserAnswer)


class ClientUserSignUpForm(UserCreationForm):
    geographyreason = forms.ModelChoiceField(
        queryset=GeographyReasons.objects.all().order_by('name'),
        # widget=forms.Select,
        required=True
    )
    operatinggroup = forms.ModelChoiceField(
        queryset=OperatingGroups.objects.all().order_by('name'),
        # widget=forms.Select,
        required=True
    )
    industrygroup = forms.ModelChoiceField(
        queryset=IndustryGroups.objects.all().order_by('name'),
        # widget=forms.Select,
        required=True
    )
    deliverygroup = forms.ModelChoiceField(
        queryset=DeliveryGroups.objects.all().order_by('name'),
        # widget=forms.Select,
        required=True
    )
    account = forms.ModelChoiceField(
        queryset=Accounts.objects.all().order_by('name'),
        # widget=forms.Select,
        required=True
    )
    deliveryunit = forms.ModelChoiceField(
        queryset=DeliveryUnits.objects.all().order_by('name'),
        # widget=forms.Select,
        required=True
    )
    project = forms.ModelChoiceField(
        queryset=Projects.objects.all().order_by('name'),
        # widget=forms.Select,
        required=True
    )
    username = forms.CharField(help_text=False)
    password1 = forms.CharField(widget=forms.PasswordInput, help_text=False)
    password2 = forms.CharField(widget=forms.PasswordInput, help_text=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'email', 'geographyreason', 'operatinggroup', 'industrygroup', 'deliverygroup', 'account', 'deliveryunit', 'project', 'username', 'password1', 'password2',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['operatinggroup'].queryset = OperatingGroups.objects.none()
        self.fields['industrygroup'].queryset = OperatingGroups.objects.none()
        self.fields['deliverygroup'].queryset = OperatingGroups.objects.none()
        self.fields['account'].queryset = OperatingGroups.objects.none()
        self.fields['deliveryunit'].queryset = OperatingGroups.objects.none()
        self.fields['project'].queryset = OperatingGroups.objects.none()

        if 'geographyreason' in self.data:
            try:
                geographyreason_id = int(self.data.get('geographyreason'))
                self.fields['operatinggroup'].queryset = OperatingGroups.objects.filter(geographyreason_id=geographyreason_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty operatinggroup queryset
        elif self.instance.pk:
            self.fields['operatinggroup'].queryset = self.instance.geographyreason.operatinggroup_set.order_by('name')

        if 'operatinggroup' in self.data:
            try:
                operatinggroup_id = int(self.data.get('operatinggroup'))
                self.fields['industrygroup'].queryset = IndustryGroups.objects.filter(operatinggroup_id=operatinggroup_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty industrygroup queryset
        elif self.instance.pk:
            self.fields['industrygroup'].queryset = self.instance.operatinggroup.industrygroup_set.order_by('name')

        if 'industrygroup' in self.data:
            try:
                industrygroup_id = int(self.data.get('industrygroup'))
                self.fields['deliverygroup'].queryset = DeliveryGroups.objects.filter(industrygroup_id=industrygroup_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty deliverygroup queryset
        elif self.instance.pk:
            self.fields['deliverygroup'].queryset = self.instance.industrygroup.deliverygroup_set.order_by('name')

        if 'deliverygroup' in self.data:
            try:
                deliverygroup_id = int(self.data.get('deliverygroup'))
                self.fields['account'].queryset = Accounts.objects.filter(deliverygroup_id=deliverygroup_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty account queryset
        elif self.instance.pk:
            self.fields['account'].queryset = self.instance.deliverygroup.account_set.order_by('name')

        if 'account' in self.data:
            try:
                account_id = int(self.data.get('account'))
                self.fields['deliveryunit'].queryset = DeliveryUnits.objects.filter(account_id=account_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty deliveryunit queryset
        elif self.instance.pk:
            self.fields['deliveryunit'].queryset = self.instance.account.deliveryunit_set.order_by('name')

        if 'deliveryunit' in self.data:
            try:
                deliveryunit_id = int(self.data.get('deliveryunit'))
                self.fields['project'].queryset = Projects.objects.filter(deliveryunit_id=deliveryunit_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty project queryset
        elif self.instance.pk:
            self.fields['project'].queryset = self.instance.deliveryunit.project_set.order_by('name')

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_clientuser = True
        user.save()
        clientuser = ClientUser.objects.create(user=user)
        clientuser.geographyreason = self.cleaned_data.get('geographyreason')
        clientuser.operatinggroup = self.cleaned_data.get('operatinggroup')
        clientuser.industrygroup = self.cleaned_data.get('industrygroup')
        clientuser.deliverygroup = self.cleaned_data.get('deliverygroup')
        clientuser.account = self.cleaned_data.get('account')
        clientuser.deliveryunit = self.cleaned_data.get('deliveryunit')
        clientuser.project = self.cleaned_data.get('project')
        clientuser.save()
        return user

class CsgUserSignUpForm(UserCreationForm):
    geographyreason = forms.ModelChoiceField(
        queryset=GeographyReasons.objects.all().order_by('name'),
        # widget=forms.Select,
        required=True
    )
    username = forms.CharField(help_text=False)
    password1 = forms.CharField(widget=forms.PasswordInput, help_text=False)
    password2 = forms.CharField(widget=forms.PasswordInput, help_text=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'email', 'geographyreason', 'username', 'password1', 'password2',)

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        # user.is_clientuser = True
        user.is_csguser = True
        user.change_pass = True
        user.save()
        csguser = CsgUser.objects.create(user=user)
        csguser.geographyreason = self.cleaned_data.get('geographyreason')
        csguser.save()
        return user

class CxSuperUserSignUpForm(UserCreationForm):
    geographyreason = forms.ModelChoiceField(
        queryset=GeographyReasons.objects.all().order_by('name'),
        # widget=forms.Select,
        required=True
    )
    username = forms.CharField(help_text=False)
    password1 = forms.CharField(widget=forms.PasswordInput, help_text=False)
    password2 = forms.CharField(widget=forms.PasswordInput, help_text=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'email', 'geographyreason', 'username', 'password1', 'password2',)

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        # user.is_clientuser = True
        user.is_cxsuperuser = True
        user.change_pass = True
        user.save()
        cxsuperuser = CxSuperUser.objects.create(user=user)
        cxsuperuser.geographyreason = self.cleaned_data.get('geographyreason')
        cxsuperuser.save()
        return user

# class ClientUserDomainForm(forms.ModelForm):
#     class Meta:
#         model = ClientUser
#         fields = ('domains', )

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
