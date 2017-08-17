from django.shortcuts import render,render_to_response, get_object_or_404,redirect
from django.http import HttpResponse,HttpResponseRedirect,Http404
from django.template import loader,RequestContext,Context
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from django.contrib.auth.forms import PasswordChangeForm



from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.admin import User
from django.views.generic import DeleteView
from django.urls import reverse_lazy
from django.contrib.auth import update_session_auth_hash


from formtools.wizard.views import SessionWizardView

from .models import Problem, Topic,  Solution,Comment,ProblemStatus,FinalTest,ProblemVersion
from .forms import SolutionForm,ProblemTextForm,AddProblemForm,DetailedProblemForm,CommentForm,DiffMoveProblemForm,NewVersionForm
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
                pk = i.split('_')[1]
                prob = Problem.objects.get(pk=pk)
                prob.problem_status=form[i]
                prob.save()
            if 'difficulty' in i:
                pk = i.split('_')[1]
                prob = Problem.objects.get(pk=pk)
                prob.difficulty = form[i]
                curr_version = prob.current_version
                curr_version.difficulty = form[i]
                prob.save()
                curr_version.save()
            if 'topic' in i:
                pk = i.split('_')[1]
                prob = Problem.objects.get(pk=pk)
                prob.topic = form[i]
                curr_version = prob.current_version
                curr_version.topic = form[i]
                prob.save()
                curr_version.save()
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
    currtablecounts=[]
    goodtablecounts=[]
    all_good_probs=Problem.objects.filter(problem_status__in=['PN','NP','MJ','MI','PL'])
    all_curr_probs=Problem.objects.filter(problem_status__in=['PN','NP'])
    topics = ['Algebra','Combinatorics','Games','Geometry','Number Theory','Other']
    for top in topics:
        goodcounts=[] 
        currcounts=[]
        goods = all_good_probs.filter(topic=top)
        currs = all_curr_probs.filter(topic=top)
        for i in range(1,7):
            goodcounts.append(goods.filter(difficulty=str(i)).count())
            currcounts.append(currs.filter(difficulty=str(i)).count())
        goodcounts.append(goods.count())
        currcounts.append(currs.count())
        currtablecounts.append((top,currcounts))
        goodtablecounts.append((top,goodcounts))
    goodcounts=[] 
    currcounts=[]
    for i in range(1,7):
        goodcounts.append(all_good_probs.filter(difficulty=str(i)).count())
        currcounts.append(all_curr_probs.filter(difficulty=str(i)).count())
    goodcounts.append(all_good_probs.count())
    currcounts.append(all_curr_probs.count())
    currtablecounts.append(('Total',currcounts))
    goodtablecounts.append(('Total',goodcounts))


    
#    abbrevs= {'Algebra':'A',
#              'Combinatorics':'C',
#              'Games':'Ga',
#              'Geometry':'Ge',
#              'Number Theory':'NT',
#              'Other':'O',}
#    for i in allcats:
#        status=i[0]
#        groups=i[1]
#        pnums=[[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0]]
#        for j in range(0,len(groups)):
#            topic=groups[j]
#            nums=[]
#            li=topic[0]
#            for k in range(1,7):
#                c=li.filter(difficulty=str(k)).count()
#                pnums[k-1][j]=(c,abbrevs[topic[1]],topic[1])

#            pnums.append(nums)
#        allnums.append((i[0],pnums))
    context = {'allcats':allcats,'nbar':'problemeditor','current':currtablecounts,'good':goodtablecounts}
    return HttpResponse(template.render(context,request))


