from django.shortcuts import render,render_to_response, get_object_or_404,redirect
from django.http import HttpResponse,HttpResponseRedirect,Http404,JsonResponse
from django.template import loader,RequestContext,Context
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.admin.models import LogEntry, ADDITION,CHANGE,DELETION
from django.contrib.contenttypes.models import ContentType


from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.admin import User
from django.views.generic import DeleteView
from django.urls import reverse_lazy
from django.contrib.auth import update_session_auth_hash


from formtools.wizard.views import SessionWizardView

from .models import Problem, Topic,  Solution,Comment,ProblemStatus,FinalTest,ProblemVersion,ShortList,StatusTopic
from .forms import SolutionForm,ProblemTextForm,AddProblemForm,DetailedProblemForm,CommentForm,DiffMoveProblemForm,NewVersionForm,ShortListModelForm,EditSolutionForm
from .utils import goodtag,goodurl,newtexcode,newsoltexcode,compileasy,compiletikz

from django.template.loader import get_template

from subprocess import Popen,PIPE
import tempfile
import os

from datetime import datetime,timedelta

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
    context={}
    if request.method == "GET":
        if request.GET.get('difficulty') == '1':
            context['difficulty'] = '1'
        elif request.GET.get('difficulty') == '2':
            context['difficulty'] = '2'
        elif request.GET.get('difficulty') == '3':
            context['difficulty'] = '3'
        elif request.GET.get('difficulty') == '4':
            context['difficulty'] = '4'
        elif request.GET.get('difficulty') == '5':
            context['difficulty'] = '5'
        elif request.GET.get('difficulty') == '6':
            context['difficulty'] = '6'

#    template = loader.get_template('problemeditor/typeview.html')

    allcats = (
        ('New Problems', 'NP', StatusTopic.objects.filter(status='NP')),
        ('Proposed for Current Year', 'PN', StatusTopic.objects.filter(status='PN')),
        ('Proposed for Future Year', 'PL', StatusTopic.objects.filter(status='PL')),
        ('Has Potential', 'MI', StatusTopic.objects.filter(status='MI')),
        ('Needs Major Revision', 'MJ', StatusTopic.objects.filter(status='MJ'))
        )
    

    log = LogEntry.objects.filter(change_message__contains="detailedview").filter(action_time__date__gte = datetime.today().date()-timedelta(days=7))

    context['log'] = log
    context['mklists'] = ShortList.objects.filter(archived=False)
    context['allcats'] = allcats
    context['nbar'] = 'problemeditor'
    context['request'] = request
    return render(request,'problemeditor/typeview.html',context)

#HttpResponse(template.render(context,request))


@login_required
def index_view2(request):
    context={}
    f = request.GET

    all_problems = Problem.objects.all()
    if request.method == "GET":
        if request.GET.get('difficulty') == '1':
            all_problems = all_problems.filter(current_version__difficulty=1)
            context['difficulty'] = 1
        elif request.GET.get('difficulty') == '2':
            all_problems = all_problems.filter(current_version__difficulty=2)
            context['difficulty'] = 2
        elif request.GET.get('difficulty') == '3':
            all_problems = all_problems.filter(current_version__difficulty=3)
            context['difficulty'] = 3
        elif request.GET.get('difficulty') == '4':
            all_problems = all_problems.filter(current_version__difficulty=4)
            context['difficulty'] = 4
        elif request.GET.get('difficulty') == '5':
            all_problems = all_problems.filter(current_version__difficulty=5)
            context['difficulty'] = 5
        elif request.GET.get('difficulty') == '6':
            all_problems = all_problems.filter(current_version__difficulty=6)
            context['difficulty'] = 6


    new_problems = all_problems.filter(problem_status='NP')
    propose_now = all_problems.filter(problem_status='PN')
    propose_later = all_problems.filter(problem_status='PL')
    needs_minor = all_problems.filter(problem_status='MI')
    needs_major = all_problems.filter(problem_status='MJ')
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
    template=loader.get_template('problemeditor/typeview2.html')
