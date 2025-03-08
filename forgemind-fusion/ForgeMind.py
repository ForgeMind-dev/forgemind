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
            
            # First check authentication state before any UI actions
            authenticated_before = login.is_user_authenticated()
            
            # Start all commands - this may trigger login/logout dialogs
            commands.start()
            
            # Check authentication state AGAIN after commands have run
            # This ensures we don't say "authenticated" if the user just logged out
            authenticated_after = login.is_user_authenticated()
            
            # Only show the "authenticated" message if the user is STILL authenticated
            # after all command processing (they might have logged out)
            if authenticated_after:
                ui.messageBox("ForgeMind is running with authenticated user. Go to ForgeMind.dev to start using it.")
            else:
                ui.messageBox("Please log in to use ForgeMind.")
        else:
            # This will run on Fusion startup - just start commands normally
            # (login command will check authentication status)
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