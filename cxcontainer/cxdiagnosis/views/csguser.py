import os
import time
from django.views.generic import CreateView, ListView, UpdateView, DetailView, DeleteView
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from ..decorators import csguser_required, cxsuperuser_required
from django.contrib.auth import login
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Count
from django.db import transaction

from ..models import ClientUser, CsgUser, User, Capability, CompletedCapability, CsgCompletedCapability, Question, Answer, MaturityLevel, CsgUserAnswer
from ..forms import CsgUserSignUpForm, CsgCompletedCapabilityForm

# below packages are to generate pdf using reportlab
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
temp_dir = BASE_DIR + "\\..\\static\\temp"

@method_decorator([login_required, cxsuperuser_required], name='dispatch')
class CsgUserSignUpView(CreateView):
    model = User
    form_class = CsgUserSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'csguser'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('csguser:capability_list')

@method_decorator([login_required, csguser_required], name='dispatch')
class CapabilityList(ListView):
    model = Capability
    ordering = ('name', )
    context_object_name = 'capabilities'
    template_name = 'csguser/capability_list.html'

    def get_queryset(self):
        csguser = self.request.user.csguser
        csguser_domains = csguser.domains
        # .values_list('pk', flat=True)
        # completed_capabilities = clientuser.capabilities.values_list(
        #     'pk', flat=True)
        completed_capability_ids = []
        for i in csguser.capabilities.values_list('pk',flat=True).distinct():
            if not csguser.get_unanswered_questions(get_object_or_404(Capability, pk=i)).exists():
                completed_capability_ids.append(i)
        queryset = Capability.objects \
            .exclude(pk__in=completed_capability_ids) \
            .annotate(questions_count=Count('questions')) \
            .filter(questions_count__gt=0)
        return queryset

@method_decorator([login_required, csguser_required], name='dispatch')
class CompletedCapabilitylistView(ListView):
    model = CsgCompletedCapability
    context_object_name = 'csg_completed_capabilities'
    template_name = 'csguser/completed_capability_list.html'

    def get_queryset(self):
        queryset = self.request.user.csguser.csg_completed_capabilities \
            .select_related('capability') \
            .order_by('capability__name')
        return queryset

@method_decorator([login_required, csguser_required], name='dispatch')
class DomainCompletedCapabilitylistView(ListView):
    context_object_name = 'csg_domain_completed_capabilities'
    template_name = 'csguser/domain_completed_capability_list.html'

    def get_context_data(self, **kwargs):
        domain = self.request.user.csguser.domains
        context = super(DomainCompletedCapabilitylistView, self).get_context_data(**kwargs)
        context['clientuserlist'] = CompletedCapability.objects.filter(clientuser__domains=domain).all()
        context['csguserlist'] = CsgCompletedCapability.objects.filter(csguser__domains=domain).all()
        return context

    def get_queryset(self):
        return 0
# @login_required
# @csguser_required
# def user_domain_completed_capability_all_child(request):
#     csguser = request.user.csguser
# 	domains = csguser.domains
#
#     for csc in CsgCompletedCapability.objects.all():
# 		if ClientUser.objects.filter(domains=domains,user=csc.clientuser_id):
# 			csc.capability, csc.question, csc.score, csc.date
#
#     for cc in CompletedCapability.objects.all():
# 		if ClientUser.objects.filter(domains=domains,user=cc.clientuser_id):
# 			cc.capability, cc.question, cc.score, cc.date
#
#     return render(request, 'csguser/user_domain_completed_capability_all_child_form.html', {
#         'csc.capability': csc.capability,
#         'csc.question': csc.question,
#         'csc.score': csc.score,
#         'csc.date': csc.date,
#         'cc.capability': csc.capability,
#         'cc.question': csc.question,
#         'cc.score': csc.score,
#         'cc.date': csc.date,
#     })

@login_required
@csguser_required
def write_pdf_view(request, pk):
    doc = SimpleDocTemplate(temp_dir + "\\csguser_data.pdf")
    styles = getSampleStyleSheet()
    Story = [Spacer(1, 2*inch)]
    style = styles["Normal"]

    header_line = ('''<span><font size="10" color=black><b>  Capability Area  </b></font><font size="10" color=gray><b>  Capability  </b></font><font size="10" color=black><b>  Score  </b></font><font size="10" color=gray><b>  Date  </b></font></span>''')
    p = Paragraph(header_line, style)
    Story.append(p)
    Story.append(Spacer(1, 0.2*inch))
    for completed_capability in CsgCompletedCapability.objects.all():
        if completed_capability.csguser_id == pk:
            formated_string = ('''<span> <font size="8" color=black>%100s</font>     <font size="8" color=gray>%400s</font>   <font size="8" color=black><i>%30s</i></font>   <font size="8" color=gray>%10s</font>  </span>''' %
                               (completed_capability.capability, completed_capability.question, completed_capability.score, completed_capability.date))
            p = Paragraph(formated_string, style)
            Story.append(p)
            Story.append(Spacer(1, 0.2*inch))
    doc.build(Story)

    fs = FileSystemStorage(temp_dir)
    with fs.open("csguser_data.pdf") as pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="csguser_data.pdf"'
        return response

    return response

