from django.conf.urls import include,url

from . import views
#from .forms import AddProblemForm1,AddProblemForm2MC,AddProblemForm2SA,AddProblemForm2PF,AddProblemForm2MCSA,AddProblemForm3,ChangeQuestionTypeForm1,ChangeQuestionTypeForm2MC,ChangeQuestionTypeForm2SA,ChangeQuestionTypeForm2PF,ChangeQuestionTypeForm2MCSA
#from .views import AddProblemWizard,ChangeQuestionTypeWizard,show_mc_form_condition,show_sa_form_condition,show_pf_form_condition,show_mcsa_form_condition
#from .views import show_mc_form_condition2,show_sa_form_condition2,show_pf_form_condition2,show_mcsa_form_condition2



urlpatterns = [
    url(r'^$', views.index_view, name='indexview'),#done
    url(r'^detailedview/(?P<pk>\w+)/$', views.detailedproblemview, name='detailedproblemview'),
    url(r'^detailedview/(?P<pk>\w+)/edittext/$', views.editproblemtextpkview, name='editproblemtextpkview'),
    url(r'^detailedview/(?P<pk>\w+)/edittext/(?P<vpk>\w+)/$', views.editproblemtextpkview, name='editproblemtextpkview'),
    url(r'^detailedview/(?P<pk>\w+)/editsolution/(?P<spk>\w+)/$', views.editsolutionpkview, name='editsolutionpkview'),
    url(r'^detailedview/(?P<pk>\w+)/newsolution/$', views.newsolutionpkview, name='newsolutionpkview'),
    url(r'^detailedview/(?P<pk>\w+)/deletesolution/(?P<spk>\w+)/$', views.deletesolutionpkview, name='deletesolutionpkview'),
    url(r'^detailedview/(?P<pk>\w+)/newcomment/$', views.newcommentpkview, name='newcommentpkview'),
    url(r'^detailedview/(?P<pk>\w+)/deletecomment/(?P<cpk>\w+)/$', views.deletecommentpkview, name='deletecommentpkview'),
    url(r'^detailedview/(?P<pk>\w+)/newversion/$',views.newversionview,name='newversionview'),#done
    url(r'^detailedview/(?P<pk>\w+)/(?P<vpk>\w+)/newsolution/$', views.newsolutionvpkview, name='newsolutionvpkview'),
    url(r'^detailedview/(?P<pk>\w+)/(?P<vpk>\w+)/editsolution/(?P<spk>\w+)/$', views.editsolutionvpkview, name='editsolutionvpkview'),
    url(r'^detailedview/(?P<pk>\w+)/(?P<vpk>\w+)/deletesolution/(?P<spk>\w+)/$', views.deletesolutionvpkview, name='deletesolutionvpkview'),
    url(r'^addproblem/$',views.addproblemview,name='addproblemview'),#done
    url(r'^pasttests/$',views.pasttestsview,name='pasttests'),
    url(r'^pasttests/(?P<pk>\w+)/$',views.viewpasttest,name='viewpasttest'),
    url(r'^pasttests/pdfs/(?P<pk>\w+)/$',views.test_as_pdf,name='test_as_pdf'),
    url(r'^publish/(?P<year>\w+)/$',views.publishview,name='publishview'),
    url(r'^mocklists/$',views.mocklistsview,name='mocklistsview'),
    url(r'^mocklists/(?P<pk>\w+)/$',views.mocklist,name='mocklist'),
    url(r'^mocklists/pdfs/(?P<pk>\w+)/$',views.shortlist_as_pdf,name='mocklist_pdf'),
#    url(r'^detailedview/(?P<pk>\w+)/editreview/(?P<apk>\w+)/$', views.editreviewpkview, name='editreviewpkview'),
#    url(r'^detailedview/(?P<pk>\w+)/newreview/$', views.newreviewpkview, name='newreviewpkview'),

]
