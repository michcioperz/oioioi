import random
from oioioi.quizzes.controllers import QuizProblemController


class PooledQuizProblemController(QuizProblemController):
    def submission_deterministic_rng(self, user, problem_instance, submission):
        user_submissions = problem_instance.submission_set.filter(user=user)
        if submission is not None:
            # filter for only submissions earlier than reference submission
            user_submissions = user_submissions.filter(pk__lt=submission.pk)
        return random.Random((user.username, user_submissions.count(), problem_instance.pk))

    def select_questions(self, user, problem_instance, submission):
        pools = problem_instance.problem.quiz.quizpool_set.order_by('pk').all()
        rng = self.submission_deterministic_rng(user, problem_instance, submission)

        questions = []
        for pool in pools:
            questions += rng.sample(pool.quizpoolquestion_set.order_by('pk').select_related('question'), pool.count)

        return [q.question for q in questions]
