from django.utils.translation import ugettext_lazy as _
from oioioi.quizzes.problem_sources import EmptyQuizSource


class EmptyPooledQuizSource(EmptyQuizSource):
    key = 'emptypooledquiz_source'
    problem_controller_class = 'oioioi.pooledquizzes.controllers.PooledQuizProblemController'
    short_description = _("Add a pooled quiz")
