# Compute de produção: EC2 t4g.small

A VM de produção é `t4g.small` (2 vCPU Graviton, 2 GB) em `us-east-2`. Micro (1 GB) foi recusado: Gunicorn + Postgres + Caddy + Wagtail com a home fotográfica não cabem com margem. `t3.small` dá a mesma RAM mais cara em x86. Gunicorn em produção usa 1 worker (`WEB_CONCURRENCY=1`), não o default 3 do `gunicorn.conf.py`.
