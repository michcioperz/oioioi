from django.contrib import admin
import nested_admin

from oioioi.quizzes.admin import QuizQuestionInline
from oioioi.pooledquizzes.models import QuizPool, QuizPoolQuestion
import oioioi.contests.admin


class QuizPoolQuestionInline(nested_admin.NestedStackedInline):
    model = QuizPoolQuestion
    extra = 0


class QuizPoolAdmin(nested_admin.NestedModelAdmin):
    model = QuizPool

oioioi.contests.admin.contest_site.register(QuizPool, QuizPoolAdmin)

QuizQuestionInline.inlines += [QuizPoolQuestionInline]
