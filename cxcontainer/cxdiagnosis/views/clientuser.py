import os
import time
from django.views.generic import CreateView, ListView, UpdateView, DetailView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.db.models import Count
from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from ..models import ClientUser, User, Capability, CompletedCapability, Question, Answer, MaturityLevel
from ..forms import ClientUserSignUpForm, CompletedCapabilityForm, ClientUserDomainForm
from ..decorators import clientuser_required
# from easy_pdf.views import PDFTemplateView
# from django_xhtml2pdf.views import PdfMixin
# from xhtml2pdf import pisa

# below packages are to generate pdf using reportlab
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
temp_dir = BASE_DIR + "\\..\\static\\temp"
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
class ClientUserDomainView(UpdateView):
    model = ClientUser
    form_class = ClientUserDomainForm
    template_name = 'clientuser/domains_form.html'
    success_url = reverse_lazy('clientuser:capability_list')

    def get_object(self):
        return self.request.user.clientuser

    def form_valid(self, form):
        messages.success(self.request, 'Interests updated with success!')
        return super().form_valid(form)


@method_decorator([login_required, clientuser_required], name='dispatch')
class CapabilityListView(ListView):
    model = Capability
    ordering = ('name', )
    context_object_name = 'capabilities'
    template_name = 'clientuser/capability_list.html'

    def get_queryset(self):
        clientuser = self.request.user.clientuser
        clientuser_domains = clientuser.domains
        # .values_list('pk', flat=True)
        # completed_capabilities = clientuser.capabilities.values_list(
        #     'pk', flat=True)
        completed_capability_ids = []
        for i in clientuser.capabilities.values_list('pk',flat=True).distinct():
            if not clientuser.get_unanswered_questions(get_object_or_404(Capability, pk=i)).exists():
                completed_capability_ids.append(i)
        queryset = Capability.objects \
            .exclude(pk__in=completed_capability_ids) \
            .annotate(questions_count=Count('questions')) \
            .filter(questions_count__gt=0)
        return queryset


@method_decorator([login_required, clientuser_required], name='dispatch')
class CompletedCapabilitylistView(ListView):
    model = CompletedCapability
    context_object_name = 'completed_capabilities'
    template_name = 'clientuser/completed_capability_list.html'

    def get_queryset(self):
        queryset = self.request.user.clientuser.completed_capabilities \
            .select_related('capability') \
            .order_by('capability__name')
        return queryset


# @method_decorator([login_required, clientuser_required], name='dispatch')
# class DownloadPDF(PdfMixin, DetailView):
#     template_name = 'clientuser/download_pdf.html'


# @method_decorator([login_required, clientuser_required], name='dispatch')
# class DownloadPDF(PdfMixin, DetailView):
#     model = CompletedCapability
#     template_name = 'clientuser/download_pdf.html'


def write_pdf_view(request, pk):
    # capability = get_object_or_404(CompletedCapability)
    # clientuser = request.user.clientuser
    # request.user.clientuser
    doc = SimpleDocTemplate(temp_dir + "\\clientuser_data.pdf")
    styles = getSampleStyleSheet()
    Story = [Spacer(1, 2*inch)]
    style = styles["Normal"]

    header_line = ('''<span><font size="10" color=black><b>  Capability Area  </b></font><font size="10" color=gray><b>  Capability  </b></font><font size="10" color=black><b>  Score  </b></font><font size="10" color=gray><b>  Date  </b></font></span>''')
    p = Paragraph(header_line, style)
    Story.append(p)
    Story.append(Spacer(1, 0.2*inch))
    # ca = None
    for completed_capability in CompletedCapability.objects.all():
        if completed_capability.clientuser_id == pk:
            # if ca == None:
            #     formated_string = (''' %30s %100s
            #                        %400s %10s ''' %
            #                        (completed_capability.date, completed_capability.capability, completed_capability.question, completed_capability.score))
            #     p = Paragraph(formated_string, style)
            #     ca = completed_capability.capability
            # elif ca == completed_capability.capability:
            #     formated_string = (''' %400s %10s ''' %
            #                        (completed_capability.question, completed_capability.score))
            #     p = Paragraph(formated_string, style)
            # else:
            #     formated_string = (''' %30s %100s
            #                        %400s %10s ''' %
            #                        (completed_capability.date, completed_capability.capability, completed_capability.question, completed_capability.score))
            #     p = Paragraph(formated_string, style)
            #     ca = completed_capability.capability

            formated_string = ('''<span> <font size="8" color=black>%100s</font>     <font size="8" color=gray>%400s</font>   <font size="8" color=black><i>%30s</i></font>   <font size="8" color=gray>%10s</font>  </span>''' %
                               (completed_capability.capability, completed_capability.question, completed_capability.score, completed_capability.date))
            p = Paragraph(formated_string, style)
            Story.append(p)
            Story.append(Spacer(1, 0.2*inch))
    # ca = None
    doc.build(Story)

    fs = FileSystemStorage(temp_dir)
    with fs.open("clientuser_data.pdf") as pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="clientuser_data.pdf"'
        # response['Content-Disposition'] = 'inline; filename="mypdf.pdf"'
        return response

    return response

