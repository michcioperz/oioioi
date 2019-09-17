from django.core.urlresolvers import reverse
from django.test import RequestFactory
from django.utils.timezone import utc

from oioioi.base.tests import TestCase, fake_time
from oioioi.contests.models import Contest, ProblemInstance, Submission, \
    SubmissionReport
from oioioi.contests.tests import SubmitMixin
from oioioi.problems.models import Problem
from oioioi.quizzes.models import QuestionReport, QuizSubmission, \
    QuizQuestionPicture, QuizAnswerPicture, Quiz
from oioioi.quizzes import views

from datetime import datetime
import os.path


class SubmitQuizMixin(SubmitMixin):
    def submit_quiz(self, contest, problem_instance, answers):
        """
        Submits a quiz with given answer
        :param contest: in what contest to submit
        :param problem_instance: indicates which quiz to submit
        :param answers: dictionary mapping question ids to:
                        1) answer id
                        2) list of answer ids if question is multiple choice
        :return response to the request
        """
        url = reverse('submit', kwargs={'contest_id': contest.id})

        post_data = {
            'problem_instance_id': problem_instance.id,
        }

        for qid in answers:
            post_data.update({
                'quiz_' + str(problem_instance.id) + '_q_' + str(qid):
                    answers[qid]
            })

        return self.client.post(url, post_data)


class TestTextInput(TestCase, SubmitQuizMixin):
    fixtures = ['test_users', 'test_basic_contest', 'test_problem_instance',
                'test_quiz_problem_with_text_input']

    def setUp(self):
        self.assertTrue(self.client.login(username='test_user'))

    def test_simple_submission(self):
        contest = Contest.objects.get()
        problem_instance = ProblemInstance.objects.get(pk=1)

        response = self.submit_quiz(contest, problem_instance, {
            '1': 'Answer - correct',
            '2': 'A',
        })
        self._assertSubmitted(contest, response)

        submission = QuizSubmission.objects.get()
        controller = submission.problem_instance.controller

        controller.judge(submission)
        submission_report = SubmissionReport.objects.get(submission=submission, status="ACTIVE")
        self.assertEqual(submission_report.score_report.score, 50)

    def test_second_possible_answer(self):
        contest = Contest.objects.get()
        problem_instance = ProblemInstance.objects.get(pk=1)

        response = self.submit_quiz(contest, problem_instance, {
            '1': 'Answer - correct',
            '2': 'B',
        })
        self._assertSubmitted(contest, response)

        submission = QuizSubmission.objects.get()
        controller = submission.problem_instance.controller

        controller.judge(submission)
        submission_report = SubmissionReport.objects.get(submission=submission, status="ACTIVE")
        self.assertEqual(submission_report.score_report.score, 50)

    def test_wrong_answer(self):
        contest = Contest.objects.get()
        problem_instance = ProblemInstance.objects.get(pk=1)

        response = self.submit_quiz(contest, problem_instance, {
            '1': 'something completely incorrect',
            '2': 'C',
        })
        self._assertSubmitted(contest, response)

        submission = QuizSubmission.objects.get()
        controller = submission.problem_instance.controller

        controller.judge(submission)
        submission_report = SubmissionReport.objects.get(submission=submission, status="ACTIVE")
        self.assertEqual(submission_report.score_report.score, 0)


class TestSubmission(TestCase, SubmitQuizMixin):
    fixtures = ['test_users', 'test_basic_contest', 'test_quiz_problem',
                'test_quiz_problem_second', 'test_problem_instance']

    def setUp(self):
        self.assertTrue(self.client.login(username='test_user'))

    def test_simple_submission(self):
        contest = Contest.objects.get()
        problem_instance = ProblemInstance.objects.get(pk=1)

        response = self.submit_quiz(contest, problem_instance, {
            '1': '1',
            '2': ('3', '4')
        })
        self._assertSubmitted(contest, response)

    def test_empty_multiple_choice(self):
        contest = Contest.objects.get()
        problem_instance = ProblemInstance.objects.get(pk=1)

        response = self.submit_quiz(contest, problem_instance, {
            '1': '1',
            '2': ()
        })
        self._assertSubmitted(contest, response)

    def test_wrong_id(self):
        contest = Contest.objects.get()
        problem_instance = ProblemInstance.objects.get(pk=1)

        response = self.submit_quiz(contest, problem_instance, {
            '1': '3',  # answer 3 belongs to question 2
            '2': ()
        })
        self.assertContains(response, "Select a valid choice")

        response = self.submit_quiz(contest, problem_instance, {
            '1': '1337',  # such an answer doesn't exist
            '2': ()
        })
        self.assertContains(response, "Select a valid choice")

    def test_submission_unanswered_question(self):
        contest = Contest.objects.get()
        problem_instance = ProblemInstance.objects.get(pk=1)

        response = self.submit_quiz(contest, problem_instance, {
            '1': '',  # single-choice questions must have some answer
            '2': ()
        })
        self.assertContains(response, "Answer is required")


