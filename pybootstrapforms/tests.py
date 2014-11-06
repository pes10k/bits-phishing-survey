import unittest
import form
from inputs import Field, Checkbox, TextArea, Dropdown, Radios


class FormValuesTestCase(unittest.TestCase):

    def test_populate(self):
        """Test to make sure that when we mix new values into a pre-populated
        form, we get the expected mix of values back"""

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

        new_textarea_value = "New textarea value"

        correct_values = dict(
            # Values that were given to the fields when the form was created
            a_text_input="Initial value",
            some_radios="red",
            a_checkbox="",
            a_textarea=new_textarea_value,
            a_select="1",
        )

        new_values = dict(
            a_checkbox="",
            a_textarea=new_textarea_value,
            a_select="1",
        )

        test_form.populate(new_values)
        self.assertEqual(correct_values, test_form.values())

    def test_invalid_dropdown(self):
        """Check to make sure that if we give a dropdown a value that isn't
        one of its accepted values, it does not validate."""
        fields = (
            Dropdown("a_select", [('', ' - Select One - '), ('1', 'First Option'),
                     ('2', 'Second Option')], label="A Select Input", required=True,
                     value="2"),
        )

        test_form = form.Form("Sample Form", *fields)

        test_values = dict(
            a_select="3",
        )

        test_form.populate(test_values)
        self.assertEqual(False, test_form.validate())
