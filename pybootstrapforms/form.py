class Form(object):

    def __init__(self, name, *args):
        self.name = name

        # Create two mappings of the given fields, one as a list (to maintain
        # order) and the second as a dict (to make querying by field name
        # quick)
        self.fields_ordered = args
        fields_named = dict()
        for field in args:
            if hasattr(field, 'sub_fields'):
                for sub_field in field.sub_fields:
                    fields_named[sub_field.name] = sub_field
            elif hasattr(field, 'name'):
                fields_named[field.name] = field
        self.fields_named = fields_named

    def render(self):
        groups = (field.render_group() for field in self.fields_ordered)
        legend = "<legend>" + self.name + "</legend>" if self.name else ""
        return """
            <fieldset>
                %s
                %s
            </fieldset>
        """ % (legend, "\t\n".join(groups))

    def populate(self, values):
        """Populates the values in the form with a set of values.  If a value
        is passed in as a value that doesn't correspond to an underlying
        field, it is silently ignored.

        Args:
            values -- a dict of field name -> values mappings
        """
        for name, value in values.items():
            if name in self.fields_named:
                self.fields_named[name].value = value

    def values(self):
        """Returns a mapping of all values in the form and their coresponding
        value.  Note that these values should not be trusted / used
        utill they're checked with self.validate() first.

        Return:
            A dict mapping of all values in the form from the name of a
            field to its corresponding value
        """
        return {field.name: field.value for name, field in self.fields_named.items()}

    def empty(self):
        """Removes all values from the form, so that the structure is as given,
        but all the fields have no value.  Note that this may result in an
        invalid form state for valid fields"""
        for field in self.fields_ordered:
            field.value = None

    def validate(self):
        """Attempts to valdiate the given value of each field.

        Return:
            True if all fields passed validation, and otherwise False
        """
        is_valid = True
        for field in self.fields:
            is_valid = is_valid and field.validate()
        return is_valid

    def errors(self):
        """Returns a dictionary of field names and the errors with their
        field.  An empty dictionary represents either a form that hasn't
        been validated yet, or a correct / valid form.

        Return:
            A dictionary of {field name: [error strings]}
        """
        errors = {}
        for field in self.fields:
            if len(field.errors):
                errors[field.name] = field.errors
        return errors

    @property
    def fields(self):
        return (field for field in self.fields_ordered if hasattr(field, 'value'))
