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
        req = urllib.request.Request(
            f"{SUPABASE_URL}/auth/v1/user",
            method='GET',
            headers={
                'apikey': SUPABASE_ANON_KEY,
                'Authorization': f'Bearer {SUPABASE_ANON_KEY}'
            }
        )
        with urllib.request.urlopen(req) as response:
            return True, None
    except urllib.error.HTTPError as e:
        if e.code == 404:
            # A 404 on this path is expected for non-authenticated requests
            return True, None
        return False, f"Server error (HTTP {e.code}): {str(e)}"
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
    headers['Content-Type'] = 'application/json'
    headers['apikey'] = SUPABASE_ANON_KEY
    
    try:
        if data:
            data = json.dumps(data).encode('utf-8')
        
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
            error_msg = error_body.get('message', error_body.get('error_description', str(e)))
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
    
    response = make_request('/auth/v1/token?grant_type=password', {
        "email": email,
        "password": password
    })
    
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
        error_msg = response.get("message", "Unknown error")
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