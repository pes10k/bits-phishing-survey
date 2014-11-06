"""Classes for handling collections of form elements.  Each of these
elements will have multiple fields in it, and will be responsible for creating,
validating, etc each field in HTML"""


from .inputs import Field, Radios


class Collection(Field):

    def __init__(self, name, *args, **kwargs):
        self.sub_fields = []
        super(Collection, self).__init__(name, *args, **kwargs)

    def validate(self):
        self.errors = []
        for field in self.sub_fields:
            field.validate()
            self.errors += field.errors
        return len(self.errors) == 0


class RaitingsGrid(Collection):
    """Displays a grid of questions, each of which the user is asked
    to rank a value between 1 and x (default 7)"""


    def __init__(self, name, questions, scale_max=7, *args, **kwargs):
        super(RaitingsGrid, self).__init__(name, *args, **kwargs)
        self.scale = range(1, scale_max + 1)
        options = [(str(i), i) for i in self.scale]
        self.sub_fields = [Radios("{0}_{1}".format(name, i + 1), options, label=q) for i, q in enumerate(questions)]


    def render_label(self):
        if not self.label:
            return ""
        else:
            return '<label class="control-label">%s</label>' % (self.label,)

    def render_field(self):

        header_cols = "\n".join(["<th>{0}</th>".format(i) for i in self.scale])

        row_template = '<tr><td><label for="{name}">{label}</label></td>{radio_cells}</tr>'
        cell_template = '<td><input type="radio" name="{name}" value="{value}"></td>'

        def _body_cells(field):
            return "\n".join([cell_template.format(name=field.name, value=v) for k, v in field.value_pairs])

        body_rows = "\n".join([row_template.format(name=f.name, label=f.label, radio_cells=_body_cells(f)) for f in self.sub_fields])

        return """
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th></th>
                        {header_cells}
                    </tr>
                </thead>
                <tbody>
                    {body_rows}
                </tbody>
            </table>""".format(header_cells=header_cols, body_rows=body_rows, label=self.label)
