// src/supabaseClient.ts
import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = process.env.REACT_APP_SUPABASE_URL!;
const SUPABASE_ANON_KEY = process.env.REACT_APP_SUPABASE_ANON_KEY!;

// Create client with extended session timeout to prevent frequent refreshes
export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true,
    // Set a longer session expiry time (default is 1 hour = 3600 seconds)
    // This extends it to 24 hours to prevent refreshes during usage
    flowType: 'pkce'
  }
});
