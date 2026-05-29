-- WARNING: This schema is for context only and is not meant to be run automatically.
-- Run it manually in your Supabase SQL editor or with psql.

CREATE TABLE IF NOT EXISTS public.FitForge (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT FitForge_pkey PRIMARY KEY (id)
);
