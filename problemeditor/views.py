from django.shortcuts import render,render_to_response, get_object_or_404,redirect
from django.http import HttpResponse,HttpResponseRedirect,Http404
from django.template import loader,RequestContext,Context
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings

from formtools.wizard.views import SessionWizardView

from .models import Problem, Topic,  Solution,Comment,ProblemStatus,FinalTest
from .forms import SolutionForm,ProblemTextForm,AddProblemForm,DetailedProblemForm,CommentForm,DiffMoveProblemForm
from .utils import goodtag,goodurl,newtexcode,newsoltexcode,compileasy,compiletikz

from django.template.loader import get_template

from subprocess import Popen,PIPE
import tempfile
import os

import logging
logger = logging.getLogger(__name__)

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
    new_problems = Problem.objects.filter(problem_status='NP')
    propose_now = Problem.objects.filter(problem_status='PN')
    propose_later = Problem.objects.filter(problem_status='PL')
    needs_minor = Problem.objects.filter(problem_status='MI')
    needs_major = Problem.objects.filter(problem_status='MJ')
    npa = new_problems.filter(topic='Algebra')
    pna = propose_now.filter(topic='Algebra')
    pla = propose_later.filter(topic='Algebra')
    mia = needs_minor.filter(topic='Algebra')
    mja = needs_major.filter(topic='Algebra')
    npc = new_problems.filter(topic='Combinatorics')
    pnc = propose_now.filter(topic='Combinatorics')
    plc = propose_later.filter(topic='Combinatorics')
    mic = needs_minor.filter(topic='Combinatorics')
    mjc = needs_major.filter(topic='Combinatorics')
    npg = new_problems.filter(topic='Geometry')
    png = propose_now.filter(topic='Geometry')
    plg = propose_later.filter(topic='Geometry')
    mig = needs_minor.filter(topic='Geometry')
    mjg = needs_major.filter(topic='Geometry')
    npn = new_problems.filter(topic='Number Theory')
    pnn = propose_now.filter(topic='Number Theory')
    pln = propose_later.filter(topic='Number Theory')
    min = needs_minor.filter(topic='Number Theory')
    mjn = needs_major.filter(topic='Number Theory')
    npga = new_problems.filter(topic='Games')
    pnga = propose_now.filter(topic='Games')
    plga = propose_later.filter(topic='Games')
    miga = needs_minor.filter(topic='Games')
    mjga = needs_major.filter(topic='Games')
    npo = new_problems.filter(topic='Other')
    pno = propose_now.filter(topic='Other')
    plo = propose_later.filter(topic='Other')
    mio = needs_minor.filter(topic='Other')
    mjo = needs_major.filter(topic='Other')
#might need calculations to build rows (# sols, etc?)
    template=loader.get_template('problemeditor/typeview.html')
#    context= {'pna' : pna, 'pla' : pla, 'mia': mia, 'mja' : mja,
#              'pnc' : pnc, 'plc' : plc, 'mic': mic, 'mjc' : mjc,
#              'png' : png, 'plg' : plg, 'mig': mig, 'mjg' : mjg,
#              'pnn' : pnn, 'pln' : pln, 'min': min, 'mjn' : mjn,
#              'pnga' : pnga, 'plga' : plga, 'miga': miga, 'mjga' : mjga,
#              'pno' : pno, 'plo' : plo, 'mio': mio, 'mjo' : mjo, 'nbar': 'problemeditor'}
    allcats= (
        ('New Problems',
         ((npa,'Algebra'),(npc,'Combinatorics'),(npga,'Games'),(npg,'Geometry'),(npn,'Number Theory'),(npo,'Other'))),
        ('Proposed for Current Year',
         ((pna,'Algebra'),(pnc,'Combinatorics'),(pnga,'Games'),(png,'Geometry'),(pnn,'Number Theory'),(pno,'Other'))),
        ('Proposed for Future Year',
         ((pla,'Algebra'),(plc,'Combinatorics'),(plga,'Games'),(plg,'Geometry'),(pln,'Number Theory'),(plo,'Other'))),
        ('Has Potential',
         ((mia,'Algebra'),(mic,'Combinatorics'),(miga,'Games'),(mig,'Geometry'),(min,'Number Theory'),(mio,'Other'))),
        ('Needs Major Revision',
         ((mja,'Algebra'),(mjc,'Combinatorics'),(mjga,'Games'),(mjg,'Geometry'),(mjn,'Number Theory'),(mjo,'Other'))),
        )
    context = {'allcats':allcats,'nbar':'problemeditor'}
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
            compiletikz(problem.problem_text,problem.label)
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
            compiletikz(sol.solution_text,prob.label,sol='sol'+str(sol_num))
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
            compiletikz(sol.solution_text,prob.label,sol='sol'+str(sol.solution_number))
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
            problem.label = 'Problem '+str(problem.pk)
            problem.problem_latex = newtexcode(problem.problem_text,problem.label)
            problem.save()
            return redirect('../detailedview/'+str(problem.pk)+'/')
    else:
        form = AddProblemForm(instance=prob)
        return render(request, 'problemeditor/addview.html', {'form': form, 'nbar': 'problemeditor'})

