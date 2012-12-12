from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from oioioi.base.menu import menu_registry
from oioioi.base.permissions import enforce_condition
from oioioi.contests.utils import can_enter_contest, is_contest_admin, \
        visible_problem_instances
from oioioi.questions.forms import AddContestMessageForm, AddReplyForm
from oioioi.questions.models import Message, MessageView

menu_registry.register('contest_messages', _("Messages"),
        lambda request: reverse('contest_messages', kwargs={'contest_id':
            request.contest.id}), order=450)

def visible_messages(request):
    problem_instances = visible_problem_instances(request)
    problem_ids = [pi.problem_id for pi in problem_instances]
    messages = Message.objects \
            .filter(Q(contest=request.contest.id)
                    | Q(problem_id__in=problem_ids)) \
            .order_by('-date')
    if not request.user.has_perm('contests.contest_admin', request.contest):
        q_expression = Q(kind='PUBLIC')
        if request.user.is_authenticated():
            q_expression = q_expression \
                    | (Q(author=request.user) & Q(kind='QUESTION')) \
                    | Q(top_reference__author=request.user)
        messages = messages.filter(q_expression)
    return messages

def new_messages(request, messages=None):
    if not request.user.is_authenticated():
        return messages.none()
    if messages is None:
        messages = visible_messages(request)
    return  messages.exclude(messageview__user=request.user) \
            .exclude(author=request.user)

def messages_template_context(request, messages):
    is_admin = request.user.has_perm('contests.contest_admin', request.contest)
    replied_ids = frozenset(m.top_reference_id for m in messages)
    new_ids = new_messages(request, messages).values_list('id', flat=True)
    to_display = [{
            'message': m,
            'link_message': m.top_reference in messages \
                    and m.top_reference or m,
            'needs_reply': is_admin and m.kind == 'QUESTION',
            'read': m.id not in new_ids,
        } for m in messages if m.id not in replied_ids]
    def key(entry):
        return entry['needs_reply'], entry['message'].date
    to_display.sort(key=key, reverse=True)
    return to_display

@enforce_condition(can_enter_contest)
def messages_view(request, contest_id):
    messages = messages_template_context(request, visible_messages(request))
    return TemplateResponse(request, 'questions/list.html',
                {'records': messages})

@enforce_condition(can_enter_contest)
def message_view(request, contest_id, message_id):
    message = get_object_or_404(Message, id=message_id)
    vmessages = visible_messages(request)
    if not vmessages.filter(id=message_id):
        raise PermissionDenied
    if message.top_reference_id is None:
        replies = list(vmessages.filter(top_reference=message).all())
    else:
        replies = []
    if request.user.is_authenticated():
        for m in [message] + replies:
            MessageView.objects.get_or_create(message=m, user=request.user)
    return TemplateResponse(request, 'questions/message.html',
                {'message': message, 'replies': replies,
                    'reply_to_id': message.top_reference_id or message.id})

@enforce_condition(can_enter_contest)
def add_contest_message_view(request, contest_id):
    is_admin = request.user.has_perm('contests.contest_admin', request.contest)
    if request.method == 'POST':
        form = AddContestMessageForm(request, request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.author = request.user
            if is_admin:
                instance.kind = 'PUBLIC'
            else:
                instance.kind = 'QUESTION'
            instance.save()
            return redirect('contest_messages', contest_id=contest_id)

    else:
        form = AddContestMessageForm(request)

    if is_admin:
        title = _("Add announcement")
    else:
        title = _("Ask question")

    return TemplateResponse(request, 'questions/add.html',
            {'form': form, 'title': title, 'is_announcement': is_admin})

def quote_for_reply(content):
    lines = content.strip().split('\n')
    return ''.join('> ' + l for l in lines)

@enforce_condition(is_contest_admin)
def add_reply_view(request, contest_id, message_id):
    question = get_object_or_404(Message, id=message_id,
            contest_id=contest_id, kind='QUESTION')
    if request.method == 'POST':
        form = AddReplyForm(request, request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.top_reference = question
            instance.author = request.user
            instance.save()
            return redirect('contest_messages', contest_id=contest_id)
    else:
        form = AddReplyForm(request, initial={
                'topic': _("Re: ") + question.topic,
                'content': quote_for_reply(question.content),
            })

    return TemplateResponse(request, 'questions/add.html',
            {'form': form, 'title': _("Reply"), 'is_reply': True})