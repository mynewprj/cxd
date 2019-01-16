from django.urls import include, path
# from cxdiagnosis import views
from cxdiagnosis.views import cxdiagnosis, clientuser, csguser, cxsupperuser

urlpatterns = [
    path('', cxdiagnosis.home, name='home'),

    path('clientuser/', include(([
        path('', clientuser.CapabilityAreaList.as_view(), name='capability_area_list'),
        # path('domains/', clientuser.ClinetsDomain.as_view(), name='clinet_domains'),
        # path('result/', clientuser.ResultsOfCapabilityArea.as_view(), name='result_of_capability_area_list'),
        path('capabilityarea/<int:pk>/', clientuser.capability_area_quiz, name='capability_area_quiz'),
    ], 'cxdiagnosis'), namespace='clientuser')),

    path('hello/', clientuser.hello),
    path('clienthello/', clientuser.client_hello, name='clienthello'),

]