@login_required
def pasttestsview(request):
    F=FinalTest.objects.order_by('year')
    return render(request,'problemeditor/pasttestsview.html',{'pasttests':F,'nbar':'pasttests'})

@login_required
def viewpasttest(request,pk):
    T=get_object_or_404(FinalTest,pk=pk)
    probs=T.problems.order_by('difficulty')
    return render(request,'problemeditor/pasttest.html',{'year':T.year,'nbar':'pasttests','problems':probs})

@login_required
def publishview(request,year):
    problems = Problem.objects.filter(problem_status='PN')
    if request.method == "POST":
        T=FinalTest(year=year)
        T.save()        
        for p in problems:
            T.problems.add(p)
            p.problem_status='XX'
            p.save()
        T.save()
        return redirect('/pasttests/')
    return render(request,'problemeditor/publishview.html',{'year':year,'nbar':'pasttests','problems':problems})    


@login_required
def test_as_pdf(request, pk):
    test = get_object_or_404(FinalTest, pk=pk)
    P=test.problems.order_by('difficulty')
    context = Context({  
            'name':test.year+' UMO',
            'rows':P,
            'pk':pk,
            })
    asyf = open(settings.BASE_DIR+'/asymptote.sty','r')
    asyr = asyf.read()
    asyf.close()
    template = get_template('problemeditor/my_latex_template.tex')
    rendered_tpl = template.render(context).encode('utf-8')  
    # Python3 only. For python2 check out the docs!
    with tempfile.TemporaryDirectory() as tempdir:
        # Create subprocess, supress output with PIPE and
        # run latex twice to generate the TOC properly.
        # Finally read the generated pdf.
        fa=open(os.path.join(tempdir,'asymptote.sty'),'w')
        fa.write(asyr)
        fa.close()
        logger.debug(os.listdir(tempdir))
        context = Context({  
                'name':test.year+' UMO',
                'rows':P,
                'pk':pk,
                'tempdirect':tempdir,
                })
        template = get_template('problemeditor/my_latex_template.tex')
        rendered_tpl = template.render(context).encode('utf-8')  
        ftex=open(os.path.join(tempdir,'texput.tex'),'wb')
        ftex.write(rendered_tpl)
        ftex.close()
        logger.debug(os.listdir(tempdir))
        for i in range(1):
            process = Popen(
                ['pdflatex', 'texput.tex'],
                stdin=PIPE,
                stdout=PIPE,
                cwd = tempdir,
            )
            stdout_value = process.communicate()[0]
        L=os.listdir(tempdir)
        logger.debug(os.listdir(tempdir))

        for i in range(0,len(L)):
            if L[i][-4:]=='.asy':
                process1 = Popen(
                    ['asy', L[i]],
                    stdin = PIPE,
                    stdout = PIPE,
                    cwd = tempdir,
                    )
                stdout_value = process1.communicate()[0]
        logger.debug(os.listdir(tempdir))
        for i in range(2):
            process2 = Popen(
                ['pdflatex', 'texput.tex'],
                stdin=PIPE,
                stdout=PIPE,
                cwd = tempdir,
            )
            stdout_value = process2.communicate()[0]
        logger.debug(os.listdir(tempdir))
        with open(os.path.join(tempdir, 'texput.pdf'), 'rb') as f:
            pdf = f.read()
    r = HttpResponse(content_type='application/pdf')  
    r.write(pdf)
    return r
