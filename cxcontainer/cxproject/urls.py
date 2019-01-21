"""cxproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.urls import include, path
# from cxdiagnosis import views
from cxdiagnosis.views import cxdiagnosis, clientuser, cxsuperuser, csguser

urlpatterns = [
    path('', include('cxdiagnosis.urls')),
    path('cxaccounts/', include('django.contrib.auth.urls')),
    # path('cxaccounts/signup/', cxdiagnosis.SignUpView.as_view(), name='signup'),
    path('cxaccounts/client/signup/', clientuser.ClientUserSignUpView.as_view(), name='client_signup'),
    path('cxaccounts/csg/signup/', csguser.CsgUserSignUpView.as_view(), name='csg_signup'),
    path('cxaccounts/cxadmin/signup/', cxsuperuser.CxSuperUserSignUpView.as_view(), name='cxsuper_signup'),

]
