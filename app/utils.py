from functools import wraps
from flask import abort
from flask_login import current_user


def role_required(*roles):
    """Restrict a view to one or more roles, e.g. @role_required('admin')."""

    def decorator(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role not in roles:
                abort(403)
            return fn(*args, **kwargs)

        return wrapped

    return decorator


def allowed_cv_file(filename, allowed_extensions):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions
