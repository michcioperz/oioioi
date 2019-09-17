from django.db import models
from django.utils.translation import ugettext_lazy as _

from oioioi.quizzes.models import Quiz, QuizQuestion


class QuizPool(models.Model):
    quiz = models.ForeignKey(Quiz)
    count = models.IntegerField()
    description = models.TextField(null=True, blank=True, help_text=_("Will not be shown to contestants."))

    def __unicode__(self):
        return self.description


class QuizPoolQuestion(models.Model):
    pool = models.ForeignKey(QuizPool)
    question = models.OneToOneField(QuizQuestion)
