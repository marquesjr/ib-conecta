# IB Conecta

Portal de comunicação, evangelização e gestão da **Igreja Batista em Santa Leopoldina**.

- **Domínio canônico:** https://www.ibsantaleopoldina.com.br
- **Repositório:** https://github.com/marquesjr/ib-conecta
- **Licença do código:** MIT (conteúdos e mídias da igreja permanecem com seus respectivos direitos)

## Stack local

Monólito modular com **Django + Wagtail + PostgreSQL**, executado via **Docker Compose**.

```
apps/
  public/        # Conteúdo público
  accounts/      # Autenticação e perfis
  private_area/  # Área privada / membros
config/          # Projeto Django (settings, urls)
```

## Pré-requisitos

- Docker e Docker Compose

## Subir o ambiente

```bash
cp .env.example .env
docker compose up --build
```

Em seguida:

- Página pública: http://localhost:8000/
- Planeje sua visita: http://localhost:8000/planeje-sua-visita/
- Pedido de oração: http://localhost:8000/pedido-de-oracao/
- Quero conhecer a igreja: http://localhost:8000/quero-conhecer/
- Contribuições PIX: http://localhost:8000/contribuicoes/
- Notícias: http://localhost:8000/noticias/
- Agenda: http://localhost:8000/agenda/
- Sermões: http://localhost:8000/sermoes/
- Ao vivo: http://localhost:8000/ao-vivo/
- Inscritos (perfis autorizados): http://localhost:8000/conta/eventos/inscritos/
- Pedidos de oração (pastor/comunicação): http://localhost:8000/conta/pedidos-de-oracao/
- Contatos Quero conhecer (pastor/comunicação): http://localhost:8000/conta/quero-conhecer/
- Área privada (membros autenticados): http://localhost:8000/area-privada/
- Biblioteca de documentos: http://localhost:8000/area-privada/documentos/
- Ministérios e escalas: http://localhost:8000/area-privada/ministerios/
- Comissão de eventos: http://localhost:8000/area-privada/eventos/
- Retiro (check-in da equipe, quando o evento é retiro): http://localhost:8000/area-privada/eventos/<id>/retiro/
- Coletânea de louvores: http://localhost:8000/area-privada/louvores/
- Playlists semanais do louvor: http://localhost:8000/area-privada/playlists/
- Admin Wagtail: http://localhost:8000/admin/

No admin Wagtail, em **Configurações**, edite WhatsApp, PIX, redes sociais, horários, endereço e o próximo culto (sem hardcode no código). Páginas institucionais (história, crenças, ministérios, liderança), notícias, eventos da agenda, sermões e a página ao vivo são criadas/publicadas pelo CMS; rascunhos não ficam públicos até a publicação. Sermões e a transmissão usam URL externa (YouTube) incorporada sem autoplay — o portal não hospeda o vídeo. Perfis com permissão de conteúdo (Comunicação, Pastor, Administrador) entram no grupo **Editores de conteúdo** e acessam o admin. Comissão de eventos e comunicação gerenciam inscritos pela área da conta. Pastor e comunicação acompanham pedidos de oração e contatos de **Quero conhecer a igreja** na área da conta, sem expor o conteúdo no site público. A página de contribuições mostra a chave PIX configurada pela administração; o portal não processa cartão nem armazena dados bancários de terceiros.


Credenciais iniciais (definidas em `.env`):

- usuário: `admin`
- senha: `admin`

Altere a senha após o primeiro acesso.

## Dados de demonstração (local)

O ambiente Docker pode popular notícias, agenda, sermões e a área privada com conteúdo fictício, para revisar o visual com páginas preenchidas. Isso **não** é o conteúdo da igreja.

```bash
docker compose exec web python manage.py seed_demo
```

Com `DJANGO_SEED_DEMO=true` (padrão no Compose local), o seed também roda ao subir o ambiente, sem sobrescrever WhatsApp/PIX já configurados.

Contas de preview (senha `demo-ibconecta`): `membro`, `lider`, `comunicacao`, `pastor`, `tesouraria`, `comissao`, `joao`, `maria`, `carla`.

PIX e WhatsApp do seed são fictícios — não envie dinheiro nem mensagens.

## Persistência do banco

O PostgreSQL usa o volume Docker `postgres_data`. Reiniciar ou recriar o container `web` **não** apaga os dados. Para zerar o banco local:

```bash
docker compose down -v
```

## Testes

```bash
docker compose run --rm --no-deps --entrypoint python --env DJANGO_SETTINGS_MODULE=config.settings.test web manage.py test
```

## Conta e autenticação

- Entrar: http://localhost:8000/conta/entrar/
- Recuperar senha: http://localhost:8000/conta/recuperar-senha/
- Área da conta: http://localhost:8000/conta/
- 2FA (administradores): http://localhost:8000/conta/2fa/

Perfis suportados: membro, líder de ministério, comunicação, pastor, tesouraria, comissão de eventos e administrador. Ações sensíveis geram trilha de auditoria sem gravar senhas ou conteúdo pastoral.

Membros autenticados entram na **área privada** e veem só os documentos liberados para o seu perfil (membros, comunicação/pastor, tesouraria ou administração). Visitantes não autenticados são redirecionados ao login. A lista completa de membros permanece restrita à gestão de perfis (`/conta/usuarios/`), acessível só a administradores. Arquivos privados ficam fora de `/media/` e só são baixados pela biblioteca autenticada. Comunicação, pastor e administrador enviam documentos em `/area-privada/documentos/novo/`.

