import time
from django.views.generic import CreateView, ListView, UpdateView, DetailView, DeleteView
from ..models import CxSuperUser, User, Capability, Question, Answer
from ..forms import CxSuperUserSignUpForm, QuestionForm, BaseAnswerInlineFormSet
# ans_maturity_sel
# , BaseAnswerInlineFormSet
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from ..decorators import clientuser_required, cxsuperuser_required
from django.contrib.auth import login
from django.shortcuts import redirect, render, get_object_or_404
from django.db.models import Count
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django import forms
from django.forms import inlineformset_factory
from django.db import transaction

@method_decorator([login_required, cxsuperuser_required], name='dispatch')
class CxSuperUserSignUpView(CreateView):
    model = User
    form_class = CxSuperUserSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'cxsuperuser'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        # return redirect('home')
        return redirect('cxsuperuser:cx_su_update_list_capability')

@method_decorator([login_required, cxsuperuser_required], name='dispatch')
class CxSuCapabilityList(ListView):
    model = Capability
    ordering = ('name', )
    context_object_name = 'capabilities'
    template_name = 'cxsuperuser/cx_su_update_list_capability.html'

    def get_queryset(self):
        queryset = self.request.user.capabilities \
            .annotate(questions_count=Count('questions', distinct=True)) \
            .annotate(completed_count=Count('cx_su_completed_capability', distinct=True))
        return queryset

@method_decorator([login_required, cxsuperuser_required], name='dispatch')
class CreateCapabilityView(CreateView):
    model = Capability
    fields = ('name', )
    template_name = 'cxsuperuser/cx_su_new_capability_form.html'

    def form_valid(self, form):
        capability = form.save(commit=False)
        capability.owner = self.request.user
        capability.save()
        messages.success(self.request, 'The capability was created with success! Go ahead and add some questions now.')
        return redirect('cxsuperuser:cx_su_update_capability', capability.pk)

@method_decorator([login_required, cxsuperuser_required], name='dispatch')
class UpdateCapabilityView(UpdateView):
    model = Capability
    fields = ('name',)
    context_object_name = 'capability'
    template_name = 'cxsuperuser/cx_su_update_capability_form.html'

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
        return reverse('cxsuperuser:cx_su_update_capability', kwargs={'pk': self.object.pk})

@method_decorator([login_required, cxsuperuser_required], name='dispatch')
class CompletedCapabilityView(DetailView):
    model = Capability
    context_object_name = 'capability'
    template_name = 'cxsuperuser/cx_su_completed_capability.html'

    def get_context_data(self, **kwargs):
        capability = self.get_object()
        cx_su_completed_capability = capability.cx_su_completed_capability.select_related('clientuser__user').order_by('-date')
        total_completed_capability = cx_su_completed_capability.count()
        capability_score = capability.cx_su_completed_capability.aggregate(average_score=Avg('score'))
        extra_context = {
            'cx_su_completed_capability': cx_su_completed_capability,
            'total_completed_capability': total_completed_capability,
            'capability_score': capability_score
        }
        kwargs.update(extra_context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        return self.request.user.capabilities.all()

@method_decorator([login_required, cxsuperuser_required], name='dispatch')
class DeleteCapabilityView(DeleteView):
    model = Capability
    context_object_name = 'capability'
    template_name = 'cxsuperuser/cx_su_delete_capability_confirm.html'
    success_url = reverse_lazy('cxsuperuser:cx_su_update_list_capability')

    def delete(self, request, *args, **kwargs):
        capability = self.get_object()
        messages.success(request, 'The capability %s was deleted with success!' % capability.name)
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.capabilities.all()

@login_required
@cxsuperuser_required
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
            return redirect('cxsuperuser:question_change', capability.pk, question.pk )
    else:
        form = QuestionForm()

    return render(request, 'cxsuperuser/question_add_form.html', {'capability': capability, 'form': form})


@login_required
@cxsuperuser_required
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
            return redirect('cxsuperuser:cx_su_update_capability', capability.pk)
    else:
        form = QuestionForm(instance=question)
        formset = AnswerFormSet(instance=question)

    return render(request, 'cxsuperuser/question_change_form.html', {
        'capability': capability,
        'question': question,
        'form': form,
        'formset': formset
    })

@method_decorator([login_required, cxsuperuser_required], name='dispatch')
class QuestionDeleteView(DeleteView):
    model = Question
    context_object_name = 'question'
    template_name = 'cxsuperuser/question_delete_confirm.html'
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
        return reverse('cxsuperuser:cx_su_update_capability', kwargs={'pk': question.capability_id})
