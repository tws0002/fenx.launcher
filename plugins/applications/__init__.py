plugin_name = 'applications'
version = '0.4'
author = 'paulwinex'
url = ''
doc_url = ''

def get():
    from .plugin import ApplicationsPlugin
    return ApplicationsPlugin