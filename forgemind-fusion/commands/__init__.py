# Here you define the commands that will be added to your add-in
# If you want to add an additional command, duplicate one of the existing directories and import it here.
# You need to use aliases (import "entry" as "my_module") assuming you have the default module named "entry"
# from .Basic import entry as basic
# from .Browser import entry as browser
# from .Everything import entry as everything
from .Info import entry as info
from .Login import entry as login
# from .Selections import entry as selections
# from .Table import entry as table

# This Template will automatically call the start() and stop() functions.
# By default the order you add the commands to this list will be the order they appear in the UI
commands = [
    # browser,
    login,  # Login should be first to ensure authentication before other commands
    info,
    # basic,
    # selections,
    # everything,
    # table,
]


# Assumes you defined a "start" function in each of your modules.
# These functions will be run when the add-in is stopped.
def start():
    # Start the login command first to ensure authentication
    login.start()
    
    # Only start other commands if the user is authenticated
    if login.is_user_authenticated():
        # Start all other commands
        for command in commands:
            if command != login:  # Skip login as it's already started
                command.start()
    else:
        # If not authenticated, only the login command will be started
        print("User not authenticated. Only login command is available.")


# Assumes you defined a "start" function in each of your modules.
# These functions will be run when the add-in is stopped.
def stop():
    for command in commands:
        command.stop()
