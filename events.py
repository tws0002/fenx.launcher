

def on_launcher_started():
    """
    Called after launcher started and initialized
    """

def on_before_launcher_closed():
    """
    Called before launcher exit process. Plugins is still active.
    """

def on_launcher_closed():
    """
    Called before QApplication.quit(). Plugins is not active.
    """