@login_required
@csguser_required
def edit_completed_capability(request, pk, editqno, pgid, isprev, isnex):
    capability = get_object_or_404(Capability, pk=pk)
    csguser = request.user.csguser

    total_questions = capability.questions.count()
    answered_questions = csguser.get_answered_questions(capability, )
    total_answered_questions = answered_questions.count()
    progress = round(((total_answered_questions - pgid) / total_questions) * 100)
    question = answered_questions.order_by('-id')[pgid]
    cuaid=CsgUserAnswer.objects.filter(csguser=csguser).latest('id').id - pgid
    cuainst=CsgUserAnswer.objects.get(id=cuaid)

    if request.method == 'POST':
        form = CsgCompletedCapabilityForm(instance=cuainst, question=question, data=request.POST)
        if form.is_valid():
            with transaction.atomic():
                csguser_answer = form.save(commit=False)
                csguser_answer.csguser = csguser
                csguser_answer.save()
                answer = csguser_answer.answer.pk
                question = Answer.objects.get(pk=answer).question
                question_weightage = Question.objects.get(
                    text=question).weightage
                maturitylevel = Answer.objects.get(pk=answer).maturitylevel
                maturitylevel_score = MaturityLevel.objects.get(
                    name=maturitylevel).score
                score = round((maturitylevel_score * question_weightage) / 100.0, 2)
                ccid=CsgCompletedCapability.objects.filter(csguser=csguser).latest('id').id - pgid
                CsgCompletedCapability.objects.filter(id=ccid, csguser=csguser).update(csguser=csguser, capability=capability, question=question, score=score)

                if pgid > 0:
                    pgid = pgid - 1
                    editqno = editqno + 1
                    return redirect('csguser:edit_completed_capability', pk, editqno, pgid, 0, 1)
                elif csguser.get_unanswered_questions(capability).exists():
                    return redirect('csguser:completed_capability', pk)
                else:
                    return redirect('csguser:capability_list')
    else:
        form = CsgCompletedCapabilityForm(instance=cuainst, question=question,)

    pgid = pgid + 1
    editqno = editqno - 1

    return render(request, 'csguser/edit_completed_capability_form.html', {
        'capability': capability,
        'question': question,
        'form': form,
        'progress': progress,
        'editqno' : editqno,
        'pgid' : pgid,
        'total_answered_questions' : total_answered_questions,
        'isprev' : isprev,
        'isnex' : isnex,
    })

@login_required
@csguser_required
def completed_capability(request, pk):
    capability = get_object_or_404(Capability, pk=pk)
    csguser = request.user.csguser

    total_questions = capability.questions.count()
    unanswered_questions = csguser.get_unanswered_questions(capability)
    total_unanswered_questions = unanswered_questions.count()
    progress = 100 - \
        round(((total_unanswered_questions - 1) / total_questions) * 100)
    question = unanswered_questions.first()

    if request.method == 'POST':
        form = CsgCompletedCapabilityForm(question=question, data=request.POST)
        if form.is_valid():
            with transaction.atomic():
                csguser_answer = form.save(commit=False)
                csguser_answer.csguser = csguser
                csguser_answer.save()
                answer = csguser_answer.answer.pk
                question = Answer.objects.get(pk=answer).question
                question_weightage = Question.objects.get(
                    text=question).weightage
                maturitylevel = Answer.objects.get(pk=answer).maturitylevel
                maturitylevel_score = MaturityLevel.objects.get(
                    name=maturitylevel).score
                score = round(
                    (maturitylevel_score * question_weightage) / 100.0, 2)
                CsgCompletedCapability.objects.create(
                    csguser=csguser, capability=capability, question=question, score=score)
                if csguser.get_unanswered_questions(capability).exists():
                    return redirect('csguser:completed_capability', pk)
                else:
                    return redirect('csguser:capability_list')
    else:
        form = CsgCompletedCapabilityForm(question=question)

    return render(request, 'csguser/completed_capability_form.html', {
        'capability': capability,
        'question': question,
        'form': form,
        'progress': progress,
        'total_unanswered_questions' : total_unanswered_questions,
        'total_questions' : total_questions
    })

@method_decorator([login_required, csguser_required], name='dispatch')
class CapabilityUpdateList(ListView):
    model = Capability
    ordering = ('name', )
    context_object_name = 'capabilities'
    template_name = 'csguser/update_list_capability.html'

    def get_queryset(self):
        queryset = self.request.user.capabilities \
            .annotate(questions_count=Count('questions', distinct=True)) \
            .annotate(completed_count=Count('csguser', distinct=True))
        return queryset

