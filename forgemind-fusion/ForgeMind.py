# Assuming you have not changed the general structure of the template no modification is needed in this file.
from . import commands
from .lib import fusionAddInUtils as futil
from .commands.Login import entry as login
import adsk.core


def run(context):
    try:
        if not context['IsApplicationStartup']:
            app = adsk.core.Application.get()
            ui = app.userInterface
            
            # Check if the user is authenticated
            if login.is_user_authenticated():
                ui.messageBox("ForgeMind is running with authenticated user. Go to ForgeMind.dev to start using it.")
            else:
                ui.messageBox("Please log in to use ForgeMind.")
            
        # This will run the start function in each of your commands as defined in commands/__init__.py
        commands.start()

    except:
        futil.handle_error('run')


def stop():
    try:
        # Remove all of the event handlers your app has created
        futil.clear_handlers()

        # This will run the start function in each of your commands as defined in commands/__init__.py
        commands.stop()

    except:
        futil.handle_error('stop')