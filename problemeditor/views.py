from django.shortcuts import render,render_to_response, get_object_or_404,redirect
from django.http import HttpResponse,HttpResponseRedirect,Http404
from django.template import loader,RequestContext
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from formtools.wizard.views import SessionWizardView

from .models import Problem, Topic,  Solution,Comment,ProblemStatus
from .forms import SolutionForm,ProblemTextForm,AddProblemForm,DetailedProblemForm,CommentForm,DiffMoveProblemForm
from .utils import goodtag,goodurl,newtexcode,newsoltexcode,compileasy


# Create your views here.

@login_required
def UpdatePassword(request):
    form = PasswordChangeForm(user=request.user)

    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect('/')
    return render(request, 'registration/change-password.html', {
        'form': form,
    })

@login_required
def index_view(request):
    if request.method=='POST':
        form=request.POST
        for i in form:
            if 'status' in i:
                pk=i.split('_')[1]
                prob=Problem.objects.get(pk=pk)
                prob.problem_status=form[i]
                prob.save()
            if 'difficulty' in i:
                pk=i.split('_')[1]
                prob=Problem.objects.get(pk=pk)
                prob.difficulty=form[i]
                prob.save()
    propose_now = Problem.objects.filter(problem_status='PN')
    propose_later = Problem.objects.filter(problem_status='PL')
    needs_minor = Problem.objects.filter(problem_status='MI')
    needs_major = Problem.objects.filter(problem_status='MJ')
    pna = propose_now.filter(topic__topic='Algebra')
    pla = propose_later.filter(topic__topic='Algebra')
    mia = needs_minor.filter(topic__topic='Algebra')
    mja = needs_major.filter(topic__topic='Algebra')
    pnc = propose_now.filter(topic__topic='Combinatorics')
    plc = propose_later.filter(topic__topic='Combinatorics')
    mic = needs_minor.filter(topic__topic='Combinatorics')
    mjc = needs_major.filter(topic__topic='Combinatorics')
    png = propose_now.filter(topic__topic='Geometry')
    plg = propose_later.filter(topic__topic='Geometry')
    mig = needs_minor.filter(topic__topic='Geometry')
    mjg = needs_major.filter(topic__topic='Geometry')
    pnn = propose_now.filter(topic__topic='Number Theory')
    pln = propose_later.filter(topic__topic='Number Theory')
    min = needs_minor.filter(topic__topic='Number Theory')
    mjn = needs_major.filter(topic__topic='Number Theory')
    pnga = propose_now.filter(topic__topic='Games')
    plga = propose_later.filter(topic__topic='Games')
    miga = needs_minor.filter(topic__topic='Games')
    mjga = needs_major.filter(topic__topic='Games')
    pno = propose_now.filter(topic__topic='Other')
    plo = propose_later.filter(topic__topic='Other')
    mio = needs_minor.filter(topic__topic='Other')
    mjo = needs_major.filter(topic__topic='Other')
#might need calculations to build rows (# sols, etc?)
    template=loader.get_template('problemeditor/typeview.html')
    context= {'pna' : pna, 'pla' : pla, 'mia': mia, 'mja' : mja,
              'pnc' : pnc, 'plc' : plc, 'mic': mic, 'mjc' : mjc,
              'png' : png, 'plg' : plg, 'mig': mig, 'mjg' : mjg,
              'pnn' : pnn, 'pln' : pln, 'min': min, 'mjn' : mjn,
              'pnga' : pnga, 'plga' : plga, 'miga': miga, 'mjga' : mjga,
              'pno' : pno, 'plo' : plo, 'mio': mio, 'mjo' : mjo, 'nbar': 'problemeditor'}
    return HttpResponse(template.render(context,request))


@login_required
def editproblemtextpkview(request,**kwargs):
    pk=kwargs['pk']
    prob=get_object_or_404(Problem, pk=pk)
    if request.method == "POST":
        form = ProblemTextForm(request.POST, instance=prob)
        if form.is_valid():
            problem = form.save()
            problem.problem_latex = newtexcode(problem.problem_text,problem.label)
            problem.save()
            compileasy(problem.problem_text,problem.label)
        return redirect('../')
    else:
        form = ProblemTextForm(instance=prob)
    context={}
    context['form'] = form
    context['nbar'] = 'problemeditor'
    return render(request, 'problemeditor/editproblemtext.html', context)


