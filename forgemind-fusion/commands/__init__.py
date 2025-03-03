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
    info,
    # basic,
    # selections,
    # everything,
    # table,
]

login_commands = [
    login
]

# Assumes you defined a "start" function in each of your modules.
# These functions will be run when the add-in is started.
def start():
    # First, run the login command
    for cmd in login_commands:
        cmd.start()
    
    # Start other commands regardless - the Info command should check login status internally
    for command in commands:
        command.start()


# Assumes you defined a "stop" function in each of your modules.
# These functions will be run when the add-in is stopped.
def stop():
    for command in commands:
        command.stop()
    
    for cmd in login_commands:
        cmd.stop()
