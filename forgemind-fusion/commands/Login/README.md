# ForgeMind Login Module with Supabase Authentication

This module provides authentication functionality for the ForgeMind Fusion 360 add-in, leveraging Supabase for user authentication.

## Features

- User login via email and password
- Integration with Supabase authentication
- "Remember Me" functionality
- Graceful error handling for authentication failures
- Proper session management

## Setup Instructions

1. **Install Required Package**

   ```bash
   pip install supabase
   ```

2. **Configure Supabase Credentials**

   Update the `forgemind-fusion/lib/supabase_config.py` file with your Supabase project details:

   ```python
   # Supabase URL - replace with your project URL
   SUPABASE_URL = "https://your-project-id.supabase.co"

   # Supabase API Key - replace with your project's anon key
   SUPABASE_KEY = "your-supabase-anon-key"
   ```

   **Important**: Use your project's **anon/public key**, not the service_role key!

3. **Create Users in Supabase**

   - In your Supabase dashboard, go to Authentication > Users
   - Add users with email and password
   - Alternatively, use the Supabase Auth API to implement sign-up functionality

## How It Works

1. When the add-in starts, it first displays the login dialog
2. User enters email and password
3. The system verifies credentials against Supabase authentication
4. If valid, the user is authenticated and can use the add-in
5. If invalid, they see an error message and can retry
6. If cancel is clicked, the add-in terminates

## Troubleshooting

- If Supabase authentication fails, check your network connection
- Verify that your Supabase URL and API key are correct
- Check the logs for detailed error messages
- Make sure the user exists in your Supabase project

## Security Considerations

- The current implementation only stores the authentication token temporarily in memory
- For production use, consider implementing:
  - Secure token storage for "Remember Me" functionality
  - Token refresh mechanisms
  - Session timeout handling
  - Two-factor authentication

## Future Enhancements

- Password reset functionality
- User registration directly from the add-in
- Profile management
- Role-based access control
- Auto-logout after period of inactivity 