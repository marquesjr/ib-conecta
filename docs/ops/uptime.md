# Monitoramento externo do portal

Issue [#36](https://github.com/marquesjr/ib-conecta/issues/36). Parte do épico [#17](https://github.com/marquesjr/ib-conecta/issues/17).

O portal em produção é checado **de fora da AWS**, a cada **5 minutos**, pelo GitHub Actions (`Monitoramento do portal`). A origem da checagem é a infra do GitHub, não a EC2 — se a VM, o Caddy ou o Django caírem, o alerta ainda dispara.

## O que é checado

URL canônica: `https://www.ibsantaleopoldina.com.br`

1. `GET /healthz/` — HTTP 200 e JSON `{"status": "ok"}` (aplicação + PostgreSQL)
2. `GET /` — HTTP 200 e HTML (Caddy + página pública)

Script local (o mesmo da Action):

```bash
python scripts/check-uptime.py
```

O agendamento `*/5 * * * *` só roda com o workflow em `master`. O GitHub pode atrasar o cron em carga alta; o alvo continua sendo 5 minutos.

## Quem recebe o alerta

Canal atual: **GitHub Issues + e-mail de quem observa o repositório**.

| Papel | Como é avisado | O que faz |
|---|---|---|
| Operador técnico | Issue `Incidente: portal IB Conecta fora do ar` (label `uptime-incident`) e falha do workflow | Diagnostica e recupera (abaixo) |
| Comunicação / pastor | **Não** recebem o alerta automaticamente | O operador avisa (WhatsApp institucional) se a queda passar de **15 minutos** |

O operador deve, neste repositório:

1. **Watch** → *All Activity*, ou no mínimo *Issues* e *Actions*
2. Em GitHub → Settings → Notifications, manter e-mail ligado para Issues e para workflows que falham

Use o mesmo e-mail de `budget_alert_email` no Terraform (`infra/aws/`), para custo e queda chegarem na mesma caixa.

Não há canal SMS. Complementos gratuitos (UptimeRobot, [Pulsetic](https://pulsetic.com/)) são opcionais se a igreja quiser e-mail/push fora do GitHub; este runbook permanece a fonte do procedimento.

## O que fazer em caso de queda

1. Confirmar: abra `https://www.ibsantaleopoldina.com.br/healthz/` e a home. Se só o seu computador falha, não é incidente.
2. Ver a Action vermelha em *Actions → Monitoramento do portal* (corpo da issue aponta o run).
3. SSH na VM: `terraform output ssh_command` em `infra/aws/` (usuário `ubuntu`). Publicar código novo **não** é este runbook — isso é o workflow **Deploy produção** (`docs/ops/deploy.md`).
4. Na pasta do clone:

   ```bash
   docker compose -f docker-compose.prod.yml --env-file .env.prod ps
   docker compose -f docker-compose.prod.yml --env-file .env.prod logs --tail=150 web caddy db
   ```

5. Disco e memória: `df -h`, `free -m`. Volume cheio derruba PostgreSQL e o `healthz`.
6. DNS: `www` e o apex devem apontar para o Elastic IP (`terraform output instance_public_ip`). Procedimento no README da raiz, seção DNS.
7. TLS: logs do Caddy se o certificado Let's Encrypt tiver falhado (`CADDY_TLS` vazio no `.env.prod`).
8. Recolocar o stack se os containers saíram:

   ```bash
   docker compose -f docker-compose.prod.yml --env-file .env.prod up -d
   ```

9. Se o banco estiver íntegro e só o processo caiu, o `up -d` basta. Restauração a partir do S3 é o procedimento da issue #33 — só use se houver perda de dados.
10. Quando `python scripts/check-uptime.py` voltar a passar, a próxima Action fecha o incidente. Comente na issue o que foi feito.
11. Se passar de 15 minutos fora do ar, avise a comunicação da igreja pelo WhatsApp institucional: o site público está indisponível; não peça para membros “tentarem de novo” até o operador confirmar.

## Teste de alerta

No GitHub: *Actions → Monitoramento do portal → Run workflow*. Marque **Simular queda e disparar um alerta de teste**.

Isso abre e fecha na hora uma issue `Teste de alerta: monitoramento do portal`. Confirme o e-mail de notificação. Não simule derrubando a VM de produção.

## Arquivos

- `.github/workflows/uptime.yml` — cron, alerta e encerramento do incidente
- `scripts/check-uptime.py` — checagem HTTP reutilizável
