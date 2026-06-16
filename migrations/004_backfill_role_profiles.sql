-- Backfill role-specific profile rows for users created before auth registration
-- started inserting into public.applicants/public.recruiters.

INSERT INTO public.applicants (user_id)
SELECT user_id
FROM public.users
WHERE role = 'applicant'
ON CONFLICT (user_id) DO NOTHING;

INSERT INTO public.recruiters (user_id)
SELECT user_id
FROM public.users
WHERE role = 'recruiter'
ON CONFLICT (user_id) DO NOTHING;
