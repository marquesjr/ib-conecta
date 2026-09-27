---
name: "IB Conecta — Editorial acolhedor"
description: "Convite pastoral com serifada editorial, fotografia ampla e superfícies claras."
colors:
  ink-red: "#862d36"
  ink-red-hover: "#69222b"
  paper: "#faf9f6"
  paper-warm: "#f3f0eb"
  paper-shade: "#ded9d2"
  mount: "#ffffff"
  graphite: "#262722"
  archive-gray: "#62635d"
typography:
  display:
    fontFamily: "DM Serif Display, Georgia, serif"
    fontSize: "clamp(2.5rem, 4.5vw, 4.5rem)"
    fontWeight: 400
    lineHeight: 1.12
    letterSpacing: "-.025em"
  headline:
    fontFamily: "DM Serif Display, Georgia, serif"
    fontSize: "clamp(1.8rem, 2.8vw, 2.8rem)"
    fontWeight: 400
    lineHeight: 1.12
    letterSpacing: "-.025em"
  title:
    fontFamily: "Archivo, Segoe UI, sans-serif"
    fontSize: "1.1rem"
    fontWeight: 600
    lineHeight: 1.12
  body:
    fontFamily: "Archivo, Segoe UI, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "Archivo, Segoe UI, sans-serif"
    fontSize: ".95rem"
    fontWeight: 600
    letterSpacing: "0"
rounded:
  badge: "5px"
  control: "8px"
  action: "10px"
  media: "12px"
  panel: "14px"
spacing:
  xs: ".25rem"
  sm: ".5rem"
  md: "1rem"
  lg: "1.5rem"
  gutter: "1.25rem"
  page-gutter: "clamp(1.25rem, 5vw, 6rem)"
components:
  button-primary:
    backgroundColor: "{colors.ink-red}"
    textColor: "{colors.mount}"
    rounded: "{rounded.action}"
    padding: ".8rem 1.35rem"
  button-primary-hover:
    backgroundColor: "{colors.ink-red-hover}"
    textColor: "{colors.mount}"
  button-secondary:
    backgroundColor: "transparent"
    textColor: "{colors.ink-red}"
    rounded: "{rounded.action}"
    padding: ".8rem 1.35rem"
  button-light:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink-red}"
    rounded: "{rounded.action}"
    padding: ".8rem 1.35rem"
  field:
    backgroundColor: "{colors.mount}"
    textColor: "{colors.graphite}"
    rounded: "{rounded.control}"
    padding: ".6rem .7rem"
  panel:
    backgroundColor: "{colors.mount}"
    textColor: "{colors.graphite}"
    rounded: "{rounded.panel}"
    padding: "clamp(1.25rem, 3vw, 2rem)"
  state:
    rounded: "{rounded.badge}"
    padding: ".16em .5em .16em .42em"
---

# Design System: IB Conecta

## Overview

**Creative North Star: "Encontro — editorial acolhedor"**

A identidade aprovada em 16/09/2026 recebe o visitante com fotografia ampla, títulos serifados e ritmo de leitura generoso. Vinho, branco morno e tinta escura aproximam a instituição de quem procura culto, caminho ou conversa. A logo da Igreja Batista em Santa Leopoldina permanece como identidade. Desde 27/09/2026 o site usa a versão em alta resolução fornecida pelo usuário, apenas aparada nas margens brancas e reduzida para a web, sem redesenho.

Este registro descreve o sistema implementado em `static/css/ib-conecta.css`, `templates/base.html`, `templates/public/home.html` e `static/js/navigation.js`. Substitui deliberadamente Arquivo da Congregação, conforme a escolha do usuário; a composição da homepage está em `.impeccable/surfaces/templates-public-home-html.md`. As ferramentas privadas compartilham paleta e controles legíveis, com densidade adequada à operação.

**Key Characteristics:**

- DM Serif Display normal e itálico nos momentos editoriais; Archivo na leitura e operação.
- Superfícies claras, divisórias finas, cantos suaves e ausência de sombras.
- Fotografias grandes, legendas discretas e procedência explícita.
- Ações vinho, foco visível e navegação acessível também sem JavaScript.

## Colors

O vinho aquece uma base clara com texto escuro e cinza de leitura secundária.

### Primary

- **Vinho** (`ink-red`): ações, links, datas, foco, erros e faixa de informações para a visita.
- **Vinho profundo** (`ink-red-hover`): resposta de hover das ações e links.

### Neutral

