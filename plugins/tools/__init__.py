plugin_name = 'tools'
version = '0.3'
author = 'paulwinex'
url = ''
doc_url = ''

def get():
    from .plugin import ToolsPlugin
    return ToolsPlugin