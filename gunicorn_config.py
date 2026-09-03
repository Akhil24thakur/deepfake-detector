import os

timeout = 120
workers = 1
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
preload_app = True
