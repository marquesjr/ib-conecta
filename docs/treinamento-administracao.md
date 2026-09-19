# Roteiro de treinamento da administração

Como a **comunicação**, o **pastor** e a **administração** publicam o portal **IB Conecta** da Igreja Batista em Santa Leopoldina **sem chamar suporte técnico a cada comunicado**.

Issue [#39](https://github.com/marquesjr/ib-conecta/issues/39). Parte do épico [#17](https://github.com/marquesjr/ib-conecta/issues/17).

Este texto descreve as telas reais do painel Wagtail em português (`pt-BR`): os nomes dos botões e menus abaixo são os que aparecem no sistema.

## Para quem é

| Perfil na conta | Entra no painel de publicação? | Papel neste roteiro |
|---|---|---|
| Comunicação | Sim | Publica o dia a dia |
| Pastor | Sim | Revisa conteúdo pastoral e autoriza o que for delicado |
| Administrador | Sim (com 2FA na área da conta) | Libera acesso, senha e problemas técnicos |
| Tesouraria, comissão de eventos, líder de ministério, membro | Não | Não usam este painel |

O grupo interno chama-se **Editores de conteúdo**. Quem não está nele vê a tela de login do painel mesmo depois de entrar na conta.

## Dois endereços de entrada

São sistemas diferentes. Use o certo.

| Onde | Produção | Local (treino) | Para quê |
|---|---|---|---|
| Painel de publicação (Wagtail) | https://www.ibsantaleopoldina.com.br/admin/ | http://localhost:8000/admin/ | Notícias, páginas institucionais, agenda, sermões, ao vivo, configurações da igreja |
| Área da conta | https://www.ibsantaleopoldina.com.br/conta/entrar/ | http://localhost:8000/conta/entrar/ | Área privada, inscritos, pedidos de oração, Quero conhecer |

Na **Minha conta**, quem publica vê o atalho **Publicar conteúdo (CMS)**. Ele abre o painel.

Não compartilhe a senha. Não publique conteúdo pastoral (pedido de oração, dado de retiro, escala interna) nas páginas públicas.

## Entrar no CMS

1. Abra o endereço **Painel de publicação** da tabela acima.
2. Informe **nome de usuário** e **senha** da igreja (não é e-mail, salvo se a administração cadastrou assim).
3. Clique em **Entrar**.
4. Você deve ver o menu lateral com **Páginas**, **Imagens**, **Documentos** e **Configurações**.

Se a tela voltar para o login: o perfil não é comunicação/pastor/administrador — peça à administração para corrigir o papel em `/conta/usuarios/`.

Administrador que entra pela **área da conta** (`/conta/entrar/`) pode precisar do código **2FA**. O treino do dia a dia da comunicação usa o `/admin/` com a conta `comunicacao`.

**Sair:** no canto da conta do painel, abra o menu do seu nome e escolha sair. Na área da conta, o botão é **Sair**.

## Mapa das páginas

No menu **Páginas**, abra a árvore do site. Não apague nem duplique os índices.

```
IB Conecta (raiz)
├── Nossa história          →  /historia/
├── Crenças                 →  /crencas/
├── Ministérios             →  /ministerios/
├── Liderança               →  /lideranca/
├── Notícias                →  /noticias/
│   └── cada comunicado     →  /noticias/<endereco>/
├── Agenda                  →  /agenda/
│   └── cada culto/evento   →  /agenda/<endereco>/
├── Sermões                 →  /sermoes/
│   └── cada sermão         →  /sermoes/<endereco>/
└── Ao vivo                 →  /ao-vivo/
```

A **Privacidade** (`/privacidade/`) não está nesta árvore: o texto é do código, aparece no rodapé, e **não** deve nascer como página do CMS (não crie um slug `privacidade`).

Regra de ouro: **notícia só nasce debaixo de Notícias**; **evento só debaixo de Agenda**; **sermão só debaixo de Sermões**. A página **Ao vivo** já existe — edite-a; não crie outra.

## Publicar, revisar e despublicar

Este ciclo vale para notícia, página institucional, evento, sermão e ao vivo.

### Salvar rascunho

1. Preencha os campos (veja as seções seguintes).
2. Clique em **Salvar rascunho** (não em **Publicar**).
3. Confira no site público: a página **não** deve aparecer. Rascunho não é vitrine.

### Revisar

1. No editor, use **Pré-visualizar** para ver o texto como o visitante verá.
2. Confira título, resumo, data, endereço da página (slug) e se o tom está pastoral — acolhedor, sem espetáculo e sem prometer plantão 24 horas.
3. Se a página **já estava publicada**, um rascunho novo **não substitui** o que o visitante vê até você clicar em **Publicar** de novo. Isso é proposital: dá tempo de corrigir sem furar a vitrine.

### Publicar

1. Clique em **Publicar**. No explorador, o estado da página passa de **Rascunho** para **Online**.
2. Abra a URL pública (veja o mapa) **em outra aba**, de preferência no celular.
3. Confira título, texto, data e, se houver, o vídeo do YouTube (não deve começar sozinho).

### Despublicar

Use quando o comunicado passou, a transmissão encerrou ou o texto saiu errado e não deve ficar no ar.

1. Abra a página no painel (**Páginas** → a página).
2. No menu de ações da página (não no lixo), escolha **Despublicar**.
3. Confirme.
4. A URL pública deve responder como página inexistente. O texto permanece no painel para republicar depois.

Não use **Excluir** no dia a dia. Despublicar basta e guarda o histórico.

## Notícias

1. **Páginas** → **Notícias**.
2. **Adicionar subpágina** → tipo **Notícia**.
3. Preencha:
   - **Título** — o que o visitante lê na lista e no celular.
   - **Resumo** — uma frase abaixo do título.
   - **Conteúdo** — o texto. Se inserir fotografia pelo editor, preencha o **texto alternativo**. Não há campo de capa nesta página.
4. **Slug** (aba **Promover**): só letras minúsculas, hífen, sem acento. Ex.: `culto-de-acao-de-gracas`. Não mude depois de divulgar o link.
5. Visibilidade (menu **Particular**): **Público** para comunicado da igreja. Não marque **Privativo** nem senha.
6. Siga o ciclo rascunho → revisar → **Publicar**.

A data da notícia no site é a da **primeira publicação**. Não invente data no título se ela não for verdadeira.

## Páginas institucionais

Já existem quatro: **Nossa história**, **Crenças**, **Ministérios**, **Liderança**.

1. **Páginas** → abra a página (não crie outra com o mesmo assunto).
2. Edite **Título**, **Resumo** e **Conteúdo**.
3. Salve rascunho, pré-visualize, publique.

O texto-semente do sistema **não** é a voz final da igreja. Substitua-o. Em dúvida teológica, o **pastor** revisa antes de publicar.

Não altere o slug (`historia`, `crencas`, `ministerios`, `lideranca`): o menu e os links da congregação dependem deles.

## Privacidade

A política pública (`/privacidade/`) não se edita neste painel. Pedido de oração, Quero conhecer e retiro já pedem consentimento e apontam para ela. Não publique pedido de oração, dado médico ou nome/foto de menor na vitrine. Prazos e o comando de descarte de retiro: `docs/privacidade.md`.

## Agenda e eventos

1. **Páginas** → **Agenda** → **Adicionar subpágina** → tipo **Evento**.
2. Preencha:
   - **Título**, **Início** (obrigatório), **Término** (se souber), **Local**, **Descrição**.
   - Relógio no fuso **America/Sao_Paulo** (Brasília).
3. Só marque **Exige inscrição** se a igreja for receber nomes pelo site. A lista de inscritos fica em **Minha conta** → **Gerenciar inscritos em eventos**, não neste painel.
4. Só marque **É retiro** depois de combinar com o pastor e a comissão de eventos. Retiro pede dados de família, saúde e menores — não é um culto comum.
5. **Vagas** e **Dias para descarte de dados sensíveis**: não altere sem o pastor/administração.
6. Slug estável. Visibilidade: **Público**.
7. Rascunho → revisar → **Publicar**.

A lista pública `/agenda/` mostra **somente eventos com início no futuro**. Evento com data passada some da lista (a URL antiga ainda abre se a página continuar publicada). Se o culto “não apareceu”, confira **Início** antes de chamar TI.

## Sermões

1. **Páginas** → **Sermões** → **Adicionar subpágina** → tipo **Sermão**.
2. **Título**, **Resumo**, **Conteúdo** (roteiro ou texto para leitura).
3. **URL da mídia incorporada**: cole o link do YouTube (ou de um áudio externo `.mp3`). O portal **não** recebe upload de vídeo.
4. Publique e confira: o player aparece sem autoplay.

Link que o painel entende: `youtube.com/watch?v=...`, `youtu.be/...`, `/live/...`. Se o player não aparecer, o endereço não foi reconhecido — corrija a URL; não anexe um arquivo de filme.

## Ao vivo

Existe **uma** página: **Ao vivo** (`/ao-vivo/`).

1. **Páginas** → **Ao vivo** → editar.
2. Cole a **URL do YouTube ao vivo** da transmissão daquela reunião.
3. **Publicar**.
4. Depois do culto, você pode **Despublicar**, limpar a URL e republicar (a página fica no ar sem player) ou deixar o último vídeo — combine o hábito com o pastor. O visitante não deve achar que há culto no ar quando não há.

Não crie uma segunda página “Ao vivo”. Não ligue autoplay (o portal recusa de propósito).

## Configurações que não são “página”

Em **Configurações** → **Configurações da igreja**:

- Home: título evangelístico, próximo culto, horários.
- Planeje sua visita: endereço, referências, mapa, acessibilidade, carona.
- WhatsApp institucional (só dígitos com DDI, ex. `5527...`).
- PIX (chave da **igreja**; combine com a tesouraria).
- Redes sociais.
- Acervo da home: arroba do Instagram, origem do acervo (API oficial ou só galeria curada) e quantos quadros mostrar.

Isso entra no ar ao **salvar** a configuração, sem o botão **Publicar** das páginas. Erro aqui aparece na home inteira. PIX e WhatsApp errados têm custo pastoral — revise em voz alta com outra pessoa.

O token da API do Instagram **não** se cola neste painel. Quem opera a VM cadastra com `set_instagram_token` ou importa o ZIP da Meta. Passo a passo: [`docs/ops/instagram-acervo.md`](ops/instagram-acervo.md).

## Quadros do acervo (fotografias da home)

A foto grande da abertura e a galeria **A vida em comunidade** vêm dos snippets **Quadros do acervo**, não da biblioteca **Imagens** (esta última serve ao editor das notícias).

1. No menu, abra **Quadros do acervo**.
2. Cada quadro tem fotografia, **texto alternativo**, **legenda**, **crédito** (ex.: `Instagram @igrejabatista.santaleopoldina`), data e se aparece no site.
3. Upload manual: **Adicionar quadro do acervo**, preencha a descrição da cena, publique o snippet (salvar basta; não é página).
4. Fotos sincronizadas da API ou importadas da exportação oficial já nascem com crédito e data. Revise e, se houver menor ou cena que não deve ir à vitrine, desmarque **Exibir no site**.

Conta da igreja no Instagram: `@igrejabatista.santaleopoldina`. Sem a API ou o ZIP da Meta, a home continua com imagens ilustrativas identificadas — não apresente essas imagens como fotografia da congregação.

## Checklist de publicação

Imprima ou copie. Marque **antes** de clicar em **Publicar**.

- [ ] **Título** claro no celular, sem MAIÚSCULAS inteiras, sem clickbait.
- [ ] **Resumo** verdadeiro; não promete o que o texto não entrega.
- [ ] Texto revisado (nomes, horários, tom acolhedor).
- [ ] **Imagem** (se houver no conteúdo): cena certa, **texto alternativo** preenchido. Notícia/sermão/evento **não** têm capa própria.
- [ ] **Data**: evento com **Início** futuro e horário de Brasília; notícia só publica quando o fato pode ser público; ao vivo com a URL **desta** reunião.
- [ ] **Perfil de visibilidade**: conteúdo da vitrine = **Público**. Nada de pedido de oração, dado médico, menor, escala ou documento interno.
- [ ] Slug estável; índices (`noticias`, `agenda`, `sermoes`, `ao-vivo`) intocados.
- [ ] YouTube/áudio só por URL; **sem** arquivo de vídeo no portal.
- [ ] Pré-visualizou no painel e conferiu a URL pública depois de publicar.

## Erros comuns

| O que acontece | Causa usual | O que fazer |
|---|---|---|
| “Publiquei e não aparece” | Clicou em **Salvar rascunho**, não em **Publicar** | Abrir a página e **Publicar**. Conferir a URL em aba anônima |
| Evento some da agenda | **Início** já passou, ou ficou no passado por fuso | Corrigir **Início** ou aceitar que a lista só mostra o futuro |
| Notícia 404 | Criou a página fora de **Notícias**, ou slug diferente do link divulgado | Criar debaixo do índice certo; não mudar slug depois do cartaz |
| Player do YouTube vazio | URL incompleta, Shorts/playlist sem id, ou arquivo enviado no lugar do link | Colar o link de *assistir* ou *ao vivo* |
| Visitante vê texto velho | Rascunho novo sem republicar | **Publicar** de novo |
| “Não entro no `/admin/`” | Perfil membro/líder/tesouraria/comissão | Administração corrige o papel |
| Site pede 2FA e a comunicação não tem | Entrou em `/conta/entrar/` com conta de administrador | Comunicação usa `/admin/` com a conta dela |
| Culto “no ar” fora de hora | URL de live antiga na página **Ao vivo** | Atualizar ou limpar a URL e publicar |
| Duas páginas “Ao vivo” ou dois índices de notícias | **Adicionar** na raiz em vez de editar | Não publique a duplicata; chame TI para remover |
| Foto “invisível” no celular leitor de tela | Imagem sem texto alternativo | Editar a imagem e preencher o texto alternativo |
| Foto de menor ou dado médico na vitrine | Publicou conteúdo que pertence à área da conta / retiro | **Despublicar** na hora; falar com o pastor. A política está em `/privacidade/` |

## Quem acionar

Não abra chamado técnico para dúvida de texto.

| Assunto | Quem | Como |
|---|---|---|
| Posso publicar isto? Tom pastoral, nomes, foto de menor, disciplina, teologia | **Pastor** | Conversa na igreja ou WhatsApp institucional |
| Texto, agenda da semana, live, sermão, notícia | **Comunicação** | Quem opera este roteiro |
| PIX, favorecido, comprovante | **Tesouraria** (pastor à vista) | Não altere PIX no painel sozinho |
| Retiro, vagas, inscrição familiar | **Comissão de eventos** + pastor | Marcar **É retiro** só depois do combinado |
| Senha, usuário sem acesso, papel errado, página duplicada, site fora do ar, erro vermelho no painel | **TI / administração do portal** | Quem observa o repositório e o alerta de queda (`docs/ops/uptime.md`) |
| Queda longa do site (> 15 min) | TI avisa **comunicação e pastor** | WhatsApp institucional — não invente comunicado no ar se o site estiver fora |

Em produção, o endereço canônico é `https://www.ibsantaleopoldina.com.br`. Se a home não abrir, não “consertam” pelo painel: siga o runbook de monitoramento.

## Treino completo (staging ou local)

Faça **um** ciclo de notícia de ponta a ponta, com outra pessoa conferindo o celular.

Ambiente local (Docker, conteúdo fictício — **não** é a igreja real):

```bash
cp .env.example .env
docker compose up --build
docker compose exec web python manage.py seed_demo
```

Conta de treino: usuário `comunicacao`, senha `demo-ibconecta`.

1. Entre em http://localhost:8000/admin/
2. Crie uma **Notícia** filha de **Notícias**, **Salvar rascunho**.
3. Abra a URL pública: deve falhar (não existe para o visitante).
4. **Pré-visualizar**, conferir o checklist, **Publicar**.
5. Abrir `/noticias/...` no celular: título e texto visíveis.
6. **Despublicar** e conferir que a URL pública some de novo.

Repita o hábito em **Agenda** (data futura) e na página **Ao vivo** (colar e limpar URL) quando for o treinamento da equipe.

Produção só recebe conteúdo **real** da igreja, já revisado. Não treine com “teste teste” no ar.
