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
- Notícias: http://localhost:8000/noticias/
- Admin Wagtail: http://localhost:8000/admin/

No admin Wagtail, em **Configurações**, edite WhatsApp, horários, endereço e o próximo culto (sem hardcode no código). Páginas institucionais (história, crenças, ministérios, liderança) e notícias são criadas/publicadas pelo CMS; rascunhos não ficam públicos até a publicação. Perfis com permissão de conteúdo (Comunicação, Pastor, Administrador) entram no grupo **Editores de conteúdo** e acessam o admin.


Credenciais iniciais (definidas em `.env`):

- usuário: `admin`
- senha: `admin`

Altere a senha após o primeiro acesso.

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

## Parar

```bash
docker compose down
```