#    context= {'pna' : pna, 'pla' : pla, 'mia': mia, 'mja' : mja,
#              'pnc' : pnc, 'plc' : plc, 'mic': mic, 'mjc' : mjc,
#              'png' : png, 'plg' : plg, 'mig': mig, 'mjg' : mjg,
#              'pnn' : pnn, 'pln' : pln, 'min': min, 'mjn' : mjn,
#              'pnga' : pnga, 'plga' : plga, 'miga': miga, 'mjga' : mjga,
#              'pno' : pno, 'plo' : plo, 'mio': mio, 'mjo' : mjo, 'nbar': 'problemeditor'}
    allcats= (
        ('New Problems','NP',
         ((npa,'Algebra','AL'),(npc,'Combinatorics','CO'),(npga,'Games','GA'),(npg,'Geometry','GE'),(npn,'Number Theory','NT'),(npo,'Other','OT'))),
        ('Proposed for Current Year','PN',
         ((pna,'Algebra','AL'),(pnc,'Combinatorics','CO'),(pnga,'Games','GA'),(png,'Geometry','GE'),(pnn,'Number Theory','NT'),(pno,'Other','OT'))),
        ('Proposed for Future Year','PL',
         ((pla,'Algebra','AL'),(plc,'Combinatorics','CO'),(plga,'Games','GA'),(plg,'Geometry','GE'),(pln,'Number Theory','NT'),(plo,'Other','OT'))),
        ('Has Potential','MI',
         ((mia,'Algebra','AL'),(mic,'Combinatorics','CO'),(miga,'Games','GA'),(mig,'Geometry','GE'),(min,'Number Theory','NT'),(mio,'Other','OT'))),
        ('Needs Major Revision','MJ',
         ((mja,'Algebra','AL'),(mjc,'Combinatorics','CO'),(mjga,'Games','GA'),(mjg,'Geometry','GE'),(mjn,'Number Theory','NT'),(mjo,'Other','OT'))),
        )
#    currtablecounts=[]
#    goodtablecounts=[]
#    all_good_probs = Problem.objects.filter(problem_status__in = ['PN','NP','MJ','MI','PL'])
#    all_curr_probs = Problem.objects.filter(problem_status__in = L)#['PN','NP','PL'])
#    topics = ['Algebra','Combinatorics','Games','Geometry','Number Theory','Other']
#    for top in topics:
#        goodcounts=[] 
#        currcounts=[]
#        goods = all_good_probs.filter(topic=top)
#        currs = all_curr_probs.filter(topic=top)
#        for i in range(1,7):
#            goodcounts.append(goods.filter(difficulty=str(i)).count())
#            currcounts.append(currs.filter(difficulty=str(i)).count())
#        goodcounts.append(goods.count())
#        currcounts.append(currs.count())
#        currtablecounts.append((top,currcounts))
#        goodtablecounts.append((top,goodcounts))
#    goodcounts=[] 
#    currcounts=[]
#    for i in range(1,7):
#        goodcounts.append(all_good_probs.filter(difficulty=str(i)).count())
#        currcounts.append(all_curr_probs.filter(difficulty=str(i)).count())
#    goodcounts.append(all_good_probs.count())
#    currcounts.append(all_curr_probs.count())
#    currtablecounts.append(('Total',currcounts))
#    goodtablecounts.append(('Total',goodcounts))


    
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

    log = LogEntry.objects.filter(change_message__contains="detailedview").filter(action_time__date__gte=datetime.today().date()-timedelta(days=7))

#    userlog=[]
#    for ent in log:
        
    context['log'] = log

    context['mklists'] = ShortList.objects.filter(archived=False)

    context['allcats'] = allcats
    context['nbar'] = 'problemeditor'
#    context['current'] = currtablecounts
#    context['good'] = goodtablecounts
    context['request'] = request
#    context['included_cats'] = L
    return HttpResponse(template.render(context,request))


