from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from ..models import GeographyReasons, OperatingGroups, IndustryGroups, DeliveryGroups, Accounts, DeliveryUnits, Projects



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
            return redirect('cxsuperuser:cx_su_update_list_capability')
        elif request.user.is_csguser:
            return redirect('csguser:capability_list')
        else:
            return redirect('clientuser:capability_list')
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

def load_operatinggroups(request):
    geographyreason_id = request.GET.get('geographyreason')
    operatinggroups = OperatingGroups.objects.filter(geographyreason_id=geographyreason_id).order_by('name')
    # operatinggroups = OperatingGroups.objects.filter(geographyreason_id=2).order_by('name')
    return render(request, 'registration/operatinggroup_dropdown_list_options.html', {'operatinggroups': operatinggroups})

def load_industrygroups(request):
    operatinggroup_id = request.GET.get('operatinggroup')
    industrygroups = IndustryGroups.objects.filter(operatinggroup_id=operatinggroup_id).order_by('name')
    # operatinggroups = OperatingGroups.objects.filter(geographyreason_id=2).order_by('name')
    return render(request, 'registration/industrygroup_dropdown_list_options.html', {'industrygroups': industrygroups})

def load_deliverygroups(request):
    industrygroup_id = request.GET.get('industrygroup')
    deliverygroups = DeliveryGroups.objects.filter(industrygroup_id=industrygroup_id).order_by('name')
    # operatinggroups = OperatingGroups.objects.filter(geographyreason_id=2).order_by('name')
    return render(request, 'registration/deliverygroup_dropdown_list_options.html', {'deliverygroups': deliverygroups})

def load_accounts(request):
    deliverygroup_id = request.GET.get('deliverygroup')
    accounts = Accounts.objects.filter(deliverygroup_id=deliverygroup_id).order_by('name')
    # operatinggroups = OperatingGroups.objects.filter(geographyreason_id=2).order_by('name')
    return render(request, 'registration/account_dropdown_list_options.html', {'accounts': accounts})

def load_deliveryunits(request):
    account_id = request.GET.get('account')
    deliveryunits = DeliveryUnits.objects.filter(account_id=account_id).order_by('name')
    # operatinggroups = OperatingGroups.objects.filter(geographyreason_id=2).order_by('name')
    return render(request, 'registration/deliveryunit_dropdown_list_options.html', {'deliveryunits': deliveryunits})

def load_projects(request):
    deliveryunit_id = request.GET.get('deliveryunit')
    projects = Projects.objects.filter(deliveryunit_id=deliveryunit_id).order_by('name')
    # operatinggroups = OperatingGroups.objects.filter(geographyreason_id=2).order_by('name')
    return render(request, 'registration/project_dropdown_list_options.html', {'projects': projects})
