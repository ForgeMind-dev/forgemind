"""
Authentication Configuration

This file contains the configuration and utilities needed for authentication.
It communicates with the backend server for user verification and session management.
"""

import os
import sys
import json
import urllib.request
import urllib.error
from . import fusionAddInUtils as futil

# Backend API URL - Try to get from environment variable or use default
BACKEND_URL = os.getenv("FORGEMIND_BACKEND_URL", "https://forgemind-backend.onrender.com")
futil.log(f"Using backend URL: {BACKEND_URL}")

# Store the current session token
current_session = None

def make_request(endpoint, data=None, method='POST', headers=None):
    """
    Makes a request to the backend API.
    
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
    url = f"{BACKEND_URL}{endpoint}"
    headers = headers or {}
    headers['Content-Type'] = 'application/json'
    
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
            futil.log(f"API error: {error_body.get('message', str(e))}")
            return error_body
        except:
            futil.log(f"HTTP error: {str(e)}")
            return {"status": "error", "message": str(e), "is_valid": False}
    except Exception as e:
        futil.log(f"Request error: {str(e)}")
        return {"status": "error", "message": str(e), "is_valid": False}

def verify_credentials(email, password):
    """
    Verifies user credentials with the backend server.
    
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
    
    response = make_request('/auth/verify', {
        "email": email,
        "password": password
    })
    
    if response.get("is_valid", False):
        # Store the session information
        current_session = response.get("session", {})
        futil.log(f"Authentication successful for user: {email}")
        return True
    else:
        futil.log(f"Authentication failed: {response.get('message', 'Unknown error')}")
        return False

def validate_session():
    """
    Validates the current session with the backend server.
    
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
    
    response = make_request('/auth/validate-session', method='POST', headers=headers)
    return response.get("is_valid", False)

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