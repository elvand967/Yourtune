
# ../config/settings/__init__.py

import os

env = os.getenv("DJANGO_ENV", "dev").lower()

if env in {"prod", "production"}:
    from .prod import *
else:
    from .dev import *