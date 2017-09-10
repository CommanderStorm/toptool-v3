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

        if pro == con:
            result = ""
            if pro > 0:
                if enthaltung > 0:
                    text = "Die Abstimmung war mit {pro} Stimmen dafür, \
                            {con} Stimmen dagegen und {enthaltung} \
                            Enthaltungen ergebnislos." 
                else:
                    text = "Die Abstimmung war mit {pro} Stimmen dafür und \
                            {con} Stimmen dagegen ergebnislos." 
            else:
                if enthaltung > 0:
                    text = "Die Abstimmung war mit {enthaltung} Enthaltungen \
                            ergebnislos."
                else:
                    text = "Die Abstimmung war mit 0 abgebenen Stimmen \
                            ergebnislos."
        else:
            if pro > con:
                result = "angenommen"
            else:
                result = "abgelehnt"
            if pro > 0:
                if con > 0:
                    if enthaltung > 0:
                        text = "Der {antrag} wurde mit {pro} Stimmen dafür, \
                                {con} Stimmen dagegen und {enthaltung} \
                                Enthaltungen {result}." 
                    else:
                        text = "Der {antrag} wurde mit {pro} Stimmen dafür und \
                                {con} Stimmen dagegen {result}." 
                else:
                    if enthaltung > 0:
                        text = "Der {antrag} wurde mit {pro} Stimmen dafür und \
                                {enthaltung} Enthaltungen {result}." 
                    else:
                        text = "Der {antrag} wurde mit {pro} Stimmen dafür \
                                einstimmig {result}." 
            else:
                if enthaltung > 0:
                    text = "Der {antrag} wurde mit {con} Stimmen dagegen und \
                            {enthaltung} Enthaltungen {result}." 
                else:
                    text = "Der {antrag} wurde mit {con} Stimmen dagegen \
                            einstimmig {result}." 
        text = ": {antrag}: " + nodelist + "\n\n**" + text + "**"
        text = text.format(result=result, pro=pro, con=con,
                enthaltung=enthaltung, antrag=self.antrag)
        return text


def do_vote(parser, token, antrag="Antrag"):
    tag_name, args, kwargs = parse_tag(token, parser)

    usage = '{{% {tag_name} pro=P con=P enthaltung=P %}} Antragstext {{% end{tag_name} %}}'.format(tag_name=tag_name)
    if len(args) > 0 or not kwargs or not all(map(lambda k: k in ("pro", "con",
            "enthaltung"), kwargs.keys())):
        raise template.TemplateSyntaxError("Usage: %s" % usage)
    
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
register.tag('goantrag', do_go_vote)
