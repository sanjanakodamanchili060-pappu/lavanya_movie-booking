"""
Compatibility package: Aliases 'yourproject' to 'jishitha' 
so that any Render Start Command pointing to 'yourproject.wsgi:application' works seamlessly.
"""
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jishitha.settings')

from jishitha.wsgi import application
