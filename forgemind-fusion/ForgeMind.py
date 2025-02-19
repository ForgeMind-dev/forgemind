# Assuming you have not changed the general structure of the template no modification is needed in this file.
from . import commands
from .lib import fusionAddInUtils as futil
import adsk.core
from .logic.main import run_logic


def run(context):
    try:
        if not context['IsApplicationStartup']:
            app = adsk.core.Application.get()
            ui = app.userInterface
            ui.messageBox("ForgeMind is running. Go to Utilities > ForgeMind to start using it.")

            run_logic(app, ui, context)
            
        # This will run the start function in each of your commands as defined in commands/__init__.py
        commands.start()

    except:
        futil.handle_error('run')


def stop(context):
    try:
        # Remove all of the event handlers your app has created
        futil.clear_handlers()

        # This will run the start function in each of your commands as defined in commands/__init__.py
        commands.stop()

    except:
        futil.handle_error('stop')