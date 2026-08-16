import { createClient } from '@supabase/supabase-js';

// TODO: Replace with your actual Supabase project URL and public Anon Key
export const supabaseUrl = 'https://accvisfrkbugfeowowhc.supabase.co';
export const supabaseKey = 'sb_publishable_ObNS1j9RHnLhoH_dvI5MXA_1qZQC-G5';

export const supabase = createClient(supabaseUrl, supabaseKey);
