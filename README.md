<div align="center">

# IB Conecta

**Portal de comunicação, evangelização e gestão da Igreja Batista em Santa Leopoldina.**

Acolhe quem chega de fora até o culto e o WhatsApp pastoral — e dá à igreja um só lugar autenticado para operar escalas, documentos, eventos, retiros e louvor.

[![Deploy](https://github.com/marquesjr/ib-conecta/actions/workflows/deploy.yml/badge.svg)](https://github.com/marquesjr/ib-conecta/actions/workflows/deploy.yml)
[![Monitoramento](https://github.com/marquesjr/ib-conecta/actions/workflows/uptime.yml/badge.svg)](https://github.com/marquesjr/ib-conecta/actions/workflows/uptime.yml)
[![Licença: MIT](https://img.shields.io/badge/licen%C3%A7a-MIT-green.svg)](LICENSE)

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.1%E2%80%935.2-092E20?logo=django&logoColor=white)
![Wagtail](https://img.shields.io/badge/Wagtail-6.4%E2%80%937.0-43B1B0?logo=wagtail&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![Caddy](https://img.shields.io/badge/Caddy-2-1F88C0?logo=caddy&logoColor=white)

[Site em produção](https://www.ibsantaleopoldina.com.br) · [Documentação](docs/) · [Issues](https://github.com/marquesjr/ib-conecta/issues)

</div>

---

## Sumário

- [Sobre o projeto](#sobre-o-projeto)
- [Funcionalidades](#funcionalidades)
- [Stack](#stack)
- [Primeiros passos](#primeiros-passos)
- [Dados de demonstração](#dados-de-demonstração)
- [Testes](#testes)
- [Contas, perfis e privacidade](#contas-perfis-e-privacidade)
- [Produção](#produção)
- [Estrutura do repositório](#estrutura-do-repositório)
- [Documentação](#documentação)
- [Licença](#licença)

## Sobre o projeto

O IB Conecta atende dois públicos:

- **Visitante ou buscador**, muitas vezes no celular e com conexão limitada, em Santa Leopoldina ou na zona rural: quer saber se é bem-vindo, quando é o culto, como chegar e como falar com a igreja.
- **Membro ou liderança autenticados** (líder de ministério, comunicação, pastor, tesouraria, comissão de eventos, administração): usa a área privada para escalas, documentos, eventos, retiros, coletânea de louvores e playlists — sem tornar nada disso público.

Quem opera o CMS (comunicação, pastor, administração) publica o conteúdo da igreja pelo admin Wagtail. Textos, horários, WhatsApp, PIX, redes sociais e o próximo culto são configurados lá, sem hardcode no código.

## Funcionalidades

### Site público

| Área | Rota |
|---|---|
| Página inicial | `/` |
| Planeje sua visita | `/planeje-sua-visita/` |
| Quero conhecer a igreja | `/quero-conhecer/` |
| Pedido de oração | `/pedido-de-oracao/` |
| Notícias | `/noticias/` |
| Agenda (com inscrição em eventos) | `/agenda/` |
| Sermões | `/sermoes/` |
| Transmissão ao vivo | `/ao-vivo/` |
| Contribuições via PIX | `/contribuicoes/` |
| Privacidade (LGPD) | `/privacidade/` |

- Páginas institucionais (história, crenças, ministérios, liderança), notícias, eventos, sermões e a página ao vivo são criadas e publicadas pelo CMS; rascunhos não ficam públicos.
- Sermões e transmissão usam URL externa (YouTube) incorporada sem autoplay — o portal não hospeda vídeo.
- A página de contribuições mostra a chave PIX configurada pela administração; o portal não processa cartão nem armazena dados bancários de terceiros.
- Pedidos de oração e contatos de "Quero conhecer a igreja" não aparecem no site público: pastor e comunicação os acompanham na área da conta.
- Fotografias da homepage vêm da API oficial do Instagram ou de exportação JSON da Meta, sem raspagem ([`docs/ops/instagram-acervo.md`](docs/ops/instagram-acervo.md)).

### Área privada (membros autenticados)

| Recurso | Rota |
|---|---|
| Biblioteca de documentos | `/area-privada/documentos/` |
| Ministérios e escalas | `/area-privada/ministerios/` |
| Comissão de eventos | `/area-privada/eventos/` |
| Retiro (check-in da equipe) | `/area-privada/eventos/<id>/retiro/` |
| Coletânea de louvores | `/area-privada/louvores/` |
| Playlists semanais do louvor | `/area-privada/playlists/` |

- **Documentos:** cada membro vê só o que foi liberado para o seu perfil (membros, comunicação/pastor, tesouraria ou administração). Arquivos privados ficam fora de `/media/` e só são baixados pela biblioteca autenticada.
- **Ministérios e escalas:** líderes cadastram ministérios e montam a escala mensal. O convocado confirma ou recusa pelo celular, substituições ficam registradas, e a escala exporta para calendário (`.ics`) e página de impressão em PDF.
- **Comissão de eventos:** calendário anual sobre os eventos da agenda pública (sem duplicar inscrição), com equipes, tarefas, checklists, fornecedores, materiais, orçamento com aprovação da tesouraria, comunicação com inscritos e relatório/atas privados. Membros só atualizam as tarefas e o checklist que lhes foram designados.
- **Retiros:** eventos da agenda com inscrição familiar — responsável legal, emergência, restrições alimentares/médicas, transporte/embarque, acomodação, lista de espera e status de pagamento PIX (sem dados bancários). Dados médicos e de menores são descartados após o prazo configurado no evento (`python manage.py discard_retreat_sensitive_data`; o entrypoint e o backup diário também disparam o comando).
- **Coletânea de louvores:** líderes criam, revisam e publicam cânticos com letra, cifra, partitura PDF, tom, andamento, tags, versões e licenciamento; o portal não armazena material sem autorização de uso. Referências externas (YouTube etc.) saem impressas como QR Code apontando para uma URL interna estável (`/r/<token>/`), então trocar o destino não exige reimpressão. A impressão A4 cobre o louvor individual, a coletânea filtrada, só letras, letras com cifras e o índice.
- **Escala do louvor e playlists:** o líder de louvor monta a escala mensal (dirigente, vocal, instrumento, sonoplastia e projeção). A playlist semanal (culto ou ensaio) escolhe louvores publicados com ordem, tom, versão e observações. Escala e playlist exportam `.ics` e PDF; o compartilhamento via WhatsApp aponta para a URL privada, que continua exigindo login.

## Stack

Monólito modular em **Django + Wagtail + PostgreSQL**, executado com **Docker Compose**. Em produção, **Gunicorn** atrás do **Caddy** (HTTPS automático), com infraestrutura na AWS descrita em Terraform.

| Camada | Tecnologia |
|---|---|
| Aplicação | Python 3.12, Django, Wagtail |
| Banco de dados | PostgreSQL 16 |
| Servidor | Gunicorn, WhiteNoise, Caddy |
| Autenticação | Perfis por grupo, 2FA (TOTP) para administradores |
| Backups | S3 privado (`django-storages`, `boto3`) |
| Infra e deploy | Docker Compose, Terraform, GitHub Actions, AWS SSM |

## Primeiros passos

**Pré-requisito:** Docker e Docker Compose.

```bash
cp .env.example .env
docker compose up --build
```

Acessos locais:

| O quê | URL |
|---|---|
| Site público | http://localhost:8000/ |
| Admin Wagtail | http://localhost:8000/admin/ |
| Entrar | http://localhost:8000/conta/entrar/ |
| Recuperar senha | http://localhost:8000/conta/recuperar-senha/ |
| Área da conta | http://localhost:8000/conta/ |
| 2FA (administradores) | http://localhost:8000/conta/2fa/ |
| Área privada | http://localhost:8000/area-privada/ |

Páginas de gestão (perfis autorizados):

- Inscritos em eventos: `/conta/eventos/inscritos/`
- Pedidos de oração (pastor/comunicação): `/conta/pedidos-de-oracao/`
- Contatos "Quero conhecer" (pastor/comunicação): `/conta/quero-conhecer/`
- Lista de membros (somente administradores): `/conta/usuarios/`

Credenciais iniciais, definidas em `.env`: usuário `admin`, senha `admin`. **Altere a senha após o primeiro acesso.**

Para parar o ambiente:

```bash
docker compose down
```

O PostgreSQL usa o volume Docker `postgres_data`: reiniciar ou recriar o container `web` **não** apaga os dados. Para zerar o banco local:

```bash
docker compose down -v
```

### Atalho no Windows com LocalStack

O Compose local do Django não fala com a AWS. Para emular o **S3 de backups** no computador:

```bat
scripts\deploy-local.bat
```

Sobe o `docker-compose.yml` com o LocalStack (`localhost:4566`), cria `s3://ib-conecta-backups` e deixa o portal em http://localhost:8000/. O Terraform de produção continua apontando para `us-east-2` de verdade.

Backup local (identidade em `.scratch/ib-conecta-backup.age.key`):

```bat
scripts\backup-local.bat
```

Restauração passo a passo: [`docs/backup.md`](docs/backup.md).

## Dados de demonstração

O ambiente Docker pode popular notícias, agenda, sermões e a área privada com conteúdo fictício, para revisar o visual com páginas preenchidas. Isso **não** é o conteúdo da igreja.

```bash
docker compose exec web python manage.py seed_demo
```

Com `DJANGO_SEED_DEMO=true` (padrão no Compose local), o seed também roda ao subir o ambiente, sem sobrescrever WhatsApp/PIX já configurados.

Contas de preview (senha `demo-ibconecta`): `membro`, `lider`, `comunicacao`, `pastor`, `tesouraria`, `comissao`, `joao`, `maria`, `carla`.

> [!WARNING]
> PIX e WhatsApp do seed são fictícios — não envie dinheiro nem mensagens.

## Testes

```bash
docker compose run --rm --no-deps --entrypoint python --env DJANGO_SETTINGS_MODULE=config.settings.test web manage.py test
```

## Contas, perfis e privacidade

Perfis suportados: membro, líder de ministério, comunicação, pastor, tesouraria, comissão de eventos e administrador. Perfis com permissão de conteúdo (comunicação, pastor, administrador) entram no grupo **Editores de conteúdo** e acessam o admin.

- Visitantes não autenticados são redirecionados ao login na área privada.
- Ações sensíveis geram trilha de auditoria, sem gravar senhas nem conteúdo pastoral.
- Política de privacidade, consentimento, menores e retenção: [`docs/privacidade.md`](docs/privacidade.md) (página pública `/privacidade/`).

## Produção

O stack de produção sobe **web (Gunicorn) + PostgreSQL + Caddy**. Não usa `runserver` nem bind-mount do código. O Caddy escuta 80/443, redireciona HTTP → HTTPS e faz proxy para a aplicação.

```bash
cp .env.prod.example .env.prod
# Preencha DJANGO_SECRET_KEY (32+ caracteres), senhas e o domínio
docker compose -f docker-compose.prod.yml --env-file .env.prod up --build
```

Na VM AWS (`t4g.small`, ARM, Ohio), use o mesmo par de comandos com `SITE_ADDRESS` público, `WEB_CONCURRENCY=1` e `CADDY_TLS` vazio (Let's Encrypt). Suba em background com `-d`.

**Deploy:** push em `master` dispara o deploy (GitHub Actions → SSM → o Compose acima). Passos únicos (IAM/OIDC + agente SSM na VM) e o fallback via SSH: [`docs/ops/deploy.md`](docs/ops/deploy.md). Sem esse bootstrap, merge em `master` **não** atualiza o site.

O entrypoint roda `migrate`, `collectstatic`, o bootstrap do CMS, o descarte de dados sensíveis de retiro vencidos e cria o superusuário se `DJANGO_SUPERUSER_*` estiver definido.

- **Saúde:** `https://<domínio>/healthz/` retorna `{"status":"ok"}` (o Compose usa essa rota no healthcheck do `web`).
- **Mídia pública:** volume Docker `media_data`, servida pelo Caddy em `/media/`.
- **Arquivos privados** (documentos, partituras): volume `private_media_data`, nunca em S3.
- **Backups:** bucket S3 privado da stack Terraform; procedimento em [`docs/backup.md`](docs/backup.md). A mídia não vai para o S3 em operação normal.
- **Infra da VM:** [`infra/aws/README.md`](infra/aws/README.md).
- **Monitoramento:** [`docs/ops/uptime.md`](docs/ops/uptime.md). **Go-live:** [`docs/ops/go-live.md`](docs/ops/go-live.md).

### DNS (Registro.br)

Domínio canônico: `https://www.ibsantaleopoldina.com.br`.

No painel do Registro.br use **Configurar zona DNS** (modo avançado) e não altere os servidores DNS — o domínio permanece nos nameservers do Registro.br. Crie dois registros **A** para o Elastic IP (`terraform output instance_public_ip` em `infra/aws`):

| Nome | Dados |
|---|---|
| `ibsantaleopoldina.com.br` | IPv4 do Elastic IP |
| `www.ibsantaleopoldina.com.br` | o mesmo IPv4 |

O Caddyfile redireciona o apex para `https://www.ibsantaleopoldina.com.br` (301). O Let's Encrypt exige `SITE_ADDRESS=www.ibsantaleopoldina.com.br` e `CADDY_TLS` vazio no `.env.prod`. Para trocar o IP, atualize os dois registros A, aguarde o DNS e recrie o Caddy se o certificado falhar.

## Estrutura do repositório

```
apps/
  public/        # Conteúdo público (CMS, agenda, sermões, oração, contato)
  accounts/      # Autenticação, perfis, 2FA e auditoria
  private_area/  # Área privada: documentos, escalas, eventos, retiros, louvores
config/          # Projeto Django (settings, urls)
templates/       # Templates
static/          # Arquivos estáticos
docs/            # Documentação (operação, privacidade, treinamento, ADRs)
infra/aws/       # Terraform da infraestrutura AWS
scripts/         # Scripts de apoio (deploy local, backup, monitoramento)
.github/         # Workflows de deploy e monitoramento
```

## Documentação

| Documento | Conteúdo |
|---|---|
| [`docs/treinamento-administracao.md`](docs/treinamento-administracao.md) | Roteiro de treinamento da administração: login, notícias, páginas institucionais, agenda, sermões, ao vivo, publicar/revisar/despublicar |
| [`docs/privacidade.md`](docs/privacidade.md) | Privacidade, consentimento, menores e retenção |
| [`docs/ops/deploy.md`](docs/ops/deploy.md) | Deploy automático e fallback via SSH |
| [`docs/ops/go-live.md`](docs/ops/go-live.md) | Checklist de entrada em produção |
| [`docs/ops/uptime.md`](docs/ops/uptime.md) | Monitoramento externo |
| [`docs/ops/instagram-acervo.md`](docs/ops/instagram-acervo.md) | Fotografias da homepage via Instagram |
| [`docs/backup.md`](docs/backup.md) | Backup e restauração |
| [`docs/acessibilidade-desempenho.md`](docs/acessibilidade-desempenho.md) | Acessibilidade e desempenho |
| [`PRODUCT.md`](PRODUCT.md) · [`DESIGN.md`](DESIGN.md) | Produto e design |

## Licença

O código é distribuído sob a licença [MIT](LICENSE). Conteúdos e mídias da igreja permanecem com seus respectivos direitos.
