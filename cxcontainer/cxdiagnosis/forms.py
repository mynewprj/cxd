from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from cxdiagnosis.models import (ClientUser, User, Domain)

# class ClientUserSignUpForm(UserCreationForm):
#     domain = forms.ModelChoiceField(
#         capabilityarea=ClientUser.objects.all(),
#         widget=forms.RadioSelect,
#         # required=True
#     )
class ClientUserSignUpForm(UserCreationForm):
    domains = forms.ModelMultipleChoiceField(
        queryset=Domain.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'password1', 'password2', 'email', 'domains')

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_clientuser = True
        user.save()
        clientuser = ClientUser.objects.create(user=user)
        clientuser.domains.add(*self.cleaned_data.get('domains'))
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
