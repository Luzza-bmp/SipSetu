-- ============================================================
-- Migration 003: pgvector support + schema hardening
-- Run AFTER 001_tables.sql and 002_tables.sql
-- ============================================================

-- 1. Enable pgvector (requires pg_vector extension installed on the server)
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Add the embedding column to resumes
--    all-MiniLM-L6-v2 produces 384-dimensional vectors
ALTER TABLE public.resumes
    ADD COLUMN IF NOT EXISTS embedding vector(384),
    ADD COLUMN IF NOT EXISTS parsed_skills  TEXT,   -- pipe-separated extracted skills
    ADD COLUMN IF NOT EXISTS parsed_experience_years NUMERIC(4,1); -- e.g. 3.5

-- 3. Add a description column to jobs so we can vectorise it at rank time
ALTER TABLE public.jobs
    ADD COLUMN IF NOT EXISTS description TEXT,
    ADD COLUMN IF NOT EXISTS required_experience_years NUMERIC(4,1) DEFAULT 0;

-- 4. HNSW index for fast approximate cosine similarity search
--    (IVFFlat is lighter but needs a VACUUM + analyse after inserts)
CREATE INDEX IF NOT EXISTS resumes_embedding_hnsw
    ON public.resumes
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- 5. Add an applications table so we only rank people who actually applied
--    (your current schema has no explicit "apply" step)
CREATE TABLE IF NOT EXISTS public.applications (
    application_id  uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    job_id          uuid NOT NULL REFERENCES public.jobs(job_id)      ON DELETE CASCADE,
    applicant_id    uuid NOT NULL REFERENCES public.applicants(user_id) ON DELETE CASCADE,
    applied_at      TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT applications_pkey      PRIMARY KEY (application_id),
    CONSTRAINT applications_unique    UNIQUE (job_id, applicant_id)   -- one application per job
);

-- 6. Update rankings to reference applications instead of a bare resume_id
--    (keeps historical scores if you re-rank later)
ALTER TABLE public.rankings
    ADD COLUMN IF NOT EXISTS semantic_score   DOUBLE PRECISION,
    ADD COLUMN IF NOT EXISTS experience_score DOUBLE PRECISION;

-- Note: existing matching_score column is kept for backwards compat.
-- New code writes to semantic_score + experience_score and derives matching_score.