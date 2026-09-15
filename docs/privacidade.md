# Privacidade, consentimento e retenção

Como o **IB Conecta** aplica a LGPD ao que o portal já coleta. A política pública está em [`/privacidade/`](https://www.ibsantaleopoldina.com.br/privacidade/) (texto versionado no código, não no CMS). Issue [#37](https://github.com/marquesjr/ib-conecta/issues/37), ADR 0011.

## O que o visitante vê

- Página **Privacidade** no rodapé de todas as telas.
- Pedido de oração, Quero conhecer e inscrição em retiro pedem consentimento e apontam para essa página.
- Retiro explica proteção de menores (responsável legal e descarte de dados médicos/de nascimento).

Não crie no Wagtail uma página com o endereço `privacidade`: a rota do Django prevalece.

## Controlador e responsáveis

| Papel | Responsável | Escopo |
|---|---|---|
| Controlador | Igreja Batista em Santa Leopoldina | Tratamento no portal |
| Encarregado operacional | Administração da igreja | Direitos do titular, exclusão, contas |
| Pedidos de oração e Quero conhecer | Pastor e comunicação | Acompanhar, concluir, pedir exclusão |
| Inscrições e retiros | Comissão de eventos | Rol, check-in, prazo de descarte |
| Infraestrutura e backup | Operador técnico | Timer de backup, S3, descarte no arranque |

Canal do titular: WhatsApp institucional (número configurável no Wagtail) ou conversa após o culto. Não é plantão 24 horas.

## Prazos

| Dado | Prazo | Descarte | Quem |
|---|---|---|---|
| Pedido de oração | Aberto enquanto houver acompanhamento; **12 meses** após status concluído | Pastor/comunicação na área da conta; administração exclui o registro | Pastor e comunicação |
| Quero conhecer | **12 meses** após concluído | O mesmo | Pastor e comunicação |
| Inscrição em evento (nome, e-mail, telefone) | **90 dias** após o evento | Comissão + administração | Comissão de eventos |
| Dados médicos, restrições, responsável e nascimento de menores no retiro | **30 dias** após o término (padrão de `EventPage.sensitive_retain_days`; o evento pode configurar outro prazo) | `python manage.py discard_retreat_sensitive_data` | Comissão e administração |
| Conta de membro | Enquanto permanecer na igreja | Administração remove o usuário | Administração |
| Backup cifrado no S3 | 30 dias (`daily/`) e 366 dias (`monthly/`) | Lifecycle do bucket | Operador técnico |

O comando de retiro **esvazia** notas médicas, restrições alimentares, dados do responsável e a data de nascimento de quem é menor. **Não apaga o nome** no rol.

Backups gerados *antes* do descarte ainda podem conter o dado até expirarem. O backup diário dispara o descarte **antes** do `pg_dump` para não renovar o prazo.

## Como rodar o descarte de retiro

Manual, com o stack no ar:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod exec web python manage.py discard_retreat_sensitive_data
```

Local:

```bash
docker compose exec web python manage.py discard_retreat_sensitive_data
```

Atalho: `scripts/discard-sensitive-data.sh`.

O mesmo comando roda:

1. No **entrypoint** do container `web` (cada arranque/deploy).
2. No **backup diário** (`scripts/backup.sh`), antes do dump, salvo `BACKUP_SKIP_DISCARD=1`.

Saída típica: `N inscrição(ões) com dados sensíveis descartados.`

## Cookies mínimos

Sessão autenticada e CSRF. Sem analytics, anúncios ou pixels próprios. Embeds de YouTube usam `youtube-nocookie.com`. Sem banner: não há cookie não essencial.

## CMS e conteúdo pastoral

A política pública **não** se edita no Wagtail. Comunicação e pastor **não** publicam pedido de oração, dado médico, nome ou foto de menor nas páginas públicas (`docs/treinamento-administracao.md`).
