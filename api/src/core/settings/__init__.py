"""
Django settings module.
"""

import os

# Load the appropriate settings based on the environment
environment = os.getenv("DJANGO_ENV", "development")

if environment == "production":
    from .production import *
elif environment == "staging":
    from .staging import *
else:
    from .development import *
