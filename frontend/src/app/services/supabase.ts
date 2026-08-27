import { createClient } from '@supabase/supabase-js';

// TODO: Replace with your actual Supabase project URL and public Anon Key
export const supabaseUrl = 'https://accvisfrkbugfeowowhc.supabase.co';
export const supabaseKey =
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFjY3Zpc2Zya2J1Z2Zlb3dvd2hjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODY4NzY0MDgsImV4cCI6MjEwMjQ1MjQwOH0.ui1p3JPDPJe1mv0JYWxFA_0pfzE9qQY-LxZYRgUaXHg';

export const supabase = createClient(supabaseUrl, supabaseKey);
