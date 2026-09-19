# Acervo fotográfico do Instagram

A homepage do IB Conecta abre com uma fotografia e a seção **A vida em comunidade** mostra as demais. Isso não é a biblioteca **Imagens** das notícias: são os snippets **Quadros do acervo**. Ordem de preferência (já no código):

1. Fotos sincronizadas pela **API oficial** do Instagram.
2. Fotos curadas no CMS (upload manual no snippet).
3. Imagens ilustrativas do repositório, identificadas como exemplo.

Conta da igreja: [@igrejabatista.santaleopoldina](https://www.instagram.com/igrejabatista.santaleopoldina/). Sem token da Meta nem a exportação oficial da conta, o portal **não** pode copiar o feed — a Graph API exige conta Profissional e login do dono; raspadores ofendem os termos da Meta.

Há dois caminhos legítimos. Prefira o **A** se a conta puder virar Criador/Empresa. Use o **B** se a conta continuar pessoal ou se quiser um lote único do arquivo antigo.

## No CMS, uma vez (os dois caminhos)

No painel (`/admin/`), **Configurações** → **Configurações da igreja**:

1. **Instagram** (redes sociais): `https://www.instagram.com/igrejabatista.santaleopoldina/`
2. **Arroba do Instagram**: `igrejabatista.santaleopoldina` (sem `@`)
3. **Origem do acervo**:
   - caminho A → `Login Empresarial do Instagram`
   - caminho B (só exportação) → pode ficar `Desligado`
4. **Quadros no acervo da home**: quantas fotos a homepage mostra (padrão 12)
5. Salvar

Não cole token nesta tela. O segredo fica fora do painel, no comando abaixo.

Revisão editorial: **Quadros do acervo** (a comunicação tem permissão neste snippet). Legenda, crédito, data, texto alternativo e “Exibir no site”. Foto de menor: desmarque a exibição e fale com o pastor. Ver `docs/privacidade.md`.

---

## Caminho A — API oficial (atualização contínua)

A Meta só libera a API para conta **Profissional** (Criador ou Empresa). Conta pessoal não tem Graph API desde o fim do Basic Display.

### 1. Conta Criador ou Empresa

No Instagram (app ou `instagram.com`), perfil da igreja → **Conta profissional** → **Criador** (basta; não precisa Página do Facebook).

### 2. Aplicativo no painel da Meta

1. Entre em [developers.facebook.com](https://developers.facebook.com/) com um usuário que administra o Instagram da igreja (José ou a comunicação).
2. **Criar aplicativo** → tipo **Negócios** → nome `IB Conecta`.
3. Adicione o produto **Instagram** → **API setup with Instagram login** (Login Empresarial / Business Login).
4. Permissão necessária: `instagram_business_basic` (ler mídia). Não peça publicar, comentários nem mensagens.
5. Em **Instagram** → **API setup with Instagram business login**, ao lado da conta `@igrejabatista.santaleopoldina`, clique em **Generate token**.
6. Entre com a conta da igreja e copie o token. No painel da Meta este token já é de **longa duração** (cerca de 60 dias).

Documentação: [Get started (Instagram Login)](https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login/get-started/) e [Business Login](https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login/business-login/).

Não commite o token. Não cole no GitHub. Não grave em `.env` permanente: o banco precisa poder **reescrever** o valor na renovação.

### 3. Cadastrar o token e sincronizar

**Local (Docker):**

```bash
docker compose exec -e INSTAGRAM_ACCESS_TOKEN='cole-o-token-aqui' web \
  python manage.py set_instagram_token
docker compose exec web python manage.py sync_instagram
```

**Produção** (depois do deploy deste código), na VM:

```bash
cd /home/ubuntu/ib-conecta
docker compose -f docker-compose.prod.yml --env-file .env.prod exec -T \
  -e INSTAGRAM_ACCESS_TOKEN='cole-o-token-aqui' web \
  python manage.py set_instagram_token
docker compose -f docker-compose.prod.yml --env-file .env.prod exec -T web \
  python manage.py sync_instagram
```

A home passa a servir os arquivos em `/media/archive/` (as URLs do CDN da Meta expiram). Crédito: `Instagram @igrejabatista.santaleopoldina`. Legenda e data vêm do post.

### 4. Renovar o token (a cada ~50 dias)

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod exec -T web \
  python manage.py refresh_instagram_token
docker compose -f docker-compose.prod.yml --env-file .env.prod exec -T web \
  python manage.py sync_instagram
```

Cron sugerido na VM (semana, fora do culto):

```cron
15 7 * * 1 cd /home/ubuntu/ib-conecta && docker compose -f docker-compose.prod.yml --env-file .env.prod exec -T web python manage.py refresh_instagram_token && docker compose -f docker-compose.prod.yml --env-file .env.prod exec -T web python manage.py sync_instagram
```

Se o token vencer, a home **não quebra**: volta a mostrar o acervo já gravado (e as ilustrativas só se ainda não houver fotos reais).

Conta Empresa já ligada a uma Página do Facebook: em **Origem do acervo** escolha `Login do Facebook`, preencha o **ID da conta do Instagram**, e defina `INSTAGRAM_APP_ID` / `INSTAGRAM_APP_SECRET` só no `.env.prod` da VM (renovação). O token continua no comando `set_instagram_token`, nunca no git.

---

## Caminho B — exportação oficial da Meta (lote, sem API)

Serve para conta pessoal, arquivo antigo, ou enquanto o aplicativo da Meta não está pronto. É o “Download Your Information” da própria Meta — não é raspagem.

### 1. Pedir o arquivo (José, na conta da igreja)

1. No Instagram: **Configurações e atividade** → **Contas centrais** (ou **Sua atividade**) → **Baixar suas informações**.
   Atalho atual da Meta: [accountscenter.facebook.com/info_and_permissions](https://accountscenter.facebook.com/info_and_permissions).
2. Escolha **Baixar ou transferir informações** → a conta **Instagram** `@igrejabatista.santaleopoldina`.
3. Formato **JSON** (não HTML). Intervalo: **Desde o início** (ou o período que a igreja quiser no site).
4. Mídia: inclua **publicações** (posts). Stories só se quiser o `--include-stories`.
5. Qualidade **alta**. Destino: e-mail do administrador.
6. Confirme. A Meta avisa por e-mail (minutos a alguns dias). Baixe o ZIP.

Não envie o ZIP para o GitHub nem para um chat público. Há dados pessoais além das fotos do feed.

### 2. Importar no portal

**Local**, com o ZIP no notebook:

```bash
docker compose cp ~/Downloads/instagram-*.zip web:/tmp/instagram-export.zip
docker compose exec web python manage.py import_instagram_export /tmp/instagram-export.zip \
  --handle igrejabatista.santaleopoldina
```

**Produção**, copie o ZIP para a VM (scp/SFTP) e:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod cp \
  /caminho/instagram-export.zip web:/tmp/instagram-export.zip
docker compose -f docker-compose.prod.yml --env-file .env.prod exec -T web \
  python manage.py import_instagram_export /tmp/instagram-export.zip \
  --handle igrejabatista.santaleopoldina
```

Confira antes de gravar:

```bash
python manage.py import_instagram_export /tmp/instagram-export.zip --dry-run
```

Vídeo é ignorado (a home é fotografia). O comando é idempotente: rodar de novo não duplica o mesmo arquivo.

### 3. Apagar o ZIP

Depois de conferir a homepage, apague o ZIP da VM, do `/tmp` do container e do notebook se não precisar mais. O portal já tem as fotos em `media/archive/` (volume Docker).

---

## O que este repositório não faz

- Não entra na conta do Instagram.
- Não usa serviços de raspagem (instaloader, cookies, `?__a=1`, etc.).
- Não publica sozinho em produção: depois do merge, o deploy atualiza o **código**; o **token** ou o **ZIP** continua um passo do administrador na VM.
- Não inventa fotografias da congregação. Sem A ou B, a home segue com as imagens ilustrativas identificadas.
