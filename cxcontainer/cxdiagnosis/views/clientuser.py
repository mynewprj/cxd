import time
from django.views.generic import CreateView, ListView, UpdateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.db.models import Count
from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from ..models import ClientUser, User, Capability, CompletedCapability
from ..forms import ClientUserSignUpForm, CompletedCapabilityForm
from ..decorators import clientuser_required


class ClientUserSignUpView(CreateView):
    model = User
    form_class = ClientUserSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'clientuser'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        # return redirect('home')
        return redirect('clientuser:capability_list')

@method_decorator([login_required, clientuser_required], name='dispatch')
class CapabilityList(ListView):
    model = Capability
    ordering = ('name', )
    context_object_name = 'capabilities'
    template_name = 'clientuser/capability_list.html'
    # template_name = 'home.html'

    # def get_queryset(self):
    #     clientuser = self.request.user.clientuser
    #     clientuser_domains = clientuser.domains.values_list('pk', flat=True)
    #     clientuser_organisations = clientuser.organisations.values_list('pk', flat=True)
    #     result_of_capabilities = clientuser.capabilities.values_list('pk', flat=True)
    #     queryset = Capability.objects.filter(domain__in=clientuser_domains) \
    #         .filter(organisation__in=clientuser_organisations) \
    #         .exclude(pk__in=result_of_capabilities) \
    #         .annotate(questions_count=Count('questions')) \
    #         .filter(questions_count__gt=0)
    #     return queryset
