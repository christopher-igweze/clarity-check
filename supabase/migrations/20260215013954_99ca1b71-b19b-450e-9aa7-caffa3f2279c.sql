
-- Add github_access_token to profiles for private repo access
ALTER TABLE public.profiles
ADD COLUMN github_access_token text DEFAULT NULL;
