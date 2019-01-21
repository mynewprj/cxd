from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm



# class SignUpView(TemplateView):
#     template_name = 'registration/signup.html'

def check_first(request):
    if request.user.change_pass:
        return redirect('change_password')
    else:
        return redirect('home')

def home(request):
    if request.user.is_authenticated:
        if request.user.is_cxsuperuser:
            return redirect('cxsuperuser:cx_su_capability_area_list')
        elif request.user.is_csguser:
            return redirect('csguser:csg_capability_area_list')
        else:
            return redirect('clientuser:capability_area_list')
    return render(request, 'home.html')

def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            if request.user.change_pass:
                request.user.change_pass = '0'
                user = form.save()
            return redirect('home')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/change_password.html', {'form': form})