- **Branco morno** (`paper`): fundo contínuo e botão claro sobre vinho.
- **Papel quente** (`paper-warm`): convite, tabelas, hover e campos desabilitados.
- **Fio de papel** (`paper-shade`): divisórias e bordas discretas.
- **Branco** (`mount`): painéis, campos e texto sobre vinho.
- **Tinta escura** (`graphite`): texto principal e navegação.
- **Cinza de leitura** (`archive-gray`): notas, legendas e informação secundária.

**The Vinho com Função Rule.** O vinho identifica ação ou informação relevante; também sustenta uma faixa de seção com texto claro. A antiga proibição de fundos vinho não pertence a este mundo.

## Typography

**Display Font:** DM Serif Display, com Georgia e serif de fallback. Arquivos locais normal e itálico no peso 400.

**Body Font:** Archivo variável local, com Segoe UI e sans-serif de fallback. Monoespaçada aparece apenas em dados técnicos como a chave PIX.

### Hierarchy

- **Display:** títulos de página fluidos, regulares e ligeiramente fechados, conforme os tokens.
- **Headline:** títulos de seção serifados; painéis usam uma versão mais contida.
- **Title:** subtítulos operacionais em Archivo semibold.
- **Body:** Archivo com entrelinha confortável; prosa limitada a `min(68ch, 100%)`.
- **Label:** rótulos de formulário semibold em caixa natural. Datas e marcas de estado usam algarismos tabulares localmente.

**The Duas Vozes Rule.** A serifada conduz convite e leitura editorial; Archivo sustenta controles, metadados, tabelas e instruções.

**The Texto Preservado Rule.** Ênfase tipográfica não reescreve conteúdo do CMS. A abertura destaca as três palavras finais da headline personalizada em itálico vinho; esse tratamento é local à homepage, não uma obrigação para todo título.

## Layout

Colunas centradas e margens fluidas substituem a antiga folha de contato. Conteúdo interno tem largura máxima de 76rem; cabeçalho e abertura chegam a 96rem, e conteúdo da home a 90rem. Prosa permanece mais estreita que sua superfície. Listas editoriais usam divisórias e data empilhada: dia em serifada vinho, dia da semana e mês em Archivo; título com linha secundária de horário e local (eventos) ou resumo (sermões). A faixa vinho da home responde quando, onde e primeira vez, cada uma com sua ação (horários, mapa, WhatsApp). Painéis operacionais usam colunas adaptáveis com mínimo de 22rem, limitado à largura disponível.

O ritmo combina pequenos intervalos de controle com respiro entre seções. Margens laterais seguem `page-gutter`. Em 1100px, navegação e abertura se compactam; em 900px, a abertura empilha e o menu pode recolher. Em 600px, pares editoriais, faixa de visita e rodapé passam para uma coluna; ações da abertura ocupam a largura disponível. Registros datados empilham em 34rem. Tabelas podem rolar horizontalmente.

**The Medida de Leitura Rule.** Uma superfície larga não exige uma linha longa: preserve os limites de prosa e de campos, com inputs até 28rem e textareas até 44rem.

## Elevation & Depth

Não há sombras no sistema entregue. Fundo morno, painéis brancos, bordas finas e respiro produzem separação. Dropdowns usam posicionamento e borda para sobrepor conteúdo, sem simular altura.

**The Superfície Serena Rule.** Use contraste tonal e espaço para separar regiões; a resposta interativa muda cor e borda, sem deslocar ou elevar controles.

## Shapes

Cantos arredondados acompanham a escala dos elementos: selos compactos, campos, botões e painéis seguem os tokens. Fotografias usam recortes suaves; a abertura tem raio próprio de 18px, reduzido no celular. Essa exceção não cria uma nova escala global. Bordas de 1px mantêm a estrutura leve. Setas e menu são SVG inline.

## Components

### Buttons

Ações com altura mínima de 48px e Archivo medium. A primária é vinho com texto branco; a secundária tem fundo transparente e contorno vinho; a clara usa papel sobre vinho. Hover escurece a primária, aquece a secundária e clareia a variante clara. Transição de fundo em .18s com `ease-out`. Desabilitado reduz opacidade e indica indisponibilidade pelo cursor.

O foco geral usa contorno vinho de 2px afastado 5px; sobre a faixa vinho, o contorno é branco.

### Chips

Estados têm texto e marcas geométricas além da cor: quadrado vazio para pendente, cheio para confirmado e cortado para encerrado. Tags também distinguem confirmação, pendência e recusa por preenchimento e bordas contínuas, tracejadas ou duplas. O raio compacto suaviza as marcas sem eliminar suas diferenças.

### Cards / Containers

Painéis brancos com borda de papel, raio `panel` e padding fluido acolhem leitura e operação. Listas editoriais permanecem abertas, separadas por fios; não precisam virar cartões. Fotografias mantêm legendas externas, salvo a legenda sobreposta da abertura.