@method_decorator([login_required, csguser_required], name='dispatch')
class CreateCapabilityView(CreateView):
    model = Capability
    fields = ('name', )
    template_name = 'csguser/new_capability_form.html'

    def form_valid(self, form):
        capability = form.save(commit=False)
        capability.owner = self.request.user
        capability.save()
        messages.success(self.request, 'The capability was created with success! Go ahead and add some questions now.')
        return redirect('csguser:update_capability', capability.pk)

@method_decorator([login_required, csguser_required], name='dispatch')
class UpdateCapabilityView(UpdateView):
    model = Capability
    fields = ('name',)
    context_object_name = 'capability'
    template_name = 'csguser/update_capability_form.html'

    def get_context_data(self, **kwargs):
        kwargs['questions'] = self.get_object().questions.annotate(answers_count=Count('answers'))
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        '''
        This method is an implicit object-level permission management
        This view will only match the ids of existing capabilities that belongs
        to the logged in user.
        '''
        return self.request.user.capabilities.all()

    def get_success_url(self):
        return reverse('csguser:update_capability', kwargs={'pk': self.object.pk})

@method_decorator([login_required, csguser_required], name='dispatch')
class CompletedCapabilityView(DetailView):
    model = Capability
    context_object_name = 'capability'
    template_name = 'csguser/completed_capability.html'

    def get_context_data(self, **kwargs):
        capability = self.get_object()
        completed_capabilities = capability.completed_capabilities.select_related('csguser__user').order_by('-date')
        total_completed_capabilities = completed_capabilities.count()
        capability_score = capability.completed_capabilities.aggregate(average_score=Avg('score'))
        extra_context = {
            'completed_capabilities': completed_capabilities,
            'total_completed_capabilities': total_completed_capabilities,
            'capability_score': capability_score
        }
        kwargs.update(extra_context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        return self.request.user.capabilities.all()

@method_decorator([login_required, csguser_required], name='dispatch')
class DeleteCapabilityView(DeleteView):
    model = Capability
    context_object_name = 'capability'
    template_name = 'csguser/delete_capability_confirm.html'
    success_url = reverse_lazy('csguser:update_list_capability')

    def delete(self, request, *args, **kwargs):
        capability = self.get_object()
        messages.success(request, 'The capability %s was deleted with success!' % capability.name)
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.capabilities.all()

@login_required
@csguser_required
def question_add(request, pk):
    # By filtering the capability by the url keyword argument `pk` and
    # by the owner, which is the logged in user, we are protecting
    # this view at the object-level. Meaning only the owner of
    # capability will be able to add questions to it.
    capability = get_object_or_404(Capability, pk=pk, owner=request.user)

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.capability = capability
            # question.weightage = forms.DecimalField(max_digits=5, decimal_places=2,required=True)
            question.save()
            messages.success(request, 'You may now add answers/options to the question.')
            return redirect('csguser:question_change', capability.pk, question.pk )
    else:
        form = QuestionForm()

    return render(request, 'csguser/question_add_form.html', {'capability': capability, 'form': form})


@login_required
@csguser_required
def question_change(request, capability_pk, question_pk):
    # mat_sel_form = ans_maturity_sel()
    # Simlar to the `question_add` view, this view is also managing
    # the permissions at object-level. By querying both `capability` and
    # `question` we are making sure only the owner of the capability can
    # change its details and also only questions that belongs to this
    # specific capability can be changed via this url (in cases where the
    # user might have forged/player with the url params.
    capability = get_object_or_404(Capability, pk=capability_pk, owner=request.user)
    question = get_object_or_404(Question, pk=question_pk, capability=capability)

    AnswerFormSet = inlineformset_factory(
        Question,  # parent model
        Answer,  # base model
        formset=BaseAnswerInlineFormSet,
        # formset=AnswerForm
        fields=('text', 'maturitylevel'),
        min_num=4,
        validate_min=True,
        max_num=4,
        validate_max=True
    )

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        formset = AnswerFormSet(request.POST, instance=question)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
            messages.success(request, 'Question and answers saved with success!')
            return redirect('csguser:update_capability', capability.pk)
    else:
        form = QuestionForm(instance=question)
        formset = AnswerFormSet(instance=question)

    return render(request, 'csguser/question_change_form.html', {
        'capability': capability,
        'question': question,
        'form': form,
        'formset': formset
    })

@method_decorator([login_required, csguser_required], name='dispatch')
class QuestionDeleteView(DeleteView):
    model = Question
    context_object_name = 'question'
    template_name = 'csguser/question_delete_confirm.html'
    pk_url_kwarg = 'question_pk'

    def get_context_data(self, **kwargs):
        question = self.get_object()
        kwargs['capability'] = question.capability
        return super().get_context_data(**kwargs)

    def delete(self, request, *args, **kwargs):
        question = self.get_object()
        messages.success(request, 'The question %s was deleted with success!' % question.text)
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return Question.objects.filter(capability__owner=self.request.user)

    def get_success_url(self):
        question = self.get_object()
        return reverse('csguser:update_capability', kwargs={'pk': question.capability_id})
