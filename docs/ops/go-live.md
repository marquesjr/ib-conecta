# Go-live e validação final

Issue [#40](https://github.com/marquesjr/ib-conecta/issues/40). Última fatia do épico [#17](https://github.com/marquesjr/ib-conecta/issues/17).

O go-live é um roteiro para **pessoa**: parte dele é automática (smoke test abaixo), parte exige acesso à AWS, ao CMS com login real e à administração da igreja. Marque cada item na issue #40 conforme for confirmando.

## 1. Smoke test automático

Só faz `GET` anônimo. Não envia formulário, não cria conta e não grava nada no banco, então pode rodar em produção a qualquer hora.

```bash
python scripts/smoke_golive.py
# outro ambiente:
python scripts/smoke_golive.py --url http://localhost:8000
```

| Checagem | O que confirma |
|---|---|
| HTTP redireciona para HTTPS | Caddy com certificado e redirect ativos |
| Apex redireciona para www | `ibsantaleopoldina.com.br` → `www`, preservando o caminho |
| Health check | Django + PostgreSQL respondendo (`/healthz/`) |
| Home e páginas públicas | Planeje sua visita, Contribuições, Privacidade em HTML |
| Formulários públicos | Pedido de oração e Quero conhecer com `<form>` e token CSRF |
| Login | `/conta/entrar/` com formulário |
| Área privada e escalas | Anônimo é mandado para o login (nada vaza) |
| CMS | `/admin/` manda para `/admin/login/` |

Saída esperada em produção: `14/14 checagens ok` (em `http://localhost` são 12: as checagens de HTTPS e apex ficam de fora). Código de saída 1 se qualquer item falhar.

Testes do próprio script: `python scripts/test_smoke_golive.py`.

## 2. Smoke manual (com login)

O script não entra com usuário. Com uma conta real de produção:

- [ ] Entrar em `/conta/entrar/` (com 2FA, se a conta tiver) e ver a área privada
- [ ] Abrir Ministérios e uma escala; abrir Louvores
- [ ] Entrar no CMS (`/admin/`), abrir uma página, salvar rascunho sem publicar
- [ ] Enviar **um** pedido de oração de teste pelo site e conferir que aparece em `/conta/pedidos-de-oracao/`; depois marcar como tratado

## 3. HTTPS, DNS e monitoramento

- [ ] Smoke test acima verde (cobre HTTPS e DNS)
- [ ] *Actions → Monitoramento do portal* com execuções recentes verdes ([uptime.md](uptime.md))
- [ ] Quem opera recebe e-mail de falha de workflow (Watch no repositório)

O GitHub costuma atrasar o cron de `*/5 * * * *` em repositórios com pouca atividade: em setembro/2026 as execuções agendadas saíram a cada 2 a 6 horas. Se isso não bastar, ligue um complemento gratuito (UptimeRobot) como diz o `uptime.md`.

## 4. Backup e restauração

Na EC2 (procedimento completo em [backup.md](../backup.md)):

- [ ] `journalctl -u ib-conecta-backup.service -n 50 --no-pager` mostra o backup da última madrugada sem erro
- [ ] `aws s3 ls s3://<bucket>/daily/ --recursive` lista o artefato do dia anterior
- [ ] Restauração testada nos últimos 30 dias (`scripts/restore.sh` em ambiente local ou LocalStack); anotar a data na issue #40

## 5. Privacidade e acessibilidade

- [ ] `/privacidade/` publicada (coberto pelo smoke test) e revisada pelo controlador ([privacidade.md](../privacidade.md))
- [ ] Checklist WCAG 2.2 AA e desempenho executado ([acessibilidade-desempenho.md](../acessibilidade-desempenho.md), PR #62)

## 6. Treinamento

- [ ] Administração percorreu o [roteiro de treinamento](../treinamento-administracao.md) e publicou uma notícia de teste sem ajuda técnica

## 7. Fechamento

- [ ] Atualizar as caixas do épico #17 (fatias #37, #38 e #39 já fechadas)
- [ ] Fechar #40 e, em seguida, #17
