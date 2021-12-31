from typing import Tuple

from django import template
from django.core.handlers.wsgi import WSGIRequest
from django.template.base import FilterExpression, kwarg_re

from meetings.models import Meeting

register = template.Library()

from django.template.context import Context
from django.template.defaultfilters import pluralize

def parse_tag(token, parser):
    """
    Generic template tag parser.
    At rendering time, a FilterExpression f can be evaluated by calling f.resolve(context).

    @param token:
    @param parser:
    @return: a three-tuple: (tag_name, args, kwargs)
        - tag_name is a string, the name of the tag.
        - args is a list of FilterExpressions, from all the arguments that didn't look like kwargs,
          in the order they occurred, including any that were mingled amongst kwargs.
        - kwargs is a dictionary mapping kwarg names to FilterExpressions, for all the arguments that
          looked like kwargs, including any that were mingled amongst args.
    """
    # Split the tag content into words, respecting quoted strings.
    bits = token.split_contents()

    # Pull out the tag name.
    tag_name = bits.pop(0)

    # Parse the rest of the args, and build FilterExpressions from them so that
    # we can evaluate them later.
    args = []
    kwargs = {}
    for bit in bits:
        # Is this a kwarg or an arg?
        match = kwarg_re.match(bit)
        kwarg_format = match and match.group(1)
        if kwarg_format:
            key, value = match.groups()
            kwargs[key] = FilterExpression(value, parser)
        else:
            args.append(FilterExpression(bit, parser))

    return tag_name, args, kwargs


class VoteNode(template.Node):
    def __init__(self, nodelist, vote_type, votes):
        self.nodelist = nodelist
        self.vote_type = vote_type
        self.votes = votes

    def _resolve_votes(self, context: Context) -> Tuple[int, int, int, bool]:
        """
        Resolves pro, con, enthaltung and gegenrede_exists against a given context.
        @param context: the context
        @return: (pro, con, enthaltung, gegenrede_exists)
            - pro: amount of votes in favor
            - con: amount of votes in not favor
            - enthaltung: amount of abstaintions
            - gegenrede_exists: flag, if someone did force a vote, or is it automatically accepted
        """
        pro, con, enthaltung, gegenrede_exists = self.votes
        pro = int(pro.resolve(context))
        con = int(con.resolve(context))
        enthaltung = int(enthaltung.resolve(context))
        gegenrede_exists = bool(gegenrede_exists.resolve(context))
        return pro, con, enthaltung, gegenrede_exists

    def render(self, context: Context) -> str:
        pro, con, enthaltung, gegenrede = self._resolve_votes(context)
        votes_text = self.__generate_votes_text(con, enthaltung, pro)
        if not gegenrede:
            voting_result = f"Der {self.vote_type} wurde ohne Gegenrede angenommen."
        elif pro == con:
            voting_result = f"Die Abstimmung war mit {votes_text} ergebnislos."
        else:
            result = "angenommen" if pro > con else "abgelehnt"
            voting_result = f"Der {self.vote_type} wurde mit {votes_text} {result}."
        nodelist = self.nodelist.render(context)
        return f": {self.vote_type}: {nodelist}\n\n**{voting_result}**"

    @staticmethod
    def __generate_votes_text(con: int, enthaltung: int, pro: int) -> str:
        # collect votes
        votes = []
        if pro:
            votes.append(f"{pro} Stimme{pluralize(pro,'n')} dafür")
        if con:
            votes.append(f"{con} Stimme{pluralize(con,'n')} dagegen")
        if enthaltung:
            votes.append(f"{enthaltung} Enthaltung{pluralize(enthaltung,'en')}")
        # format return-value
        if not votes:
            return "0 abgegebene Stimmen"
        if len(votes) == 1:
            return votes[0]
        return ", ".join(votes[:-1]) + " und " + votes[-1]


@register.tag(name="antrag")
@register.tag(name="motion")
def do_vote(parser, token, vote_type="Antrag"):
    tag_name, args, kwargs = parse_tag(token, parser)

    usage_text = (
        f"Usage: [[ {tag_name} pro=P con=P enthaltung=P gegenrede=True|False ]] Antragstext [[ end{tag_name} ]]"
    )
    if args:
        raise template.TemplateSyntaxError(
            f"No positional arguments allowed. {usage_text}",
        )
    if not kwargs:
        raise template.TemplateSyntaxError(f"No arguments given. {usage_text}")
    if not all(k in ("pro", "con", "enthaltung", "gegenrede") for k in kwargs):
        raise template.TemplateSyntaxError(f"Illegal keyword arguments. {usage_text}")

    pro = kwargs.get("pro", FilterExpression("0", parser))
    con = kwargs.get("con", FilterExpression("0", parser))
    enthaltung = kwargs.get("enthaltung", FilterExpression("0", parser))
    gegenrede = kwargs.get("gegenrede", FilterExpression("True", parser))

    nodelist = parser.parse((f"end{tag_name}",))

    parser.delete_first_token()

    return VoteNode(
        nodelist,
        vote_type,
        votes=(pro, con, enthaltung, gegenrede),
    )


@register.tag(name="goantrag")
@register.tag(name="point_of_order")
def do_go_vote(parser, token):
    return do_vote(parser, token, vote_type="GO-Antrag")


@register.simple_tag(takes_context=True)
def anhang(context, attachment_id):
    meeting: Meeting = context["meeting"]
    request: WSGIRequest = context["request"]
    attachments_with_id = meeting.attachments_with_id
    for counted_sort_id, attachment in attachments_with_id:
        if counted_sort_id == attachment_id:
            url = request.build_absolute_uri(attachment.attachment.url)
            return f"[{attachment.name} {url}]"
    raise template.TemplateSyntaxError("Attachment not found")