@login_required
def get_new_table(request):
    context = {}
    #modify this to take advantage of statustopic.
    f = request.GET
    L = []
    if 'NP' in f:
        L.append('NP')
    if 'PN' in f:
        L.append('PN')
    if 'PL' in f:
        L.append('PL')
    if 'MI' in f:
        L.append('MI')
    if 'MJ' in f:
        L.append('MJ')
    if len(L) == 0:
        L = ['NP','PN']
    all_problems = Problem.objects.all()
    if request.method == "GET":
        if request.GET.get('difficulty') == '1':
            all_problems = all_problems.filter(current_version__difficulty=1)
            context['difficulty'] = 1
        elif request.GET.get('difficulty') == '2':
            all_problems = all_problems.filter(current_version__difficulty=2)
            context['difficulty'] = 2
        elif request.GET.get('difficulty') == '3':
            all_problems = all_problems.filter(current_version__difficulty=3)
            context['difficulty'] = 3
        elif request.GET.get('difficulty') == '4':
            all_problems = all_problems.filter(current_version__difficulty=4)
            context['difficulty'] = 4
        elif request.GET.get('difficulty') == '5':
            all_problems = all_problems.filter(current_version__difficulty=5)
            context['difficulty'] = 5
        elif request.GET.get('difficulty') == '6':
            all_problems = all_problems.filter(current_version__difficulty=6)
            context['difficulty'] = 6


    new_problems = all_problems.filter(problem_status='NP')
    propose_now = all_problems.filter(problem_status='PN')
    propose_later = all_problems.filter(problem_status='PL')
    needs_minor = all_problems.filter(problem_status='MI')
    needs_major = all_problems.filter(problem_status='MJ')
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

    currtablecounts=[]
    all_curr_probs = Problem.objects.filter(problem_status__in = L)#['PN','NP','PL'])
    topics = ['Algebra','Combinatorics','Games','Geometry','Number Theory','Other']
    for top in topics:
        currcounts=[]
        currs = all_curr_probs.filter(topic=top)
        for i in range(1,7):
            currcounts.append(currs.filter(difficulty=str(i)).count())
        currcounts.append(currs.count())
        currtablecounts.append((top,currcounts))
    currcounts=[]
    for i in range(1,7):
        currcounts.append(all_curr_probs.filter(difficulty=str(i)).count())
    currcounts.append(all_curr_probs.count())
    currtablecounts.append(('Total',currcounts))


    

    context['current'] = currtablecounts



    return JsonResponse({'table':render_to_string('problemeditor/typeview-dynamictable.html',context)})

@login_required
def change_difficulty(request):
    form = request.POST
    pk = form['pk']
    prob = get_object_or_404(Problem,pk=pk)
    prob.difficulty = form['diff']
    curr_version = prob.current_version
    curr_version.difficulty = form['diff']
    prob.save()
    curr_version.save()
    return JsonResponse({})

@login_required
def change_status(request):
    form = request.POST
    pk = form['pk']
    prob = get_object_or_404(Problem,pk=pk)
    old_stat = prob.problem_status_new.status
    new_stat = get_object_or_404(ProblemStatus,status = form['stat'])
    prob.problem_status_new = new_stat
    prob.problem_status = form['stat']
    prob.status_topic = StatusTopic.objects.get(topic = prob.topic_new.topic,status = form['stat'])
    prob.save()
    return JsonResponse({'prob-card': render_to_string('problemeditor/problemrow.html',{'p':prob,'request':request,'mklists':ShortList.objects.filter(archived=False)}),'add-here':form['stat']+'-'+prob.topic_new.short_topic,'subtract-here':old_stat+'-'+prob.topic_new.short_topic})

@login_required
def change_topic(request):
    form = request.POST
    pk = form['pk']
    prob = get_object_or_404(Problem,pk=pk)
    old_topic = prob.topic_new.short_topic# change topic; change topicstatus.
    prob.topic = form['topic']
    new_topic = get_object_or_404(Topic,topic = form['topic'])
    prob.topic_new = new_topic
    prob.status_topic = StatusTopic.objects.get(topic = form['topic'],status = prob.status_topic.status)
    prob.save()
    return JsonResponse({'prob-card': render_to_string('problemeditor/problemrow.html',{'p':prob,'request':request,'mklists':ShortList.objects.filter(archived=False)}),'add-here':prob.problem_status+'-'+prob.topic_new.short_topic,'subtract-here':prob.problem_status+'-'+old_topic})

