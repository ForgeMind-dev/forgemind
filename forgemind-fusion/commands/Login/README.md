# ForgeMind Login Module

## Overview
The Login module provides user authentication functionality for the ForgeMind add-in for Autodesk Fusion 360. It implements a login dialog that collects user credentials, validates them, and manages the login state throughout the add-in's lifecycle.

## Features
- Login dialog with email/password inputs and "Remember Me" option
- Input validation with error messaging
- Persistence of login state across commands
- Handling of login cancellation
- Integration with Supabase authentication service
- Fallback authentication for when Supabase is not available

## Authentication Flow
1. When the add-in starts, the login dialog is presented first
2. User enters credentials (email and password)
3. Credentials are validated:
   - If Supabase is available, authentication is performed via Supabase
   - If Supabase is not available, fallback to local validation with hardcoded credentials
4. On successful login, the add-in continues normal operation
5. On failed login, the dialog remains open with an error message
6. If the user cancels the login, the add-in shuts down

## Usage in Other Commands
Other commands should check the login status before executing their functionality:

```python
from ..Login import entry as login

# In your command_execute function:
if not login.get_login_status():
    ui.messageBox("Please log in to use this feature.")
    return
    
# Continue with your command logic if the user is logged in
```

## Testing Without Supabase
For testing without Supabase, the module accepts the following hardcoded credentials:
- Email: ata@forgemind.dev
- Password: test123

## Security Notes
In a production environment, this module should be enhanced with:
- Secure credential storage for "Remember Me" functionality
- More robust fallback authentication when Supabase is unavailable
- Encryption of credentials during transmission
- Session management and timeout handling 