@login_required
def editproblemtextpkview(request,**kwargs):#Needs to be in terms of "Versions" (is done?)
    pk=kwargs['pk']
    prob=get_object_or_404(Problem, pk=pk)
    if 'vpk' in kwargs:
        vers=get_object_or_404(ProblemVersion,pk=kwargs['vpk'])
    else:
        vers=prob.current_version
    if request.method == "POST":
        form = ProblemTextForm(request.POST, instance=vers)
        if form.is_valid():
            version = form.save()
            version.problem_latex = newtexcode(version.problem_text,version.label)
            version.save()
            compileasy(version.problem_text,version.label)
            compiletikz(version.problem_text,version.label)
        if 'vpk' in kwargs:
            return redirect('../../')
        else:
            return redirect('../')
    else:
        form = ProblemTextForm(instance=vers)
    context={}
    context['problem'] = prob
    context['form'] = form
    context['nbar'] = 'problemeditor'
    return render(request, 'problemeditor/editproblemtext.html', context)


@login_required
def newsolutionpkview(request,**kwargs):#Needs to be in terms of "Versions"
    pk=kwargs['pk']
    prob=get_object_or_404(Problem, pk=pk)
    sol_num=prob.current_version.top_solution_number+1
    cv=prob.current_version
    if request.method == "POST":
        sol_form = SolutionForm(request.POST)
        if sol_form.is_valid():
            cv.top_solution_number=sol_num
            cv.save()
            sol = sol_form.save()
            sol.solution_number=sol_num
            sol.authors.add(request.user)
            sol.problem_label=cv.label
            sol.solution_latex = newsoltexcode(sol.solution_text,cv.label+'sol'+str(sol.solution_number))
            sol.save()
            compileasy(sol.solution_text,cv.label,sol='sol'+str(sol_num))
            compiletikz(sol.solution_text,cv.label,sol='sol'+str(sol_num))
            cv.solutions.add(sol)
            cv.save()
        return redirect('../')
    else:
        sol=Solution(solution_text='', solution_number=sol_num, problem_label=cv.label)
        form = SolutionForm(instance=sol)

    return render(request, 'problemeditor/newsol.html', {'form': form, 'nbar': 'problemeditor','problem':prob, 'version' : cv})


@login_required
def editsolutionpkview(request,**kwargs):#Needs to be in terms of "Versions"
    pk=kwargs['pk']
    spk=kwargs['spk']
    prob=get_object_or_404(Problem, pk=pk)
    sol=Solution.objects.get(pk=spk)
    cv=prob.current_version
    if request.method == "POST":
        if request.POST.get("save"):
            sollist=request.POST.getlist('solution_text')
            sol.solution_text=sollist[0]
            sol.authors.add(request.user)
            sol.solution_latex=newsoltexcode(sol.solution_text,cv.label+'sol'+str(sol.solution_number))
            sol.save()
            compileasy(sol.solution_text,cv.label,sol='sol'+str(sol.solution_number))
            compiletikz(sol.solution_text,cv.label,sol='sol'+str(sol.solution_number))
            return redirect('../../')
    form = SolutionForm(instance=sol)
    return render(request, 'problemeditor/editsol.html', {'form': form, 'nbar': 'problemeditor','problem':prob, 'cv':cv})




@login_required
def deletesolutionpkview(request,**kwargs):#If solution_number is kept, this must be modified to adjust.
    pk=kwargs['pk']
    spk=kwargs['spk']
    sol = get_object_or_404(Solution, pk=spk)
    sol.delete()
    return redirect('../../')


@login_required
def newsolutionvpkview(request,**kwargs):#Needs to be in terms of "Versions"
    pk=kwargs['pk']
    vpk=kwargs['vpk']
    prob=get_object_or_404(Problem, pk=pk)
    cv=get_object_or_404(ProblemVersion, pk=vpk)
    sol_num=prob.current_version.top_solution_number+1
    if request.method == "POST":
        sol_form = SolutionForm(request.POST)
        if sol_form.is_valid():
            cv.top_solution_number=sol_num
            cv.save()
            sol = sol_form.save()
            sol.solution_number=sol_num
            sol.authors.add(request.user)
            sol.problem_label=cv.label
            sol.solution_latex = newsoltexcode(sol.solution_text,cv.label+'sol'+str(sol.solution_number))
            sol.save()
            compileasy(sol.solution_text,cv.label,sol='sol'+str(sol_num))
            compiletikz(sol.solution_text,cv.label,sol='sol'+str(sol_num))
            cv.solutions.add(sol)
            cv.save()
        return redirect('../../')
    else:
        sol=Solution(solution_text='', solution_number=sol_num, problem_label=cv.label)
        form = SolutionForm(instance=sol)

    return render(request, 'problemeditor/newsol.html', {'form': form, 'nbar': 'problemeditor','problem':prob, 'version' : cv})


