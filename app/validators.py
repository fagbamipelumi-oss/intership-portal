import re

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_registration_fields(form, required_fields):
    """
    Checks that every field in required_fields is present and non-empty,
    and that 'email' (if present) looks like a real email address.
    Returns a list of error messages — empty list means validation passed.
    """
    errors = []
    for field in required_fields:
        value = form.get(field, "").strip()
        if not value:
            errors.append(f"{field.replace('_', ' ').title()} is required.")

    email = form.get("email", "").strip()
    if email and not EMAIL_PATTERN.match(email):
        errors.append("Please enter a valid email address.")

    password = form.get("password", "")
    if password and len(password) < 8:
        errors.append("Password must be at least 8 characters.")

    return errors
