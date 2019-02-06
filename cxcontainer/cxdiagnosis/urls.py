from django.urls import include, path
# from cxdiagnosis import views
from cxdiagnosis.views import cxdiagnosis, clientuser, csguser, cxsuperuser
# from django.conf.urls.import url, patterns

urlpatterns = [
    path('', cxdiagnosis.home, name='home'),
    path('passwd/', cxdiagnosis.change_password, name='change_password'),
    path('changeit/', cxdiagnosis.check_first, name='check_first'),

    path('clientuser/', include(([
        path('', clientuser.CapabilityListView.as_view(), name='capability_list'),
        path('domains/', clientuser.ClientUserDomainView.as_view(),
             name='clientuser_domains'),
        path('completed/', clientuser.CompletedCapabilitylistView.as_view(),
             name='completed_capability_list'),
        path('downloadpdf/<int:pk>/', clientuser.write_pdf_view,
             name='download_pdf'),
        path('capability/<int:pk>/', clientuser.completed_capability,
             name='completed_capability'),
    ], 'cxdiagnosis'), namespace='clientuser')),

    # url('downloadpdf/', clientuser.DownloadPDF.as_view(), name='download_pdf'),

    path('csguser/', include(([
        path('', csguser.CsgCapabilityList.as_view(), name='csg_capability_list'),
    ], 'cxdiagnosis'), namespace='csguser')),

    path('cxsuperuser/', include(([
        path('', cxsuperuser.CxSuCapabilityList.as_view(),
             name='cx_su_update_list_capability'),
        path('capability/new/', cxsuperuser.CreateCapabilityView.as_view(),
             name='cx_su_new_capability'),
        path('capability/<int:pk>/', cxsuperuser.UpdateCapabilityView.as_view(),
             name='cx_su_update_capability'),
        path('capability/<int:pk>/completed/',
             cxsuperuser.CompletedCapabilityView.as_view(), name='cx_su_completed_capability'),
        path('capability/<int:pk>/delete/',
             cxsuperuser.DeleteCapabilityView.as_view(), name='cx_su_delete_capability'),
        path('capability/<int:pk>/question/add/',
             cxsuperuser.question_add, name='question_add'),
        path('capability/<int:capability_pk>/question/<int:question_pk>/',
             cxsuperuser.question_change, name='question_change'),
        path('capability/<int:capability_pk>/question/<int:question_pk>/delete/',
             cxsuperuser.QuestionDeleteView.as_view(), name='question_delete'),
    ], 'cxdiagnosis'), namespace='cxsuperuser')),

]