@login_required
def editsolutionvpkview(request,**kwargs):#Needs to be in terms of "Versions"
    pk=kwargs['pk']
    spk=kwargs['spk']
    prob=get_object_or_404(Problem, pk=pk)
    vpk=kwargs['vpk']
    cv=get_object_or_404(ProblemVersion, pk=vpk)
    sol=Solution.objects.get(pk=spk)
    if request.method == "POST":
        if request.POST.get("save"):
            sollist=request.POST.getlist('solution_text')
            sol.solution_text=sollist[0]
            sol.authors.add(request.user)
            sol.solution_latex=newsoltexcode(sol.solution_text,cv.label+'sol'+str(sol.solution_number))
            sol.save()
            compileasy(sol.solution_text,cv.label,sol='sol'+str(sol.solution_number))
            compiletikz(sol.solution_text,cv.label,sol='sol'+str(sol.solution_number))
            return redirect('../../../')
    form = SolutionForm(instance=sol)
    return render(request, 'problemeditor/editsol.html', {'form': form, 'nbar': 'problemeditor','problem':prob,'cv':cv})




@login_required
def deletesolutionvpkview(request,**kwargs):#If solution_number is kept, this must be modified to adjust.
    pk=kwargs['pk']
    spk=kwargs['spk']
    vpk=kwargs['vpk']
    prob=get_object_or_404(Problem, pk=pk)
    sol = get_object_or_404(Solution, pk=spk)
    vers = get_object_or_404(ProblemVersion, pk=vpk)
    sol.delete()
    return redirect('../../../')



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
    if request.method == "POST":
        versions=prob.versions.all()
        for i in versions:
            if i.label in request.POST:
                prob.current_version=i
                prob.save()
    context={}
    breadcrumbs=[]
#    form=DetailedProblemForm(instance=prob)
    #sols...
    sols=prob.current_version.solutions.all()
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
#    context['form']=form
    context['breadcrumbs']=breadcrumbs
    return render(request, 'problemeditor/detailedview.html', context)

@login_required
def newversionview(request,pk):#args
    problem=get_object_or_404(Problem, pk=pk)
    vers=ProblemVersion()
    if request.method == "POST":
        form = NewVersionForm(request.POST, instance=vers)
        if form.is_valid():
            version = form.save()
            version.save()
            version.version_number = problem.top_version_number+1
            version.save()
            version.label = 'Problem '+str(problem.pk)+'v'+str(version.version_number)
            version.save()
            version.problem_latex = newtexcode(version.problem_text,version.label)#requires version.label...need to redo image naming conventions
            version.save()
            problem.versions.add(version)
            problem.top_version_number+=1
            problem.save()
            return redirect('../')
    else:
        form = NewVersionForm(instance=vers)
        return render(request, 'problemeditor/newversionview.html', {'form': form, 'nbar': 'problemeditor','problem' : problem})

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
            problem.problem_status='NP'
            problem.save()
            pv=ProblemVersion(
                difficulty=problem.difficulty,
                problem_text=problem.problem_text,
                problem_latex=problem.problem_latex,
                version_number=1,
                author_name=problem.author_name,
                label=problem.label+'v1'
                )
            pv.save()
            problem.versions.add(pv)
            problem.current_version=pv
            problem.top_version_number=1
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
