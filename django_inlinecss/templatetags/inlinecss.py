from django import template

from django.utils.encoding import smart_unicode
from django.contrib.staticfiles.finders import find

from django_inlinecss import conf

register = template.Library()


class InlineCssNode(template.Node):
    def __init__(self, nodelist, filter_expressions):
        self.nodelist = nodelist
        self.filter_expressions = filter_expressions

    def render(self, context):
        rendered_contents = self.nodelist.render(context)
        css = ''
        for expression in self.filter_expressions:
            path = expression.resolve(context, True)
            if path is not None:
                path = smart_unicode(path)
            expanded_path = find(path)

            with open(expanded_path) as css_file:
                css = ''.join((css, css_file.read()))

        engine = conf.get_engine()(html=rendered_contents, css=css)
        return engine.render()


@register.tag
def inlinecss(parser, token):
    nodelist = parser.parse(('endinlinecss',))

    # prevent second parsing of endinlinecss
    parser.delete_first_token()

    args = token.split_contents()[1:]

    return InlineCssNode(
        nodelist,
        [parser.compile_filter(arg) for arg in args])
