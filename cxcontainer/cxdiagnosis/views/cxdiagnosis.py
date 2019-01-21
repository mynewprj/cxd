from django.shortcuts import redirect, render
from django.views.generic import TemplateView


# class SignUpView(TemplateView):
#     template_name = 'registration/signup.html'


def home(request):
    if request.user.is_authenticated:
        if request.user.is_cxsuperuser:
            return redirect('cxsuperuser:cx_su_capability_area_list')
        elif request.user.is_csguser:
            return redirect('csguser:csg_capability_area_list')
        else:
            return redirect('clientuser:capability_area_list')
    return render(request, 'home.html')
