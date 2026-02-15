
-- Add security_review column to scan_reports to store Agent_Security's verdict
ALTER TABLE public.scan_reports
ADD COLUMN security_review jsonb DEFAULT NULL;