@login_required
def add_to_list(request):
    form = request.POST
    pk = form['pk']
    prob = get_object_or_404(Problem,pk=pk)
    sl = ShortList.objects.get(pk=form['list_pk'])
    if sl.problems.filter(pk=pk).exists() == False:
        sl.problems.add(prob)
        sl.save()
        return JsonResponse({'status': 1})
    return JsonResponse({'status': 0})



@login_required
def editproblemtextpkview(request,**kwargs):#Needs to be in terms of "Versions" (is done?)
    pk = kwargs['pk']
    prob = get_object_or_404(Problem, pk=pk)
    if 'vpk' in kwargs:
        vers = get_object_or_404(ProblemVersion,pk=kwargs['vpk'])
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
            LogEntry.objects.log_action(
                user_id = request.user.id,
                content_type_id = ContentType.objects.get_for_model(sol).pk,
                object_id = sol.id,
                object_repr = sol.author_name+" added a solution to "+prob.label,
                action_flag = ADDITION,
                change_message = "/detailedview/"+str(prob.pk)+'/',
                )
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
    prob = get_object_or_404(Problem, pk=pk)
    sol = get_object_or_404(Solution, pk=spk)
    prob.current_version.solutions.remove(sol)
    prob.current_version.deleted_solutions.add(sol)
    prob.save()
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
    pk = kwargs['pk']
    prob = get_object_or_404(Problem, pk=pk)
    com_num = prob.comments.count()+1
    if request.method == "POST":
        com_form = CommentForm(request.POST)
        if com_form.is_valid():
            com = com_form.save(commit = False)
            com.comment_number = com_num
            com.author = request.user
            com.problem_label = prob.label
            com.save()
            prob.comments.add(com)
            prob.save()
            LogEntry.objects.log_action(
                user_id = request.user.id,
                content_type_id = ContentType.objects.get_for_model(com).pk,
                object_id = com.id,
                object_repr = com.author_name+" added a comment to "+prob.label,
                action_flag = ADDITION,
                change_message = "/detailedview/"+str(prob.pk)+'/',
                )
            return redirect('../')
    else:
        com = Comment(comment_text = '', comment_number = com_num, problem_label = prob.label)
        com_form = CommentForm(instance = com)

    return render(request, 'problemeditor/newcom.html', {'form': com_form, 'nbar': 'problemeditor','problem':prob})



@login_required
def detailedproblemview(request,**kwargs):
    pk = kwargs['pk']
    prob = get_object_or_404(Problem, pk = pk)
    if request.method == "POST":
        versions = prob.versions.all()
        for i in versions:
            if i.label in request.POST:
                prob.current_version = i
                prob.save()
    context = {}
    breadcrumbs=[]
#    form=DetailedProblemForm(instance=prob)
    #sols...
    sols = prob.current_version.solutions.all()
    context['sols'] = sols
    #coms...
    coms=prob.comments.all()
    context['coms'] = coms
    #approvals
#    status=prob.problem_status
#    context['apprs']=apprs
    #other
    context['problem'] = prob
    context['nbar'] = 'problemeditor'
#    context['form']=form
    context['breadcrumbs'] = breadcrumbs
    return render(request, 'problemeditor/detailedview.html', context)

@login_required
def newversionview(request,pk):#args
    problem = get_object_or_404(Problem, pk = pk)
    vers = ProblemVersion()
    if request.method == "POST":
        form = NewVersionForm(request.POST, instance = vers)
        if form.is_valid():
            version = form.save()
            version.save()
            version.version_number = problem.top_version_number + 1
            version.save()
            version.label = 'Problem ' + str(problem.pk) + 'v' + str(version.version_number)
            version.save()
            version.problem_latex = newtexcode(version.problem_text,version.label)#requires version.label...need to redo image naming conventions
            version.authors.add(request.user)
            version.save()
            problem.versions.add(version)
            problem.top_version_number += 1
            problem.save()
            LogEntry.objects.log_action(
                user_id = request.user.id,
                content_type_id = ContentType.objects.get_for_model(version).pk,
                object_id = version.id,
                object_repr = version.author_name + " added a new version to "+problem.label,
                action_flag = ADDITION,
                change_message = "/detailedview/" + str(problem.pk) + '/',
                )
            return redirect('../')
    else:
        form = NewVersionForm(instance = vers)
        return render(request, 'problemeditor/newversionview.html', {'form': form, 'nbar': 'problemeditor','problem' : problem})