class TestScore(TestCase):
    fixtures = ['test_users', 'test_contest', 'test_quiz_problem',
                'test_quiz_problem_second', 'test_problem_instance',
                'test_quiz_submission']

    def test_multiple_choice_no_correct_answer_score(self):
        submission = QuizSubmission.objects.get()
        controller = submission.problem_instance.controller

        controller.judge(submission)
        submission_report = SubmissionReport.objects.get(submission=submission, status="ACTIVE")
        question_report = QuestionReport.objects.get(question=3,
                                                     submission_report=submission_report)

        self.assertEqual(question_report.score, 27)

    def test_all_answers_correct_score(self):
        submission = QuizSubmission.objects.get()
        controller = submission.problem_instance.controller

        controller.judge(submission)
        submission_report = SubmissionReport.objects.get(submission=submission, status="ACTIVE")
        question_report = QuestionReport.objects.get(question=1,
                                                     submission_report=submission_report)

        self.assertEqual(question_report.score, 27)

    def test_one_answer_incorrect_score(self):
        submission = QuizSubmission.objects.get()
        controller = submission.problem_instance.controller

        controller.judge(submission)
        submission_report = SubmissionReport.objects.get(submission=submission, status="ACTIVE")
        question_report = QuestionReport.objects.get(question=2,
                                                     submission_report=submission_report)

        self.assertEqual(question_report.score, 0)


class TestSubmissionView(TestCase):
    fixtures = ['test_users', 'test_contest',
                'test_quiz_problem', 'test_problem_instance',
                'test_quiz_submission']

    def setUp(self):
        self.assertTrue(self.client.login(username='test_user'))

    def test_question_report(self):
        contest = Contest.objects.get()
        submission = QuizSubmission.objects.get(pk=1)
        kwargs = {'contest_id': contest.id, 'submission_id': submission.id}
        response = self.client.get(reverse('submission', kwargs=kwargs))

        self.assertContains(response, '27 / 27', count=1)
        self.assertContains(response, '0 / 27', count=1)

    def test_submission_score_visible(self):
        submission = Submission.objects.get(pk=1)
        kwargs = {'contest_id': submission.problem_instance.contest.id,
                  'submission_id': submission.id}
        expected_score = 50
        response = self.client.get(reverse('submission', kwargs=kwargs))
        self.assertContains(response,
                            '<td>{}</td>'
                            .format(expected_score),
                            html=True)


class TestEditQuizQuestions(TestCase):
    fixtures = ['test_users', 'test_contest', 'test_quiz_problem']

    def setUp(self):
        self.assertTrue(self.client.login(username='test_user'))  # this user is not an admin

    def test_edit_quiz_questions(self):
        # test_user is an author of this problem
        problem = Problem.objects.get(pk=1)
        url = reverse('oioioiadmin:quizzes_quiz_change', args=[problem.pk])
        response = self.client.get(url, follow=True)
        self.assertContains(response, 'Add another Quiz Question')


class TestQuizBleach(TestCase):
    fixtures = ['test_users', 'test_basic_contest',
                'test_quiz_bleach', 'test_problem_instance']

    def setUp(self):
        self.assertTrue(self.client.login(username='test_user'))

    def test_quizbleach(self):
        response = self.client.get(reverse('submit', kwargs={'contest_id': Contest.objects.get().id}))
        self.assertContains(response, '<pre>Answer - correct</pre>')
        self.assertNotContains(response, '<script src="http://weaselcrow.com/keylogger.js"></script>')


class TestPictures(TestCase):
    fixtures = ['test_users', 'test_basic_contest',
                'test_quiz_problem_pictures', 'test_problem_instance']

    def setUp(self):
        self.assertTrue(self.client.login(username='test_user'))

    def test_embedding(self):
        response = self.client.get(reverse('submit', kwargs={'contest_id': Contest.objects.get().id}))
        def test(picture):
            self.assertContains(response, picture.get_absolute_url())
        test(QuizQuestionPicture.objects.get())
        test(QuizAnswerPicture.objects.get())

    def test_invalid_mode(self):
        response = views.picture_view(RequestFactory().request(), 'z', 1)
        self.assertEqual(response.status_code, 404)

    def test_access(self):
        url = QuizQuestionPicture.objects.get().get_absolute_url()
        with fake_time(datetime(1999, 1, 1, tzinfo=utc)):
            response = self.client.get(url, follow=True)
            self.assertEqual(response.status_code, 403)

    def test_download(self):
        cat_path = os.path.join(os.path.dirname(__file__), 'files', 'cat.jpg')
        picture = QuizQuestionPicture.objects.get()
        picture.file.save('cat', open(cat_path, 'rb'))
        picture.save()
        response = self.client.get(picture.get_absolute_url(), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.streaming)
        self.assertEqual(b''.join(response.streaming_content), open(cat_path, 'rb').read())
