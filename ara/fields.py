import datetime
from flask import render_template_string
from jinja2 import Undefined

from ara import app

implicit_templates = {
    datetime.datetime: '{{ value|datefmt }}',
    datetime.timedelta: '{{ value|timefmt }}',
}


class Field(object):
    '''A utility class for extracting a value from an object hierarchy and
    formatting it using a Jinja2 template.'''

    def __init__(self, name, path=None, template=None,
                 raise_on_err=False):
        '''Initialize a Field object.

        - `name` -- field label (used for display)
        - `path` -- a Jinja2 expression used to extract a value from
           an object hierarchy.  If not specified, this is derived from
           `name` by setting `name` to lower case and replacing ` ` with
           `_`.
        - `template` -- a Jinja2 template that will be used to render
          the value for display.
        - `raise_on_err` -- raise an AttributeError if the specified
          `path` does not return a value.
        '''

        if path is None:
            path = name.lower().replace(' ', '_')

        self.name = name
        self.template = template
        self.raise_on_err = raise_on_err
        self.path = path

        self.expr = app.jinja_env.compile_expression(
            path, undefined_to_none=False)

    def __call__(self, obj):
        '''Extract a value from `obj` and return the formatted value.'''

        # Extract value from the object.
        value = self.expr(**{x: getattr(obj, x)
                             for x in dir(obj)
                             if not x.startswith('_')})

        if value is Undefined:
            if self.raise_on_err:
                raise AttributeError(self.path)

        # Get a template, maybe
        template = (self.template if self.template
                    else implicit_templates.get(type(value)))

        if template:
            return render_template_string(template, value=value)
        else:
            return value

    def __str__(self):
        return self.name
