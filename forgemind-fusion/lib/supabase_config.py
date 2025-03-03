"""
Supabase Configuration

This file contains the configuration details needed to connect to Supabase services.
It's designed to work both when the Supabase package is available and when it's not.

In a production environment, these values should be stored securely and not hard-coded.
Consider using environment variables or a secure configuration manager.
"""

import os
from . import fusionAddInUtils as futil

# Flag to track if Supabase features are available
SUPABASE_ENABLED = False

# Try to import Supabase to check if it's available
try:
    from supabase import create_client, Client
    SUPABASE_ENABLED = True
    futil.log("Supabase package is available")
except ImportError:
    futil.log("Supabase package not available. Install with 'pip install supabase'")

# Supabase URL - Your project URL
SUPABASE_URL = "https://euxilwmhugndmualbpcs.supabase.co"

# Supabase API Key - Your project's anon/public key
# This should be your public anon key, not the service_role key
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV1eGlsd21odWduZG11YWxicGNzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk5Mzk5ODAsImV4cCI6MjA1NTUxNTk4MH0.XR--n_8IVLWNgvPfnyYu8Z9J1RRbQD6nYvHVtax715U"

# Initialize Supabase client if possible
supabase = None
if SUPABASE_ENABLED:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        futil.log(f"Supabase client initialized with URL: {SUPABASE_URL}")
    except Exception as e:
        futil.log(f"Error initializing Supabase client: {str(e)}")
        SUPABASE_ENABLED = False
        
# Function to get Supabase client (safer than direct access)
def get_client():
    """
    Returns the Supabase client if available, None otherwise.
    
    This function provides a safe way to access the Supabase client
    without having to check for its existence each time.
    
    Returns:
    --------
    Client or None
        The Supabase client if available, None otherwise
    """
    return supabase

def is_available():
    """
    Returns whether Supabase functionality is available.
    
    This checks both that the package is installed and that
    the client was successfully initialized.
    
    Returns:
    --------
    bool
        True if Supabase is available and initialized, False otherwise
    """
    return SUPABASE_ENABLED and supabase is not None 