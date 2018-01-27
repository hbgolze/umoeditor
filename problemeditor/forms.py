from django import forms
#from django.contrib.auth.models import User
from problemeditor.models import Problem,Solution,Comment,ProblemVersion,ShortList
from .models import Topic

PROBLEM_DIFFICULTY = (
    ('1','1'),
    ('2','2'),
    ('3','3'),
    ('4','4'),
    ('5','5'),
    ('6','6'),
    )

PROBLEM_STATUS = (
    ('NP','New Problem'),
    ('PN','Propose for Current Year'),
    ('PL','Propose for Later Year'),
    ('MI','Has Potential'),
    ('MJ','Needs Major Revision'),
    )

class DetailedProblemForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = ('difficulty',)
    def __init__(self, *args, **kwargs):
        super(DetailedProblemForm, self).__init__(*args, **kwargs)

class ProblemTextForm(forms.ModelForm):
    class Meta:
        model = ProblemVersion
        fields = ('problem_text',)
        widgets = {
            'problem_text': forms.Textarea(attrs={'cols': 120, 'rows': 15,'id' : 'codetext','class':'form-control'}),
            }
    def __init__(self, *args, **kwargs):
        super(ProblemTextForm, self).__init__(*args, **kwargs)   

class SolutionForm(forms.ModelForm):
    class Meta:
        model = Solution
        fields = ('author_name','solution_text',)
        widgets = {
            'author_name': forms.TextInput(attrs={"class":"form-control"}),
            'solution_text': forms.Textarea(attrs={'cols': 120, 'rows': 15,'id' : 'codetext','class':'form-control'})
        }
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('author_name','comment_text',)
        widgets = {
            'author_name': forms.TextInput(attrs={"class":"form-control"}),
            'comment_text': forms.Textarea(attrs={'cols': 100, 'rows': 15,'id' : 'codetext','class':'form-control'})
        }
    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)   
        self.fields['author_name'].required = True

class AddProblemForm(forms.ModelForm):
#    topic=forms.ModelChoiceField(queryset = Topic.objects.all(),required = True)
    class Meta:
        model = Problem
        fields = ('problem_text',
                  'author_name',
                  'topic',
                  'difficulty',
                  )
        widgets = {
            'author_name': forms.TextInput(attrs={"class":"form-control"}),
            'problem_text': forms.Textarea(attrs={'cols': 120, 'rows': 15,'id' : 'codetext','class':'form-control'}),
            }
    def __init__(self, *args, **kwargs):
        super(AddProblemForm, self).__init__(*args, **kwargs)   
        self.fields['problem_text'].label = 'Problem LaTeX'
        self.fields['author_name'].required = True
        self.fields['topic'].empty_label = None
#    def clean_types(self):
#        data = self.cleaned_data['types']
#        return [data]

class NewVersionForm(forms.ModelForm):
    class Meta:
        model = ProblemVersion
        fields = ('problem_text',
                  'author_name',
                  'difficulty',
                  )
        widgets = {
            'problem_text': forms.Textarea(attrs={'cols': 120, 'rows': 15,'id' : 'codetext','class':'form-control'}),
            }
    def __init__(self, *args, **kwargs):
        super(NewVersionForm, self).__init__(*args, **kwargs)   
        self.fields['problem_text'].label = 'Problem LaTeX'
        self.fields['author_name'].required = True


class DiffMoveProblemForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = ('difficulty',
                  'problem_status',
                  )
    def __init__(self, *args, **kwargs):
        super(DiffMoveProblemForm, self).__init__(*args, **kwargs)   


class ShortListModelForm(forms.ModelForm):
    class Meta:
        model = ShortList
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={"class":"form-control"}),
        }
