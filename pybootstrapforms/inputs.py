import re

ATTRIBUTE_SANATIZE = re.compile(r'[^A-Za-z0-9\-_\[\]]')


def _value_to_id(name, val):
    return name + "_" + ATTRIBUTE_SANATIZE.sub('', val)


def _attr(attr):
    return attr.replace(r'"', '&quot;')


class Markup(object):

    def __init__(self, markup):
        self.markup = markup

    def render_group(self):
        return self.markup


class Field(object):

    def __init__(self, name, label=None, help=None, value=None, attrs=None, required=False, classes=None):
        self.classes = classes or []
        self.required = required
        self.errors = []
        self.name = name
        self.field_type = "text"
        self.label = label
        self.attrs = attrs
        self.help = help
        self.value = value or ""

    def value_sanatized(self):
        if not self.value:
            return ''
        else:
            return self.value.replace(r'"', '&quot;')

    def attrs_string(self):
        if self.attrs is None:
            return ""
        else:
            return " ".join(('%s="%s"' % (k, _attr(v)) for k, v in self.attrs.items()))

    def render_label(self):
        if not self.label:
            return ""
        else:
            return '<label class="control-label" for="%s">%s</label>' % (
                self.name, self.label)

    def render_errors(self):
        if len(self.errors) == 1:
            return ""
        else:
            template = '<span class="help-inline">%s</span>'
            return "\n".join(template % (error,) for error in self.errors)

    def render_classes(self):
        if self.required:
            self.classes.append("required")
        if not self.classes or len(self.classes) == 0:
            return ''
        else:
            return "class='%s'" % (" ".join(self.classes),)

    def render_field(self):
        return '<input type="%s" id="%s" name="%s" value="%s" %s %s>' % (
            self.field_type, self.name, self.name, self.value_sanatized(),
            self.attrs_string(), self.render_classes())

    def render_description(self):
        if not self.help:
            return ""
        else:
            return '<span class="help-block">%s</span>' % (self.help,)

    def render_group(self):
        is_in_error = len(self.errors) > 1
        params = ("error" if is_in_error else "", self.render_label(),
                  self.render_field(), self.render_errors(),
                  self.render_description())
        return """
            <div class="control-group %s">
                %s
                <div class="controls">
                    %s
                    %s
                </div>
                %s
            </div>""" % params

    def validate(self):
        """Returns a boolean description of whether the current value of the
        field should be treated as valid.  Should return True if the
        value if valid, and otherwise False.  If False, this method
        should populate the self.errors list with descriptions of the problems

        Return:
            True if the value if valid, and otherwise False

        """
        if self.attrs and "maxlength" in self.attrs and len(self.value) > self.attrs['maxlength']:
            error = "%s cannot be longer than %d characters" % (
                self.name, self.attrs['maxlength'])
            self.errors.append(error)
        if self.required and (self.value is None or len(self.value) == 0):
            error = "%s is a required field"
            self.errors.append(error)
        return len(self.errors) == 0


class Checkbox(Field):

    def __init__(self, name, allowed_value, **kwargs):
        self.allowed_value = allowed_value
        super(Checkbox, self).__init__(name, **kwargs)

    def validate(self):
        if self.value and self.value != self.allowed_value:
            error = "%s is not a valid value for %s" % (
                self.value, self.name)
            self.errors.append(error)
        return super(Checkbox, self).validate()

    def render_label(self):
        return ''

    def render_field(self):
        template = """
            <label class="checkbox">
                <input type="checkbox" name="%s" id="%s" value="%s" %s %s %s>
                %s
            </label>"""
        params = (self.name, self.name, self.allowed_value,
                  'checked="checked"' if self.value == self.allowed_value else "",
                  self.attrs_string(), self.render_classes(), self.label)
        return template % params


class TextArea(Field):

    def __init__(self, name, rows=3, **kwargs):
        self.rows = rows
        super(TextArea, self).__init__(name, **kwargs)

    def validate(self):
        return True

    def value_sanatized(self):
        if not self.value:
            return ''
        else:
            return self.value.replace(r'<', '&lt;').replace(r'>', '&gt;')

    def render_field(self):
        return '<textarea id="%s" name="%s" rows="%d" %s %s>%s</textarea>' % (
            self.name, self.name, self.rows, self.attrs_string(),
            self.render_classes(), self.value_sanatized())


class Multiple(Field):

    def __init__(self, name, value_pairs, **kwargs):
        self.value_pairs = value_pairs
        super(Multiple, self).__init__(name, **kwargs)


class Exclusive(Multiple):

    def allowed_values(self):
        return (value for (value, display) in self.value_pairs)

    def validate(self):
        """For fields that take a set number of values, and accept only one
        of them, for validation just check to make sure that that the current
        value is one of the allowed values."""
        if self.value and self.value not in self.allowed_values():
            error = "%s is not a valid value for '%s'" % (
                self.value_sanatized(), self.label or self.name)
            self.errors.append(error)
        return super(Exclusive, self).validate()


class Dropdown(Exclusive):

    def render_field(self):
        options = ('<option value="%s" %s>%s</option>' % (_attr(val), 'selected="selected"' if val == self.value else "", label) for (val, label) in self.value_pairs)
        params = (self.name, self.name, self.attrs_string(),
                  self.render_classes(), "\t\n".join(options))
        return """
            <select name="%s" id="%s" %s %s>
                %s
            </select>
        """ % params


class Radios(Exclusive):

    def render_label(self):
        if not self.label:
            return ""
        else:
            return '<label class="control-label">%s</label>' % (
                self.label)

    def render_field(self):
        template = """
            <label class="radio">
                <input type="radio" name="%s" id="%s" value="%s" %s>
                %s
            </label>
        """
        radios = (template % (self.name, _value_to_id(self.name, val), val, 'checked="checked"' if val == self.value else "", label) for (val, label) in self.value_pairs)
        return "\n".join(radios)
