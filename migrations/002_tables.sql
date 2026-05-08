-- Add application status to rankings
ALTER TABLE public.rankings  
ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'Pending';

ALTER TABLE public.rankings
ADD CONSTRAINT rankings_status_check  
CHECK (status IN ('Pending', 'Shortlisted', 'Rejected'));