from django.contrib import admin

from .models import Problem,UserProfile,ProblemVersion,Comment,Solution
# Register your models here.

admin.site.register(ProblemVersion)
admin.site.register(Solution)
admin.site.register(Comment)
admin.site.register(Problem)
admin.site.register(UserProfile)
