"""Template helpers for the auth pages (login, 2FA, registration, password
reset). They only add accessibility and autofill attributes while rendering a
form field. Validation and form logic stay unchanged."""

from django import template
from django.conf import settings
from django.forms import BoundField

register = template.Library()

# autocomplete values for fields whose widget does not set one already
AUTOCOMPLETE_BY_FIELD_NAME = {
    "name": "name",
    "email": "email",
    "code": "one-time-code",
}

ERROR_BLOCK_ID = "form-errors"


@register.filter
def lo_widget(field: BoundField, mark_invalid=False):
    """Render the widget of a bound field with accessibility attributes.

    - invalid fields get aria-invalid="true" and aria-describedby pointing to
      the error block above the form (and to their help text, if any)
    - mark_invalid marks the field invalid when the form has non-field errors,
      e.g. wrong email or password on the sign in page
    - autocomplete is set for name, email and one-time-code fields when the
      widget does not define it already
    """
    attrs: dict[str, str | bool] = {}
    widget_attrs = field.field.widget.attrs

    described_by: list[str] = []
    form_has_errors = bool(field.form.non_field_errors())
    if field.errors or (mark_invalid and form_has_errors):
        attrs["aria-invalid"] = "true"
        described_by.append(ERROR_BLOCK_ID)
    if field.help_text:
        described_by.append("{}_help".format(field.auto_id))
    if described_by:
        attrs["aria-describedby"] = " ".join(described_by)

    autocomplete = AUTOCOMPLETE_BY_FIELD_NAME.get(field.name)
    if autocomplete and "autocomplete" not in widget_attrs:
        attrs["autocomplete"] = autocomplete
    if field.name == "code":
        attrs["inputmode"] = "numeric"

    return field.as_widget(attrs=attrs)


@register.simple_tag
def lo_error_block_id() -> str:
    return ERROR_BLOCK_ID


@register.simple_tag
def frontend_url() -> str:
    """The public Law&Orga frontend (landing page)."""
    return settings.MAIN_FRONTEND_URL