### Inputs / Fields

Campos brancos, borda cinza, raio `control` e altura mínima de 46px. Rótulos ficam acima, em caixa natural; foco muda a borda para vinho, além do contorno global. Erros combinam borda e texto vinho. Desabilitados usam papel quente e cinza. Textareas permitem redimensionamento vertical; checkboxes e radios preservam forma nativa com acento vinho.

### Navigation

Logo original e navegação horizontal discreta, com links em caixa natural. Página atual recebe vinho e sublinhado; grupos usam `details`/`summary` com chevron SVG no lugar do marcador nativo. A logo aparece inteira (com o lema), com 72px de altura (58px no celular), e usa `mix-blend-mode: multiply` para o fundo branco não virar caixa sobre o fundo morno. No celular, Menu expõe `aria-expanded` e `aria-controls`; Escape fecha o grupo ou menu e devolve foco ao controle. Clique fora fecha; sem JavaScript os links continuam visíveis. O dropdown torna-se parte do fluxo em telas pequenas.

### Ícone do navegador

Derivado do peixe da logo, vetorizado sem redesenho: peixe branco sobre o vermelho da logo (`#d21019`, exceção à paleta por ser cor da marca). O traço fino da logo recebe reforço proporcional ao tamanho, maior no `favicon.ico` de 16 px. Arquivos em `static/img/icons/` (procedência em `source.txt`); manifesto em `static/site.webmanifest`; `/favicon.ico` redireciona para o arquivo estático.

### Fotografia editorial

O acervo separa **fotografia** de **arte ou cartaz** (campo Tipo do Quadro do acervo). Fotografia usa `object-fit: cover`, cantos suaves e legendas em Archivo; arte nunca é recortada.

- **Abertura:** sempre uma fotografia (a marcada como destaque, senão a mais recente), em retrato 4:5 com no máximo 32rem de largura — perto da resolução dos arquivos do Instagram (640px) — e legenda fora da imagem. No celular a foto vem antes do título, em 4:3.
- **Mural da igreja:** artes inteiras, quadradas, `object-fit: contain` sobre branco com borda, em slide: páginas de quatro cartazes (três até 900px; no celular um por vez, com o próximo aparecendo na borda). Setas no título avançam uma página e ficam desativadas nas pontas; um contador ("1–4 de 5") é anunciado a leitores de tela. Sem troca automática. A barra de rolagem some só com o slide ativo (`static/js/mural.js`); sem JavaScript, as setas ficam ocultas e a faixa continua deslizável. O link do perfil fica no título da seção.
- **A vida em comunidade:** mosaico de até quatro fotografias, a primeira maior; legenda curta sobreposta em etiqueta clara. Com menos de quatro, um convite para enviar fotos fecha a grade sem buracos.
- **Crédito:** o crédito padrão do Instagram não se repete sob cada quadro; crédito de fotógrafo aparece.

A foto inicial tem prioridade de carregamento; mural e mosaico usam lazy loading. A revelação inicial por recorte dura .65s com `cubic-bezier(.16,1,.3,1)`. Reduced motion desativa animação, rolagem suave e transição dos botões.

Fotos reais publicadas ou sincronizadas têm prioridade. Imagens ilustrativas só aparecem quando não há nenhuma fotografia real e nunca se misturam a ela; mantêm legendas e aviso explícito e não constituem evidência documental da congregação.

## Do's and Don'ts

### Do:

- **Do** preservar a logo original e a dupla tipográfica local.
- **Do** manter texto editável e fatos institucionais vindos do CMS.
- **Do** usar serifada para hierarquia editorial e Archivo para operação.
- **Do** manter estados legíveis por texto e forma, inclusive na impressão.
- **Do** conservar foco visível, reduced motion e navegação sem JavaScript.
- **Do** identificar imagens ilustrativas até sua substituição por acervo real.

### Don't:

- **Don't** restaurar grade de arquivo, textura, cantoneiras ou letra manuscrita como regras atuais.
- **Don't** adicionar sombras deslocadas, glifos como ícones ou rótulos decorativos acima dos títulos.
- **Don't** transformar o layout específico da home em obrigação das páginas operacionais.
- **Don't** apresentar dados de demonstração ou fotos ilustrativas como fatos reais da igreja.
- **Don't** recortar arte ou cartaz, nem abrir a home com um.
- **Don't** iniciar vídeos automaticamente.

Não canonizado: imagens ilustrativas são conteúdo provisório; o aviso de demonstração é uma salvaguarda de preview condicionada a DEBUG e EDITORIAL_DEMO_PREVIEW. Nenhum dos dois define a identidade permanente.