@login_required
def addproblemview(request):
    prob = Problem()
    if request.method == "POST":
        form = AddProblemForm(request.POST, instance = prob)
        if form.is_valid():
            problem = form.save()
            problem.save()
            problem.label = 'Problem ' + str(problem.pk)
            problem.problem_latex = newtexcode(problem.problem_text,problem.label)
            problem.problem_status = 'NP'
            problem.problem_status_new = ProblemStatus.objects.get(status = "NP")
            problem.topic_new = Topic.objects.get(topic = problem.topic)
            problem.status_topic = StatusTopic.objects.get(status = 'NP',topic = problem.topic)
            problem.save()
            pv = ProblemVersion(
                difficulty = problem.difficulty,
                problem_text = problem.problem_text,
                problem_latex = problem.problem_latex,
                version_number = 1,
                author_name = problem.author_name,
                label = problem.label + 'v1'
                )
            pv.save()
            pv.authors.add(request.user)
            pv.save()
            problem.versions.add(pv)
            problem.current_version = pv
            problem.top_version_number = 1
            problem.save()
            LogEntry.objects.log_action(
                user_id = request.user.id,
                content_type_id = ContentType.objects.get_for_model(problem).pk,
                object_id = problem.id,
                object_repr = problem.author_name+" added a problem ("+problem.label+")",
                action_flag = ADDITION,
                change_message = "/detailedview/"+str(problem.pk)+'/',
                )
            return redirect('../detailedview/'+str(problem.pk)+'/')
    else:
        form = AddProblemForm(instance = prob)
        return render(request, 'problemeditor/addview.html', {'form': form, 'nbar': 'problemeditor'})

@login_required
def pasttestsview(request):
    F = FinalTest.objects.order_by('year')
    return render(request,'problemeditor/pasttestsview.html',{'pasttests':F,'nbar':'pasttests'})

@login_required
def viewpasttest(request,pk):
    T = get_object_or_404(FinalTest,pk=pk)
    probs = T.problems.order_by('difficulty')
    return render(request,'problemeditor/pasttest.html',{'year':T.year,'nbar':'pasttests','problems':probs})

@login_required
def publishview(request,year):
    problems = Problem.objects.filter(problem_status='PN')
    if request.method == "POST":
        T = FinalTest(year = year)
        T.save()        
        for p in problems:
            T.problems.add(p)
            p.problem_status = 'XX'
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
        fa = open(os.path.join(tempdir,'asymptote.sty'),'w')
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
        ftex = open(os.path.join(tempdir,'texput.tex'),'wb')
        ftex.write(rendered_tpl)
        ftex.close()
        logger.debug(os.listdir(tempdir))
        for i in range(1):
            process = Popen(
                ['pdflatex', 'texput.tex'],
                stdin = PIPE,
                stdout = PIPE,
                cwd = tempdir,
            )
            stdout_value = process.communicate()[0]
        L = os.listdir(tempdir)
        logger.debug(os.listdir(tempdir))

        for i in range(0,len(L)):
            if L[i][-4:] == '.asy':
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
                stdin = PIPE,
                stdout = PIPE,
                cwd = tempdir,
            )
            stdout_value = process2.communicate()[0]
        logger.debug(os.listdir(tempdir))
        with open(os.path.join(tempdir, 'texput.pdf'), 'rb') as f:
            pdf = f.read()
    r = HttpResponse(content_type = 'application/pdf')  
    r.write(pdf)
    return r

@login_required
def mocklistsview(request):
    if request.method == 'POST':
        shortlist_form = ShortListModelForm(request.POST)
        if shortlist_form.is_valid():
            shortlist = shortlist_form.save()
            shortlist.author = request.user
            shortlist.save()
    F = ShortList.objects.filter(archived = False)
    archived = ShortList.objects.filter(archived = True)
    form = ShortListModelForm()
    return render(request,'problemeditor/mocklistsview.html',{'mocklists':F,'nbar':'mocklists','form':form,'archived_mocklists':archived})


