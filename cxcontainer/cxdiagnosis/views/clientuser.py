import time
from django.views.generic import CreateView, ListView, UpdateView
from ..models import ClientUser, User, CapabilityArea
from ..forms import ClientUserSignUpForm
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from ..decorators import clientuser_required
from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.db.models import Count

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
        return redirect('clientuser:capability_area_list')

@method_decorator([login_required, clientuser_required], name='dispatch')
class CapabilityAreaList(ListView):
    model = CapabilityArea
    ordering = ('name', )
    context_object_name = 'capabilityareas'
    template_name = 'clientuser/capability_area_list.html'
    # template_name = 'home.html'

    def get_queryset(self):
        clientuser = self.request.user.clientuser
        clientuser_domains = clientuser.domains.values_list('pk', flat=True)
        result_of_capability_areas = clientuser.capabilityareas.values_list('pk', flat=True)
        queryset = CapabilityArea.objects.filter(domain__in=clientuser_domains) \
            .exclude(pk__in=result_of_capability_areas) \
            .annotate(questions_count=Count('questions')) \
            .filter(questions_count__gt=0)
        return queryset

@login_required
@clientuser_required
def capability_area_quiz(request, pk):
    capability_area_quiz = get_object_or_404(Quiz, pk=pk)
    clientuser = request.user.clientuser

    # if clientuser.capabilityareas.filter(pk=pk).exists():
        # return render(request, 'students/capability_area_quiz.html')
    return render(request, 'clientuser/capability_area_quiz.html')


# Create your views here.
from django.http import HttpResponse, HttpResponseNotFound
def hello(request):
    return HttpResponse("<h2>Hello, Welcome to Django!</h2>")
def client_user(request):
    return render(request, "clientuser/client.html")
def client_hello(request):
   now=time.strftime("%d/%m/%Y %H:%M:%S")
   return render(request, "clientuser/clienthello.html", {"today" : now})
