# -*- coding: utf-8 -*-
#!/usr/bin/env python
import os
import sys
import codecs

# تنظیم encoding برای پشتیبانی از کاراکترهای یونیکد
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(__file__), 'amlak_mashhad'))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    execute_from_command_line(sys.argv)