@login_required
def newsolutionpkview(request,**kwargs):
    pk=kwargs['pk']
    prob=get_object_or_404(Problem, pk=pk)

    sol_num=prob.top_solution_number+1
    prob.top_solution_number=sol_num
    prob.save()
    if request.method == "POST":
        sol_form = SolutionForm(request.POST)
        if sol_form.is_valid():
            sol = sol_form.save()
            sol.solution_number=sol_num
            sol.authors.add(request.user)
            sol.problem_label=prob.label
            sol.solution_latex = newsoltexcode(sol.solution_text,prob.label+'sol'+str(sol.solution_number))
            sol.save()
            compileasy(sol.solution_text,prob.label,sol='sol'+str(sol_num))
            prob.solutions.add(sol)
            prob.save()
        return redirect('../')
    else:
        sol=Solution(solution_text='', solution_number=sol_num, problem_label=prob.label)
        form = SolutionForm(instance=sol)

    return render(request, 'problemeditor/newsol.html', {'form': form, 'nbar': 'problemeditor','problem':prob})


@login_required
def editsolutionpkview(request,**kwargs):
    pk=kwargs['pk']
    spk=kwargs['spk']
    prob=get_object_or_404(Problem, pk=pk)
    sol=Solution.objects.get(pk=spk)
    if request.method == "POST":
        if request.POST.get("save"):
            sollist=request.POST.getlist('solution_text')
            sol.solution_text=sollist[0]
            sol.authors.add(request.user)
            sol.solution_latex=newsoltexcode(sol.solution_text,prob.label+'sol'+str(sol.solution_number))
            sol.save()
            compileasy(sol.solution_text,prob.label,sol='sol'+str(sol.solution_number))
            return redirect('../../')
    form = SolutionForm(instance=sol)
    return render(request, 'problemeditor/editsol.html', {'form': form, 'nbar': 'problemeditor','problem':prob})




@login_required
def deletesolutionpkview(request,**kwargs):#If solution_number is kept, this must be modified to adjust.
    pk=kwargs['pk']
    spk=kwargs['spk']
    sol = get_object_or_404(Solution, pk=spk)
    sol.delete()
    return redirect('../../')

@login_required
def deletecommentpkview(request,**kwargs):#If solution_number is kept, this must be modified to adjust.
    pk=kwargs['pk']
    cpk=kwargs['cpk']
    com = get_object_or_404(Comment, pk=cpk)
    com.delete()
    return redirect('../../')

@login_required
def newcommentpkview(request,**kwargs):
    pk=kwargs['pk']
    prob=get_object_or_404(Problem, pk=pk)
    com_num=prob.comments.count()+1
    if request.method == "POST":
        com_form = CommentForm(request.POST)
        if com_form.is_valid():
            com = com_form.save(commit=False)
            com.comment_number=com_num
            com.author = request.user
            com.problem_label=prob.label
            com.save()
            prob.comments.add(com)
            prob.save()
            return redirect('../')
    else:
        com=Comment(comment_text='', comment_number=com_num, problem_label=prob.label)
        com_form = CommentForm(instance=com)

    return render(request, 'problemeditor/newcom.html', {'form': com_form, 'nbar': 'problemeditor','problem':prob})



@login_required
def detailedproblemview(request,**kwargs):
    pk=kwargs['pk']
    prob=get_object_or_404(Problem, pk=pk)
    context={}
    breadcrumbs=[]
    form=DetailedProblemForm(instance=prob)
    #sols...
    sols=prob.solutions.all()
    context['sols']=sols
    #coms...
    coms=prob.comments.all()
    context['coms']=coms
    #approvals
#    status=prob.problem_status
#    context['apprs']=apprs
    #other
    context['problem']=prob
    context['nbar']='problemeditor'
    context['form']=form
    context['breadcrumbs']=breadcrumbs
    return render(request, 'problemeditor/detailedview.html', context)

@login_required
def addproblemview(request):
    prob=Problem()
    if request.method == "POST":
        form = AddProblemForm(request.POST, instance=prob)
        if form.is_valid():
            problem = form.save()
            problem.save()
            problem.label = problem.topic.topic+' '+str(problem.topic.top_index)
            problem.topic.top_index+=1
            problem.topic.save()
            problem.save()
            return redirect('../detailedview/'+str(problem.pk)+'/')
    else:
        form = AddProblemForm(instance=prob)
    return render(request, 'problemeditor/addview.html', {'form': form, 'nbar': 'problemeditor'})

