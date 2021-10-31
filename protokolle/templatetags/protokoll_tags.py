from django import template
from django.template.base import FilterExpression, kwarg_re

register = template.Library()


def parse_tag(token, parser):
    """
    Generic template tag parser.

    Returns a three-tuple: (tag_name, args, kwargs)

    tag_name is a string, the name of the tag.

    args is a list of FilterExpressions, from all the arguments that didn't look like kwargs,
    in the order they occurred, including any that were mingled amongst kwargs.

    kwargs is a dictionary mapping kwarg names to FilterExpressions, for all the arguments that
    looked like kwargs, including any that were mingled amongst args.

    (At rendering time, a FilterExpression f can be evaluated by calling f.resolve(context).)
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
    def __init__(self, nodelist, votes, antrag):
        self.nodelist = nodelist
        self.votes = votes
        self.antrag = antrag

    def _resolve_votes(self, context):
        pro = int(self.votes[0].resolve(context))
        con = int(self.votes[1].resolve(context))
        enthaltung = int(self.votes[2].resolve(context))
        gegenrede = bool(self.votes[3].resolve(context))
        return pro, con, enthaltung, gegenrede

    def render(self, context):
        pro, con, enthaltung, gegenrede = self._resolve_votes(context)
        votes_text = self.__generate_votes_text(con, enthaltung, pro)
        if not gegenrede:
            voting_result = f"Der {self.antrag} wurde ohne Gegenrede angenommen."
        elif pro == con:
            voting_result = f"Die Abstimmung war mit {votes_text} ergebnislos."
        else:
            result = "angenommen" if pro > con else "abgelehnt"
            voting_result = f"Der {self.antrag} wurde mit {votes_text} {result}."
        nodelist = self.nodelist.render(context)
        return f": {self.antrag}: {nodelist}\n\n**{voting_result}**"

    @staticmethod
    def __generate_votes_text(con, enthaltung, pro):
        votes = []
        if pro == 1:
            votes.append(f"{pro} Stimme dafür")
        elif pro > 1:
            votes.append(f"{pro} Stimmen dafür")
        if con == 1:
            votes.append(f"{con} Stimme dagegen")
        elif con > 1:
            votes.append(f"{con} Stimmen dagegen")
        if enthaltung == 1:
            votes.append(f"{enthaltung} Enthaltung")
        elif enthaltung > 1:
            votes.append(f"{enthaltung} Enthaltungen")
        if not votes:
            return "0 abgebenen Stimmen"
        if len(votes) == 1:
            return votes[0]
        return ", ".join(votes[:-1]) + " und " + votes[-1]


def do_vote(parser, token, antrag="Antrag"):
    tag_name, args, kwargs = parse_tag(token, parser)

    usage = f"[[ {tag_name} pro=P con=P enthaltung=P gegenrede=True|False ]] Antragstext [[ end{tag_name} ]]"
    if args:
        raise template.TemplateSyntaxError(
            f"No positional arguments allowed. Usage: {usage}",
        )
    if not kwargs:
        raise template.TemplateSyntaxError(f"No arguments given. Usage: {usage}")
    if not all(k in ("pro", "con", "enthaltung", "gegenrede") for k in kwargs):
        raise template.TemplateSyntaxError(f"Illegal keyword arguments. Usage: {usage}")

    pro = kwargs.get("pro", FilterExpression("0", parser))
    con = kwargs.get("con", FilterExpression("0", parser))
    enthaltung = kwargs.get("enthaltung", FilterExpression("0", parser))
    gegenrede = kwargs.get("gegenrede", FilterExpression("True", parser))

    nodelist = parser.parse((f"end{tag_name}",))

    parser.delete_first_token()

    return VoteNode(
        nodelist,
        votes=(pro, con, enthaltung, gegenrede),
        antrag=antrag,
    )


def do_go_vote(parser, token):
    return do_vote(parser, token, antrag="GO-Antrag")


register.tag("antrag", do_vote)
register.tag("motion", do_vote)
register.tag("goantrag", do_go_vote)
register.tag("point_of_order", do_go_vote)


@register.simple_tag(takes_context=True)
def anhang(context, attachmentid):
    meeting = context["meeting"]
    request = context["request"]
    attachments = meeting.get_attachments_with_id()
    for attachment in attachments:
        if attachment.get_attachmentid == attachmentid:
            url = request.build_absolute_uri(attachment.attachment.url)
            return f"[{attachment.name} {url}]"
    raise template.TemplateSyntaxError("Attachment not found")
