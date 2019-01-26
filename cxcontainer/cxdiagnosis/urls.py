from django.urls import include, path
# from cxdiagnosis import views
from cxdiagnosis.views import cxdiagnosis, clientuser, csguser, cxsuperuser

urlpatterns = [
    path('', cxdiagnosis.home, name='home'),
    path('passwd/', cxdiagnosis.change_password, name='change_password'),
    path('changeit/', cxdiagnosis.check_first, name='check_first'),

    path('clientuser/', include(([
        path('', clientuser.CapabilityList.as_view(), name='capability_list'),
        # path('domains/', clientuser.ClinetsDomain.as_view(), name='clinet_domains'),
        # path('result/', clientuser.ResultsOfCapability.as_view(), name='result_of_capability_list'),
        # path('capability/<int:pk>/', clientuser.capability, name='capability'),
    ], 'cxdiagnosis'), namespace='clientuser')),

    path('csguser/', include(([
        path('', csguser.CsgCapabilityList.as_view(), name='csg_capability_list'),
    ], 'cxdiagnosis'), namespace='csguser')),

    path('cxsuperuser/', include(([
        path('', cxsuperuser.CxSuCapabilityList.as_view(), name='cx_su_update_list_capability'),
        path('capability/new/', cxsuperuser.CreateCapabilityView.as_view(), name='cx_su_new_capability'),
        path('capability/<int:pk>/', cxsuperuser.UpdateCapabilityView.as_view(), name='cx_su_update_capability'),
        path('capability/<int:pk>/completed/', cxsuperuser.CompletedCapabilityView.as_view(), name='cx_su_completed_capability'),
        path('capability/<int:pk>/delete/', cxsuperuser.DeleteCapabilityView.as_view(), name='cx_su_delete_capability'),
        path('capability/<int:pk>/question/add/', cxsuperuser.question_add, name='question_add'),
        path('capability/<int:capability_pk>/question/<int:question_pk>/', cxsuperuser.question_change, name='question_change'),
        path('capability/<int:capability_pk>/question/<int:question_pk>/delete/', cxsuperuser.QuestionDeleteView.as_view(), name='question_delete'),
    ], 'cxdiagnosis'), namespace='cxsuperuser')),

]
