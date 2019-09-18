from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.db.models import Q

from oioioi.contests.controllers import ContestController, \
        RegistrationController, PastRoundsHiddenContestControllerMixin


class PrivateRegistrationController(RegistrationController):
    @classmethod
    def anonymous_can_enter_contest(cls):
        return False

    def user_contests_query(self, request):
        return Q(pk__isnull=True)  # (False)

    def filter_participants(self, queryset):
        return queryset.none()


class PrivateContestController(ContestController):
    def registration_controller(self):
        return PrivateRegistrationController(self.contest)

    def update_submission_score(self, submission):
        raise NotImplementedError

    def render_submission(self, request, submission):
        raise NotImplementedError

    def create_submission(self, request, problem_instance, form_data,
                          **kwargs):
        raise NotImplementedError


class PastRoundsHiddenContestController(ContestController):
    pass
PastRoundsHiddenContestController.mix_in(
    PastRoundsHiddenContestControllerMixin
)


class SubmitMixin(object):
    def _assertSubmitted(self, contest, response):
        self.assertEqual(302, response.status_code)
        submissions = reverse('my_submissions',
                              kwargs={'contest_id': contest.id})
        self.assertTrue(response["Location"].endswith(submissions))

    def _assertNotSubmitted(self, contest, response):
        self.assertEqual(302, response.status_code)
        submissions = reverse('my_submissions',
                              kwargs={'contest_id': contest.id})
        self.assertFalse(response["Location"].endswith(submissions))


def make_empty_contest_formset():
    formsets = (
        ('round_set', 0, 0, 0, 1000),
        ('c_attachments', 0, 0, 0, 1000),
        ('contestlink_set', 0, 0, 0, 1000),
        ('messagenotifierconfig_set', 0, 0, 0, 1000),
        ('mail_submission_config', 1, 0, 0, 1),
        ('problemstatementconfig', 1, 0, 0, 1),
        ('statistics_config', 1, 0, 0, 1),
        ('exclusivenessconfig_set', 0, 0, 0, 1000),
        ('contesticon_set', 0, 0, 0, 1000),
        ('contestlogo', 1, 0, 0, 1),
        ('programs_config', 1, 0, 0, 1),
        ('contestcompiler_set', 0, 0, 0, 1000),
    )
    data = dict()
    for (name, total, initial, min_num, max_num) in formsets:
        data['{}-TOTAL_FORMS'.format(name)] = total
        data['{}-INITIAL_FORMS'.format(name)] = initial
        data['{}-MIN_NUM_FORMS'.format(name)] = min_num
        data['{}-MAX_NUM_FORMS'.format(name)] = max_num
    return data