Líderes de ministério e administradores cadastram ministérios e montam a **escala mensal** (participantes e funções). O convocado confirma ou recusa pelo celular; substituições ficam registradas. A escala exporta para calendário (`.ics`) e tem página de impressão para salvar PDF; o compartilhamento via WhatsApp aponta para a URL privada, que continua exigindo login.

A **comissão de eventos** opera o calendário anual sobre os eventos da agenda pública (sem duplicar inscrição): equipes, tarefas, checklists, fornecedores, materiais, orçamento com aprovação da tesouraria, comunicação com inscritos e relatório/atas privados. Membros só atualizam as tarefas e o checklist que lhes foram designados. Tesouraria vê e aprova o financeiro; relatório e documentos da operação ficam restritos à comissão e à administração.

**Retiros** são eventos da agenda pública com inscrição familiar: responsável legal, emergência, restrições alimentares/médicas, transporte/embarque, acomodação, lista de espera e status de pagamento PIX (sem dados bancários). A equipe do retiro faz check-in e lê a programação/documentos privados em `/area-privada/eventos/<id>/retiro/`. Dados médicos e de menores são descartados após o prazo configurado no evento (`python manage.py discard_retreat_sensitive_data`).

A **coletânea de louvores** fica na área privada. Líderes de ministério criam, revisam e publicam cânticos com letra, cifra, partitura PDF, tom, andamento, tags, versões e licenciamento; o portal não armazena material sem autorização de uso. Referências externas (YouTube etc.) saem impressas como QR Code apontando para uma URL interna estável (`/r/<token>/`); trocar o destino não exige reimpressão. A impressão A4 cobre o louvor individual, a coletânea filtrada, só letras, letras com cifras e o índice.

O líder de louvor monta a **escala mensal** com funções de dirigente, vocal, instrumento, sonoplastia e projeção; o convocado confirma ou recusa, e substituições ficam no histórico. A **playlist semanal** (culto ou ensaio) escolhe louvores publicados da coletânea com ordem, tom, versão e observações. Músicos autenticados consultam e imprimem o material; escala e playlist exportam calendário (`.ics`) e PDF, e o compartilhamento via WhatsApp aponta para a URL privada, que continua exigindo login.

## Produção (Docker Compose + Caddy)

O stack de produção sobe **web (Gunicorn) + PostgreSQL + Caddy**. Não usa `runserver` nem bind-mount do código. Caddy escuta 80/443, redireciona HTTP → HTTPS e faz proxy para a aplicação.

```bash
cp .env.prod.example .env.prod
# Preencha DJANGO_SECRET_KEY (32+ caracteres), senhas e o domínio
docker compose -f docker-compose.prod.yml --env-file .env.prod up --build
```

Na VM AWS (`t4g.small`, ARM, Ohio), depois de `git pull`, o mesmo par de comandos — com `SITE_ADDRESS` público, `WEB_CONCURRENCY=1` e `CADDY_TLS` vazio (Let's Encrypt). Suba em background com `-d`.

O entrypoint já roda `migrate`, `collectstatic`, bootstrap do CMS e cria o superusuário se `DJANGO_SUPERUSER_*` estiver definido.

- Saúde da aplicação: `https://<domínio>/healthz/` (JSON `{"status":"ok"}`; o Compose também usa essa rota no healthcheck do `web`)
- Mídia pública: volume Docker `media_data`, servida pelo Caddy em `/media/`
- Arquivos privados (documentos, partituras): volume `private_media_data` (nunca em S3)
- Backups: bucket S3 privado da stack Terraform; procedimento em `docs/backup.md` (issue #33). Mídia não vai para o S3 em operação normal.

Na VM pública, deixe `CADDY_TLS` vazio no `.env` para o Let's Encrypt. Com `SITE_ADDRESS=localhost` o padrão é `tls internal`.

Infra da VM: `infra/aws/README.md`.

## DNS (Registro.br)

Domínio canônico: `https://www.ibsantaleopoldina.com.br`.

No painel do Registro.br use **Configurar zona DNS** (modo avançado). Não altere os servidores DNS — o domínio permanece nos nameservers do Registro.br.

Dois registros **A** para o Elastic IP (`terraform output instance_public_ip` em `infra/aws`):

| Nome | Dados |
|---|---|
| `ibsantaleopoldina.com.br` | IPv4 do Elastic IP |
| `www.ibsantaleopoldina.com.br` | o mesmo IPv4 |

O Caddyfile redireciona o apex para `https://www.ibsantaleopoldina.com.br` (301). Let's Encrypt exige `SITE_ADDRESS=www.ibsantaleopoldina.com.br` e `CADDY_TLS` vazio no `.env.prod`.

Para trocar o IP: atualize os dois A, espere o DNS e recrie o Caddy se o certificado falhar.

## Local (atalho Windows + LocalStack)

O Compose local do Django não fala com a AWS. Para emular o **S3 de backups** no notebook:

```bat
scripts\deploy-local.bat
```

Sobe `docker-compose.yml` + LocalStack (`localhost:4566`), cria `s3://ib-conecta-backups` e deixa o portal em http://localhost:8000/. Terraform de produção continua apontando para `us-east-2` de verdade.

Backup local (identidade em `.scratch/ib-conecta-backup.age.key`):

```bat
scripts\backup-local.bat
```

Restauração passo a passo: `docs/backup.md`.

## Parar

```bash
docker compose down
```
