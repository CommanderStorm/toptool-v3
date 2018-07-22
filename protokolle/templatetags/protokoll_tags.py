from django import template
from django.template.base import FilterExpression, kwarg_re
from django.utils.translation import ugettext_lazy as _


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

    return (tag_name, args, kwargs)


class VoteNode(template.Node):
    def __init__(self, nodelist, pro, con, enthaltung, antrag):
        self.nodelist = nodelist
        self.pro = pro
        self.con = con
        self.enthaltung = enthaltung
        self.antrag = antrag

    def render(self, context):
        pro = int(self.pro.resolve(context))
        con = int(self.con.resolve(context))
        enthaltung = int(self.enthaltung.resolve(context))
        nodelist = self.nodelist.render(context)

        votes = []
        if pro == 1:
            votes.append("{pro} Stimme dafür")
        elif pro > 1:
            votes.append("{pro} Stimmen dafür")
        if con == 1:
            votes.append("{con} Stimme dagegen")
        elif con > 1:
            votes.append("{con} Stimmen dagegen")
        if enthaltung == 1:
            votes.append("{enthaltung} Enthaltung")
        elif enthaltung > 1:
            votes.append("{enthaltung} Enthaltungen")

        if len(votes) == 0:
            votes_text = "0 abgebenen Stimmen"
        elif len(votes) == 1:
            votes_text = votes[0]
        else:
            votes_text = ", ".join(votes[:-1]) + " und " + votes[-1]

        votes_text = votes_text.format(
            pro=pro, con=con, enthaltung=enthaltung,
        )

        result = ""
        if pro == con:
            text = "Die Abstimmung war mit {votes_text} ergebnislos."
        else:
            text = "Der {antrag} wurde mit {votes_text} {result}."
            if pro > con:
                result = "angenommen"
            else:
                result = "abgelehnt"
        text = ": {antrag}: " + nodelist + "\n\n**" + text + "**"
        text = text.format(
            result=result, votes_text=votes_text, antrag=self.antrag,
        )
        return text


def do_vote(parser, token, antrag="Antrag"):
    tag_name, args, kwargs = parse_tag(token, parser)

    usage = '[[ {tag_name} pro=P con=P enthaltung=P ]] Antragstext [[ end{tag_name} ]]'.format(tag_name=tag_name)
    if len(args) > 0 or not kwargs or not all(map(lambda k: k in ("pro", "con",
            "enthaltung"), kwargs.keys())):
        raise template.TemplateSyntaxError(
            _("Syntax von {tag_name}: {usage}").format(
                tag_name=tag_name,
                usage=usage,
            )
        )
    
    pro = kwargs.get("pro", FilterExpression("0", parser))
    con = kwargs.get("con", FilterExpression("0", parser))
    enthaltung = kwargs.get("enthaltung", FilterExpression("0", parser))

    nodelist = parser.parse(('end{tag_name}'.format(tag_name=tag_name),))

    parser.delete_first_token()

    return VoteNode(nodelist, pro=pro, con=con, enthaltung=enthaltung,
            antrag=antrag)


def do_go_vote(parser, token):
    return do_vote(parser, token, antrag="GO-Antrag")


register.tag('antrag', do_vote)
register.tag('motion', do_vote)
register.tag('goantrag', do_go_vote)
register.tag('point_of_order', do_go_vote)


@register.simple_tag(takes_context=True)
def anhang(context, attachmentid):
    meeting = context['meeting']
    request = context['request']
    attachments = meeting.get_attachments_with_id()
    for attachment in attachments:
        if attachment.get_attachmentid == attachmentid:
            url = request.build_absolute_uri(attachment.attachment.url)
            return '[{} {}]'.format(attachment.name, url)
    raise template.TemplateSyntaxError("Attachment not found")
