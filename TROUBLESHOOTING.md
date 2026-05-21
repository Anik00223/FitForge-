# FitForge Troubleshooting

## agno ImportError in Docker

This project uses NVIDIA NIM through the OpenAI SDK, not Gemini or agno. If you are adapting an older Gemini build, do not mix `agno`, `google-generativeai`, and `openai` randomly. Keep one AI provider path per build.

## Supabase Connection Refused

Check `DATABASE_URL` in `.env`. Supabase URLs must look like:

```text
postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

Confirm the password is URL-safe, the project is not paused, and local network/firewall rules allow outbound PostgreSQL traffic.

## Static Files 404

Run:

```bash
python manage.py collectstatic --noinput
```

In Docker, confirm the `static_volume` is mounted for both `web` and `nginx`, and that `nginx.conf` points `/static/` to `/app/staticfiles/`.

## Redis Connection Error

For Docker, use:

```text
REDIS_URL=redis://redis:6379/0
```

For local development, use `config.settings.development`; it falls back to an in-memory cache and database sessions so Redis is not required.

## CSRF Verification Failed

Make sure every POST form contains `{% csrf_token %}`. If deploying behind Nginx, confirm forwarded protocol headers are present and `ALLOWED_HOSTS` includes the host you are using.

## Session Not Persisting

In production, sessions use the configured cache. Confirm Redis is reachable. In development, sessions use the database, so run:

```bash
python manage.py migrate
```

Also check that browser cookies are not blocked.

## Port 8000 Already In Use

Run Django on another port:

```bash
python manage.py runserver 0.0.0.0:8001
```

For Docker, change the left side of the port mapping, for example `"8001:8000"`.

## Migration Errors On Fresh Clone

Run migrations from the repository root:

```bash
python manage.py migrate
```

If you previously created a broken local SQLite database, delete `db.sqlite3` and run migrations again.

## NVIDIA API Quota Or Authentication Error

Confirm `.env` contains:

```text
NVIDIA_API_KEY=nvapi-your-key
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_MODEL=meta/llama-3.3-70b-instruct
```

If the key is correct but generation still fails, check your NVIDIA account quota and model access.