@login_required
def mocklist(request,pk):
    T = get_object_or_404(ShortList,pk = pk)
    probs = T.problems.order_by('current_version__difficulty')
    return render(request,'problemeditor/mocklist.html',{'nbar':'mocklists','problems':probs,'mocklist' : T, 'mklists': ShortList.objects.filter(archived=False)})

@login_required
def remove_from_list(request):
    form = request.POST
    pk = form['pk']
    T = get_object_or_404(ShortList,pk = pk)
    ppk = form['ppk']
    prob = Problem.objects.get(pk = ppk)
    T.problems.remove(prob)
    T.save()
    return JsonResponse({})



@login_required
def shortlist_as_pdf(request, pk):
    shortlist = get_object_or_404(ShortList, pk = pk)
    P = shortlist.problems.order_by('difficulty')
    context = Context({  
            'name':shortlist.name,
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
        fa = open(os.path.join(tempdir,'asymptote.sty'),'w')
        fa.write(asyr)
        fa.close()
        logger.debug(os.listdir(tempdir))
        context = Context({  
                'name':shortlist.name,
                'rows':P,
                'pk':pk,
                'tempdirect':tempdir,
                })
        template = get_template('problemeditor/my_latex_template.tex')
        rendered_tpl = template.render(context).encode('utf-8')  
        ftex = open(os.path.join(tempdir,'texput.tex'),'wb')
        ftex.write(rendered_tpl)
        ftex.close()
        logger.debug(os.listdir(tempdir))
        for i in range(1):
            process = Popen(
                ['pdflatex', 'texput.tex'],
                stdin = PIPE,
                stdout = PIPE,
                cwd = tempdir,
            )
            stdout_value = process.communicate()[0]
        L = os.listdir(tempdir)
        logger.debug(os.listdir(tempdir))

        for i in range(0,len(L)):
            if L[i][-4:] == '.asy':
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
                stdin = PIPE,
                stdout = PIPE,
                cwd = tempdir,
            )
            stdout_value = process2.communicate()[0]
        logger.debug(os.listdir(tempdir))
        if 'texput.pdf' in os.listdir(tempdir):
            with open(os.path.join(tempdir, 'texput.pdf'), 'rb') as f:
                pdf = f.read()
                r = HttpResponse(content_type = 'application/pdf')  
                r.write(pdf)
                return r
        else:
            with open(os.path.join(tempdir,'texput.log')) as f:
                error_text = f.read()
                return render(request,'problemeditor/latex_errors.html',{'nbar':'mocklists','mocklist':shortlist,'error_text':error_text})

@login_required
def new_solution(request):
    pk = request.GET.get('pk')
    prob = get_object_or_404(Problem,pk = pk)
    return JsonResponse({'modal-html':render_to_string('problemeditor/modal-new-solution.html',{'prob':prob})})

@login_required
def load_solutions(request):
    pk = request.GET.get('pk')
    prob = get_object_or_404(Problem,pk = pk)
    return JsonResponse({'modal-html':render_to_string('problemeditor/modal-view-solutions.html',{'prob':prob})})

@login_required
def save_new_solution(request,**kwargs):
    pk = request.POST.get('ns-pk','')
    prob =  get_object_or_404(Problem,pk=pk)
    sol_num = prob.current_version.top_solution_number+1
    cv = prob.current_version
    cv.top_solution_number = sol_num
    cv.save();

    sol_text = request.POST.get("new_solution_text","")
    author_name = request.POST.get("author_name","")
    sol = Solution(solution_text = sol_text,solution_number = sol_num,problem_label = cv.label, author_name = author_name)
    sol.save()
    sol.authors.add(request.user)
    sol.save()
    compileasy(sol.solution_text,cv.label,sol = 'sol'+str(sol_num))
    compiletikz(sol.solution_text,cv.label,sol = 'sol'+str(sol_num))
    sol.solution_latex = newsoltexcode(sol.solution_text,cv.label+'sol'+str(sol.solution_number))
    sol.save()
    cv.solutions.add(sol)
    cv.save()

    LogEntry.objects.log_action(
        user_id = request.user.id,
        content_type_id = ContentType.objects.get_for_model(sol).pk,
        object_id = sol.id,
        object_repr = sol.author_name+" added a solution to "+prob.label,
        action_flag = ADDITION,
        change_message = "/detailedview/"+str(prob.pk)+'/',
        )
    return JsonResponse({'pk':pk,'sol_count':prob.current_version.solutions.count()})

@login_required
def delete_sol(request,**kwargs):
    pk = request.POST.get('pk','')
    spk = request.POST.get('spk','')
    prob =  get_object_or_404(Problem,pk = pk)
    sol =  get_object_or_404(Solution,pk = spk)
    prob.current_version.solutions.remove(sol)
    prob.current_version.deleted_solutions.add(sol)
    prob.save()
    return JsonResponse({'deleted':1,'sol_count': prob.current_version.solutions.count()})

@login_required
def load_edit_sol(request,**kwargs):
    pk = request.POST.get('pk','')
    spk = request.POST.get('spk','')
    prob = get_object_or_404(Problem,pk = pk)
    sol = get_object_or_404(Solution,pk = spk)
    form = EditSolutionForm(instance = sol)
    return JsonResponse({'sol_form':render_to_string('problemeditor/edit_sol_form.html',{'form':form,'prob':prob})})

@login_required
def save_sol(request,**kwargs):
    pk = request.POST.get('pk','')
    spk = request.POST.get('spk','')
    prob = get_object_or_404(Problem,pk = pk)
    sol = get_object_or_404(Solution,pk = spk)
    cv = prob.current_version

    sol.solution_text = request.POST.get('solution_text')
    sol.authors.add(request.user)
    sol.save()
    compileasy(sol.solution_text,cv.label,sol = 'sol'+str(sol.solution_number))
    compiletikz(sol.solution_text,cv.label,sol = 'sol'+str(sol.solution_number))
    sol.solution_latex = newsoltexcode(sol.solution_text,cv.label+'sol'+str(sol.solution_number))
    sol.save()
    return JsonResponse({'sol_text':render_to_string('problemeditor/soltext.html',{'solution':sol})})

@login_required
def add_problem(request):
    prob = Problem()
    form = AddProblemForm(instance = prob)
    return JsonResponse({'modal-html':render_to_string('problemeditor/modal-add-problem.html',{'form':form})})


@login_required
def save_new_problem(request):
    prob = Problem()
    form = AddProblemForm(request.POST, instance=prob)
    if form.is_valid():
        problem = form.save()
        problem.save()
        problem.label = 'Problem '+str(problem.pk)
        problem.problem_latex = newtexcode(problem.problem_text,problem.label)
        problem.problem_status='NP'
        problem.problem_status_new = ProblemStatus.objects.get(status = "NP")
        problem.topic_new = Topic.objects.get(topic = problem.topic)
        problem.status_topic = StatusTopic.objects.get(status = 'NP',topic = problem.topic)

        problem.save()
        pv = ProblemVersion(
            difficulty = problem.difficulty,
            problem_text = problem.problem_text,
            problem_latex = problem.problem_latex,
            version_number = 1,
            author_name = problem.author_name,
            label = problem.label+'v1'
            )
        pv.save()
        pv.authors.add(request.user)
        pv.save()
        problem.versions.add(pv)
        problem.current_version = pv
        problem.top_version_number = 1
        problem.save()
        LogEntry.objects.log_action(
            user_id = request.user.id,
            content_type_id = ContentType.objects.get_for_model(problem).pk,
            object_id = problem.id,
            object_repr = problem.author_name+" added a problem ("+problem.label+")",
            action_flag = ADDITION,
            change_message = "/detailedview/"+str(problem.pk)+'/',
            )
        D = {
            'Algebra':'AL',
            'Combinatorics':'CO',
            'Games':'GA',
            'Geometry':'GE',
            'Number Theory': 'NT',
            'Other':'OT',
            }
        return JsonResponse({'prob-card': render_to_string('problemeditor/problemrow.html',{'p':problem,'request':request,'mklists':ShortList.objects.filter(archived=False)}),'add-here':'NP'+'-'+problem.topic_new.short_topic,'pk':problem.pk})
    return JsonResponse({})
#comment-body.html


@login_required
def new_comment(request):
    pk = request.GET.get('pk')
    prob = get_object_or_404(Problem,pk = pk)
    return JsonResponse({'modal-html':render_to_string('problemeditor/modal-new-comment.html',{'prob':prob})})

@login_required
def save_new_comment(request,**kwargs):
    pk = request.POST.get('ns-pk','')
    prob =  get_object_or_404(Problem,pk=pk)
    com_num = prob.comments.count()+1

    com_text = request.POST.get("comment_text","")
    author_name = request.POST.get("author_name","")
    com = Comment(comment_text = com_text, author_name = author_name, comment_number = com_num, author = request.user,problem_label = prob.label)
    com.save()
    prob.comments.add(com)
    prob.save()
    LogEntry.objects.log_action(
        user_id = request.user.id,
        content_type_id = ContentType.objects.get_for_model(com).pk,
        object_id = com.id,
        object_repr = com.author_name+" added a comment to "+prob.label,
        action_flag = ADDITION,
        change_message = "/detailedview/"+str(prob.pk)+'/',
        )
    return JsonResponse({'pk':pk,'com_count':prob.comments.count(),'com-html': render_to_string('problemeditor/comment-body.html',{'request':request,'c': com,'p':prob})})

@login_required
def remove_comment(request,**kwargs):
    pk = request.POST.get('pk','')
    cpk = request.POST.get('cpk','')
    prob =  get_object_or_404(Problem,pk=pk)
    com =  get_object_or_404(Comment,pk=cpk)
    com.delete()
#    prob.comments.remove(com)
#    prob.deleted_comments.add(com)
#    prob.save()
    return JsonResponse({'deleted':1,'com_count': prob.comments.count()})

@login_required
def refresh_status(request):
    st = request.POST.get('st')
    diff = request.POST.get("diff")
    problem_status = get_object_or_404(ProblemStatus,status = st)
    plist = StatusTopic.objects.filter(status = st)
    context = {}
    if diff != '':
        context['difficulty'] = diff
    context['mklists'] = ShortList.objects.filter(archived=False)
    context['plist'] = plist
    context['request'] = request
    return JsonResponse({'refreshed-html':render_to_string('problemeditor/typeview-statusdiv.html',context)})

@login_required
def edit_problemtext(request,**kwargs):
    pk = request.POST.get('pk','')
    prob = get_object_or_404(Problem,pk = pk)
    form = ProblemTextForm(instance = prob.current_version)
    return JsonResponse({'modal-html':render_to_string('problemeditor/modal-edit-problemtext.html',{'form':form,'prob':prob})})


@login_required
def save_problemtext(request,**kwargs):
    pk = request.POST.get('pk','')
    prob =  get_object_or_404(Problem,pk=pk)
    cv = prob.current_version
    form = ProblemTextForm(request.POST,instance = cv)
    if form.is_valid():
        cvv = form.save()
        cvv.problem_latex = newtexcode(cvv.problem_text,cvv.label)
        cvv.save()
        compileasy(cvv.problem_text,cvv.label)
        compiletikz(cvv.problem_text,cvv.label)
    return JsonResponse({'pk':pk,'prob-html': render_to_string('problemeditor/ptext.html',{'p':prob})})

@login_required
def archive_mocklist(request):
    pk = request.POST.get('pk')
    mklist = get_object_or_404(ShortList,pk=pk)
    mklist.archived = True
    mklist.save()
    return JsonResponse({'mocklist-row': render_to_string('problemeditor/mocklist-row.html',{'t':mklist})})

@login_required
def unarchive_mocklist(request):
    pk = request.POST.get('pk')
    mklist = get_object_or_404(ShortList,pk=pk)
    mklist.archived = False
    mklist.save()
    return JsonResponse({'mocklist-row': render_to_string('problemeditor/mocklist-row.html',{'t':mklist})})
