import time
from django.views.generic import CreateView, ListView, UpdateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from ..decorators import csguser_required, cxsuperuser_required
from django.contrib.auth import login
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Count

from ..models import CsgUser, User, Capability, CompletedCapability, Question, Answer, MaturityLevel
from ..forms import CsgUserSignUpForm

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
        return redirect('csguser:csg_capability_list')

@method_decorator([login_required, csguser_required], name='dispatch')
class CsgCapabilityList(ListView):
    model = Capability
    ordering = ('name', )
    context_object_name = 'capabilities'
    template_name = 'csguser/csg_capability_list.html'

@method_decorator([login_required, csguser_required], name='dispatch')
class CsgCompletedCapabilitylistView(ListView):
    model = Capability
    ordering = ('name', )
    context_object_name = 'capabilities'
    template_name = 'csguser/csg_completed_capability_list.html'

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
    for completed_capability in CompletedCapability.objects.all():
        if completed_capability.clientuser_id == pk:
            formated_string = ('''<span> <font size="8" color=black>%100s</font>     <font size="8" color=gray>%400s</font>   <font size="8" color=black><i>%30s</i></font>   <font size="8" color=gray>%10s</font>  </span>''' %
                               (completed_capability.capability, completed_capability.question, completed_capability.score, completed_capability.date))
            p = Paragraph(formated_string, style)
            Story.append(p)
            Story.append(Spacer(1, 0.2*inch))
    doc.build(Story)

    fs = FileSystemStorage(temp_dir)
    with fs.open("clientuser_data.pdf") as pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="clientuser_data.pdf"'
        return response

    return response

@login_required
@csguser_required
def edit_completed_capability(request, pk, editqno, pgid, isprev, isnex):
    capability = get_object_or_404(Capability, pk=pk)
    clientuser = request.user.clientuser

    total_questions = capability.questions.count()
    answered_questions = clientuser.get_answered_questions(capability, )
    total_answered_questions = answered_questions.count()
    progress = round(((total_answered_questions - pgid) / total_questions) * 100)
    question = answered_questions.order_by('-id')[pgid]
    cuaid=ClientUserAnswer.objects.filter(clientuser=clientuser).latest('id').id - pgid
    cuainst=ClientUserAnswer.objects.get(id=cuaid)

    if request.method == 'POST':
        form = CompletedCapabilityForm(instance=cuainst, question=question, data=request.POST)
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
                score = round((maturitylevel_score * question_weightage) / 100.0, 2)
                ccid=CompletedCapability.objects.filter(clientuser=clientuser).latest('id').id - pgid
                CompletedCapability.objects.filter(id=ccid, clientuser=clientuser).update(clientuser=clientuser, capability=capability, question=question, score=score)

                if pgid > 0:
                    pgid = pgid - 1
                    editqno = editqno + 1
                    return redirect('clientuser:edit_completed_capability', pk, editqno, pgid, 0, 1)
                elif clientuser.get_unanswered_questions(capability).exists():
                    return redirect('clientuser:completed_capability', pk)
                else:
                    return redirect('clientuser:capability_list')
    else:
        form = CompletedCapabilityForm(instance=cuainst, question=question,)

    pgid = pgid + 1
    editqno = editqno - 1

    return render(request, 'clientuser/edit_completed_capability_form.html', {
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
    clientuser = request.user.clientuser

    total_questions = capability.questions.count()
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
                score = round(
                    (maturitylevel_score * question_weightage) / 100.0, 2)
                CompletedCapability.objects.create(
                    clientuser=clientuser, capability=capability, question=question, score=score)
                if clientuser.get_unanswered_questions(capability).exists():
                    return redirect('clientuser:completed_capability', pk)
                else:
                    return redirect('clientuser:capability_list')
    else:
        form = CompletedCapabilityForm(question=question)

    return render(request, 'clientuser/completed_capability_form.html', {
        'capability': capability,
        'question': question,
        'form': form,
        'progress': progress,
        'total_unanswered_questions' : total_unanswered_questions,
        'total_questions' : total_questions
    })