# class DownloadPDF(ListView):
#     model = CompletedCapability
#     context_object_name = 'completed_capabilities'
#     template_name = 'clientuser/download_pdf.html'
#
#     def get_queryset(self):
#         queryset = self.request.user.clientuser.completed_capabilities \
#             .select_related('capability') \
#             .order_by('capability__name')
#         return queryset


@login_required
@clientuser_required
def completed_capability(request, pk):
    capability = get_object_or_404(Capability, pk=pk)
    clientuser = request.user.clientuser
    # question = question = get_object_or_404(Question, pk=pk, capability=capability)
    # question_weightage = question.weightage
    # if clientuser.capabilities.filter(pk=pk).exists():
    #     return render(request, 'clientuser/completed_capability.html')

    total_questions = capability.questions.count()
    # question_weightage = capability.questions.weightage
    unanswered_questions = clientuser.get_unanswered_questions(capability)
    total_unanswered_questions = unanswered_questions.count()
    progress = 100 - \
        round(((total_unanswered_questions - 1) / total_questions) * 100)
    question = unanswered_questions.first()

    if request.method == 'POST':
        form = CompletedCapabilityForm(question=question, data=request.POST)
        if form.is_valid():
            with transaction.atomic():
                clientuser_answer = form.save(commit=False)
                clientuser_answer.clientuser = clientuser
                clientuser_answer.save()
                answer = clientuser_answer.answer.pk
                question = Answer.objects.get(pk=answer).question
                question_weightage = Question.objects.get(
                    text=question).weightage
                maturitylevel = Answer.objects.get(pk=answer).maturitylevel
                maturitylevel_score = MaturityLevel.objects.get(
                    name=maturitylevel).score
                # question_weightage = Question.objects.get(capability=pk).weightage
                score = round(
                    (maturitylevel_score * question_weightage) / 100.0, 2)
                CompletedCapability.objects.create(
                    clientuser=clientuser, capability=capability, question=question, score=score)
                if clientuser.get_unanswered_questions(capability).exists():
                    return redirect('clientuser:completed_capability', pk)
                else:
                    # maturitylevel_score = 15
                    # maturitylevel = clientuser_answer.maturitylevel
                    # maturitylevel_score = MaturityLevel.objects.get(pk=maturitylevel).score
                    # maturitylevel_score = clientuser.capability_answers.filter(answer__question__capability=pk)
                    # maturitylevel = clientuser.capability_answers.filter(question__capability=capability)
                    # question_weightage = Question.objects.get(capability=pk).weightage
                    # score = round((maturitylevel_score * question_weightage) / 100.0, 2)
                    # CompletedCapability.objects.create(clientuser=clientuser, capability=capability, score=score)
                    messages.success(request, 'Congratulations! You completed the capability %s with success! You scored %s points.' % (
                        capability.name, score))
                    return redirect('clientuser:capability_list')
    else:
        form = CompletedCapabilityForm(question=question)

    return render(request, 'clientuser/completed_capability_form.html', {
        'capability': capability,
        'question': question,
        'form': form,
        'progress': progress
    })
