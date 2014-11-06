import form
from inputs import Field, Checkbox, TextArea, Dropdown, Radios

fields = (
    Field("a_text_input", label="Sample Text Input",
          help="This is an example of a text input", value="Initial value"),
    Checkbox("a_checkbox", label="Example Checkbox",
             help="Check this if you like", allowed_value="1"),
    TextArea("a_textarea", label="Here is a sample text area",
             help="Any text can go here", value="Intial text area text"),
    Dropdown("a_select", [('', ' - Select One - '), ('1', 'First Option'),
             ('2', 'Second Option')], label="A Select Input", required=True,
             value="2"),
    Radios("some_radios", [('blue', 'Blue Color'), ('red', 'Red Color')],
           value="red")
)

test_form = form.Form("Sample Form", *fields)
print test_form.render()

