# Deploy em push para master via GitHub Actions + SSM

Publicar produção deixa de ser SSH + `git pull` + `compose up --build`. Push (e `workflow_dispatch`) em `master` dispara o workflow **Deploy produção**, que assume role IAM por OIDC do GitHub e envia AWS-RunShellScript à EC2 (`t4g.small` existente, Compose + Caddy). A VM continua dona do `.env.prod` e do rebuild.

Recusado neste desenho:

- Abrir SSH `0.0.0.0/0` ou os CIDRs do GitHub Actions (a SG só libera 22 para o IP do operador — ADR 0006).
- Runner self-hosted na EC2: o repositório é **público**; um PR malicioso poderia executar job na VM de produção. A `t4g.small` (2 GB) também não deve hospedar o runner junto do Compose.
- Access keys de IAM user no GitHub: OIDC com `sub` = `repo:marquesjr/ib-conecta:ref:refs/heads/master` e `aud` = `sts.amazonaws.com`.

Issue #17. Runbook `docs/ops/deploy.md`.
