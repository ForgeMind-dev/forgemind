"""
Authentication Configuration

This file contains the configuration and utilities needed for authentication.
It communicates with the Supabase authentication API.
"""

import os
import sys
import json
import urllib.request
import urllib.error
from . import fusionAddInUtils as futil

# Supabase Configuration
SUPABASE_URL = os.getenv("FORGEMIND_BACKEND_URL", "https://euxilwmhugndmualbpcs.supabase.co")
SUPABASE_ANON_KEY = os.getenv("FORGEMIND_SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV1eGlsd21odWduZG11YWxicGNzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk5Mzk5ODAsImV4cCI6MjA1NTUxNTk4MH0.XR--n_8IVLWNgvPfnyYu8Z9J1RRbQD6nYvHVtax715U")

futil.log(f"Using Supabase URL: {SUPABASE_URL}")

# Store the current session token
current_session = None

def test_connection():
    """
    Tests the connection to the Supabase server.
    
    Returns:
    --------
    tuple
        (bool, str) - (is_connected, error_message)
    """
    try:
        # Just check if we can reach the Supabase domain
        req = urllib.request.Request(
            SUPABASE_URL,
            method='GET',
            headers={
                'apikey': SUPABASE_ANON_KEY
            }
        )
        with urllib.request.urlopen(req) as response:
            return True, None
    except urllib.error.HTTPError as e:
        # Any response from Supabase means the service is available
        return True, None
    except urllib.error.URLError as e:
        return False, f"Connection error: {str(e.reason)}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def make_request(endpoint, data=None, method='POST', headers=None):
    """
    Makes a request to the Supabase API.
    
    Parameters:
    -----------
    endpoint : str
        The API endpoint to call (without the base URL)
    data : dict, optional
        The data to send in the request body
    method : str, optional
        The HTTP method to use
    headers : dict, optional
        Additional headers to include in the request
        
    Returns:
    --------
    dict
        The parsed JSON response from the server
    """
    # Test connection first
    is_connected, error_msg = test_connection()
    if not is_connected:
        futil.log(f"Supabase server not available: {error_msg}")
        return {
            "status": "error",
            "message": f"Supabase server not available: {error_msg}",
            "is_valid": False
        }
    
    url = f"{SUPABASE_URL}{endpoint}"
    headers = headers or {}
    
    # Add required Supabase headers
    headers.update({
        'Content-Type': 'application/json',
        'apikey': SUPABASE_ANON_KEY,
        'X-Client-Info': 'forgemind-fusion',
    })
    
    try:
        if data:
            data = json.dumps(data).encode('utf-8')
        
        futil.log(f"Making request to: {url}")
        futil.log(f"Request headers: {json.dumps({k: v for k, v in headers.items() if k != 'apikey'})}")
        
        req = urllib.request.Request(
            url,
            data=data,
            headers=headers,
            method=method
        )
        
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        # Parse error response if available
        try:
            error_body = json.loads(e.read().decode())
            error_msg = error_body.get('error_description', error_body.get('msg', error_body.get('message', str(e))))
            futil.log(f"API error: {error_msg}")
            return {"status": "error", "message": error_msg, "is_valid": False}
        except:
            error_msg = str(e)
            futil.log(f"HTTP error: {error_msg}")
            return {"status": "error", "message": error_msg, "is_valid": False}
    except Exception as e:
        futil.log(f"Request error: {str(e)}")
        return {"status": "error", "message": str(e), "is_valid": False}

def verify_credentials(email, password):
    """
    Verifies user credentials with Supabase authentication.
    
    Parameters:
    -----------
    email : str
        The user's email address
    password : str
        The user's password
        
    Returns:
    --------
    bool
        True if credentials are valid, False otherwise
    """
    global current_session
    
    # Log the URL we're using (without sensitive data)
    futil.log(f"Attempting authentication with URL: {SUPABASE_URL}/auth/v1/token?grant_type=password")
    
    response = make_request('/auth/v1/token?grant_type=password', {
        "email": email,
        "password": password,
        "gotrue_meta_security": {}  # Required by Supabase auth
    })
    
    # Log the full response for debugging (excluding sensitive data)
    sanitized_response = {k: v for k, v in response.items() if k not in ['access_token', 'refresh_token']}
    futil.log(f"Auth response (sanitized): {json.dumps(sanitized_response)}")
    
    if "access_token" in response:
        # Store the session information
        current_session = {
            "access_token": response["access_token"],
            "refresh_token": response.get("refresh_token"),
            "user": response.get("user", {})
        }
        futil.log(f"Authentication successful for user: {email}")
        return True
    else:
        error_msg = response.get("message", "Invalid credentials")
        futil.log(f"Authentication failed: {error_msg}")
        return False

def validate_session():
    """
    Validates the current session with Supabase.
    
    Returns:
    --------
    bool
        True if the session is valid, False otherwise
    """
    if not current_session or not current_session.get("access_token"):
        return False
    
    headers = {
        "Authorization": f"Bearer {current_session['access_token']}"
    }
    
    response = make_request('/auth/v1/user', method='GET', headers=headers)
    return "id" in response

def get_current_user():
    """
    Returns information about the currently logged-in user.
    
    Returns:
    --------
    dict or None
        User information if available, None otherwise
    """
    return current_session.get("user") if current_session else None

def clear_session():
    """
    Clears the current session.
    """
    global current_session
    current_session = None

def get_session_data():
    """
    Returns the current session data for persistence.
    
    Returns:
    --------
    dict or None
        Session data if available, None otherwise
    """
    if current_session:
        return {
            "access_token": current_session.get("access_token"),
            "refresh_token": current_session.get("refresh_token"),
            "user": current_session.get("user")
        }
    return None

def restore_session(session_data):
    """
    Restores a previously saved session.
    
    Parameters:
    -----------
    session_data : dict
        The session data to restore
    """
    global current_session
    if session_data and "access_token" in session_data:
        current_session = session_data
        futil.log("Session restored from saved data")
        return True
    return False 