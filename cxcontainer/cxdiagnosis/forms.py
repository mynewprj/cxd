from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.forms.utils import ValidationError

from cxdiagnosis.models import (ClientUser, User, Domain, Organisation)

# class ClientUserSignUpForm(UserCreationForm):
#     domain = forms.ModelChoiceField(
#         capabilityarea=ClientUser.objects.all(),
#         widget=forms.RadioSelect,
#         # required=True
#     )
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

# from django import forms
# from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User
#
#
# class SignUpForm(UserCreationForm):
#     email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
#
#     class Meta:
#         model = User
#         fields = ('username', 'email', 'password1', 'password2', )
