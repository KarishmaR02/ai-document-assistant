import { createClient } from '@supabase/supabase-js';
import { environment } from '../../environments/environment';

export const supabaseUrl = environment.supabaseUrl;
export const supabaseKey = environment.supabaseKey;

export const supabase = createClient(supabaseUrl, supabaseKey);
