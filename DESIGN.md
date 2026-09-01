---
name: IB Conecta
description: O acervo fotográfico da congregação, montado como folha de contato em papel de arquivo — canto reto, sem sombra, um único vermelho de sinal.
colors:
  paper: "#ece8e2"
  paper-shade: "#d4d0ca"
  paper-warm: "#f4f1ec"
  mount: "#f9f9f9"
  graphite: "#222527"
  graphite-hover: "#15181a"
  photo-black: "#111313"
  archive-gray: "#74706c"
  ink-red: "#8b211a"
  ink-red-hover: "#6f1a14"
typography:
  display:
    fontFamily: 'Archivo, "Segoe UI", system-ui, sans-serif'
    fontSize: "clamp(1.7rem, 3.6vw, 3.4rem)"
    fontWeight: 600
    lineHeight: 1.05
    letterSpacing: "-0.015em"
    fontFeature: "tabular-nums"
  headline:
    fontFamily: 'Archivo, "Segoe UI", system-ui, sans-serif'
    fontSize: "clamp(1.5rem, 3.4vw, 2.05rem)"
    fontWeight: 600
    lineHeight: 1.15
    letterSpacing: "-0.01em"
  title:
    fontFamily: 'Archivo, "Segoe UI", system-ui, sans-serif'
    fontSize: "1.15rem"
    fontWeight: 600
    lineHeight: 1.15
    letterSpacing: "0"
  section-label:
    fontFamily: 'Archivo, "Segoe UI", system-ui, sans-serif'
    fontSize: "0.7rem"
    fontWeight: 600
    lineHeight: 1.15
    letterSpacing: "0.15em"
  lede:
    fontFamily: 'Archivo, "Segoe UI", system-ui, sans-serif'
    fontSize: "1.05rem"
    fontWeight: 400
    lineHeight: 1.55
  body:
    fontFamily: 'Archivo, "Segoe UI", system-ui, sans-serif'
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.55
    fontFeature: "tabular-nums"
  label:
    fontFamily: 'Archivo, "Segoe UI", system-ui, sans-serif'
    fontSize: "0.63rem"
    fontWeight: 600
    lineHeight: 1.55
    letterSpacing: "0.16em"
  nav:
    fontFamily: 'Archivo, "Segoe UI", system-ui, sans-serif'
    fontSize: "0.63rem"
    fontWeight: 500
    lineHeight: 1.55
    letterSpacing: "0.15em"
  brand:
    fontFamily: 'Archivo, "Segoe UI", system-ui, sans-serif'
    fontSize: "0.78rem"
    fontWeight: 600
    lineHeight: 1.55
    letterSpacing: "0.22em"
  cta:
    fontFamily: 'Archivo, "Segoe UI", system-ui, sans-serif'
    fontSize: "0.72rem"
    fontWeight: 600
    lineHeight: 1.35
    letterSpacing: "0.14em"
  state:
    fontFamily: 'Archivo, "Segoe UI", system-ui, sans-serif'
    fontSize: "0.68rem"
    fontWeight: 600
    letterSpacing: "0.12em"
    fontFeature: "tabular-nums"
  caption:
    fontFamily: 'Caveat, "Segoe UI", cursive'
    fontSize: "0.9rem"
    fontWeight: 400
    lineHeight: 1.15
  frame-date:
    fontFamily: 'Archivo, "Segoe UI", system-ui, sans-serif'
    fontSize: "0.6rem"
    fontWeight: 400
    letterSpacing: "0.08em"
  mono:
    fontFamily: 'ui-monospace, "Cascadia Mono", Consolas, monospace'
    fontSize: "0.9rem"
    fontWeight: 400
rounded:
  square: "0"
spacing:
  hair: "1px"
  gutter: "6px"
  gutter-narrow: "4px"
  xs: "0.25rem"
  sm: "0.5rem"
  md: "1rem"
  lg: "1.5rem"
  xl: "2.75rem"
components:
  cta-primary:
    backgroundColor: "{colors.ink-red}"
    textColor: "{colors.mount}"
    typography: "{typography.cta}"
    rounded: "{rounded.square}"
    padding: "0.8rem 1.5rem"
  cta-primary-hover:
    backgroundColor: "{colors.ink-red-hover}"
    textColor: "{colors.mount}"
    rounded: "{rounded.square}"
    padding: "0.8rem 1.5rem"
  cta-secondary:
    backgroundColor: "transparent"
    textColor: "{colors.graphite}"
    typography: "{typography.cta}"
    rounded: "{rounded.square}"
    padding: "0.8rem 1.5rem"
  cta-secondary-hover:
    backgroundColor: "{colors.graphite}"
    textColor: "{colors.paper}"
    rounded: "{rounded.square}"
    padding: "0.8rem 1.5rem"
  plate:
    backgroundColor: "{colors.paper-warm}"
    textColor: "{colors.graphite}"
    typography: "{typography.body}"
    rounded: "{rounded.square}"
    padding: "{spacing.md}"
  plate-mount:
    backgroundColor: "{colors.mount}"
    textColor: "{colors.graphite}"
    rounded: "{rounded.square}"
    padding: "{spacing.lg} {spacing.md}"
  plate-graphite:
    backgroundColor: "{colors.graphite}"
    textColor: "{colors.paper}"
    rounded: "{rounded.square}"
    padding: "{spacing.md}"
  plate-ink:
    backgroundColor: "{colors.ink-red}"
    textColor: "{colors.mount}"
    rounded: "{rounded.square}"
    padding: "{spacing.md}"
  sheet-action:
    backgroundColor: "{colors.ink-red}"
    textColor: "{colors.mount}"
    typography: "{typography.cta}"
    rounded: "{rounded.square}"
    padding: "{spacing.md} 0.7rem"
  sheet-frame:
    backgroundColor: "{colors.paper-warm}"
    textColor: "{colors.archive-gray}"
    typography: "{typography.caption}"
    rounded: "{rounded.square}"
    padding: "5px 5px 0"
  sheet-list:
    backgroundColor: "{colors.paper-warm}"
    textColor: "{colors.graphite}"
    rounded: "{rounded.square}"
    padding: "0.85rem 0.9rem"
  input-text:
    backgroundColor: "{colors.mount}"
    textColor: "{colors.graphite}"
    rounded: "{rounded.square}"
    padding: "0.6rem 0.7rem"
    width: "min(100%, 28rem)"
  input-textarea:
    backgroundColor: "{colors.mount}"
    textColor: "{colors.graphite}"
    rounded: "{rounded.square}"
    padding: "0.6rem 0.7rem"
    width: "min(100%, 44rem)"
  nav-link:
    backgroundColor: "transparent"
    textColor: "{colors.graphite}"
    typography: "{typography.nav}"
    padding: "0.15rem 0"
  nav-link-active:
    backgroundColor: "transparent"
    textColor: "{colors.ink-red}"
    typography: "{typography.nav}"
    padding: "0.15rem 0"
  state-open:
    backgroundColor: "transparent"
    textColor: "{colors.ink-red}"
    typography: "{typography.state}"
    rounded: "{rounded.square}"
    padding: "0.16em 0.5em 0.16em 0.42em"
  state-settled:
    backgroundColor: "transparent"
    textColor: "{colors.archive-gray}"
    typography: "{typography.state}"
    rounded: "{rounded.square}"
    padding: "0.16em 0.5em 0.16em 0.42em"
  state-closed:
    backgroundColor: "transparent"
    textColor: "{colors.archive-gray}"
    typography: "{typography.state}"
    rounded: "{rounded.square}"
    padding: "0.16em 0.5em 0.16em 0.42em"
  message:
    backgroundColor: "{colors.mount}"
    textColor: "{colors.graphite}"
    rounded: "{rounded.square}"
    padding: "0.7rem 0.9rem"
  message-error:
    backgroundColor: "{colors.mount}"
    textColor: "{colors.ink-red}"
    rounded: "{rounded.square}"
    padding: "0.7rem 0.9rem"
  pix-key:
    backgroundColor: "{colors.mount}"
    textColor: "{colors.graphite}"
    typography: "{typography.mono}"
    rounded: "{rounded.square}"
    padding: "0.4rem 0.6rem"
  skip-link:
    backgroundColor: "{colors.graphite}"
    textColor: "{colors.paper}"
    rounded: "{rounded.square}"
    padding: "0.7rem 1.1rem"
---

# Design System: IB Conecta

## Overview

**Creative North Star: "Arquivo da Congregação"**

O site é o acervo fotográfico da própria congregação, montado como uma folha de
contato. Os quadros não ilustram a página: eles **são** a página. O primeiro
viewport é uma grade de células em papel de arquivo onde doze fotografias, uma
chapa branca com o próximo culto, duas ações e três listas datadas ocupam
células inteiras separadas apenas por goteira. Nada flutua entre as células.
Esta é uma recusa deliberada do padrão de site de igreja — uma foto de palco em
hero sobre três cartões arredondados com sombra.

A personalidade é documental e institucional, não devocional decorativa: o
material é papel, fio de 1px, cantoneira de álbum e cruz de registro. A
hierarquia se resolve por **inversão** (uma chapa branca supera o papel, o papel
supera a fotografia) e por **densidade**, nunca por elevação. Há um único
vermelho de nanquim no sistema inteiro, e ele significa "a próxima ação humana"
ou "isto ainda espera você". Onde outros sistemas usariam verde de sucesso,
âmbar de atenção e vermelho de erro, este usa a **forma** da marca.

O mundo cobre o site inteiro — as treze superfícies públicas, o login e a área
privada de membros. Uma varredura mecânica confirmou que nenhuma superfície
ficou com classe órfã do mundo anterior. Três invariantes são verificadas por
máquina em `apps/public/tests/test_design_contract.py` (6 testes, dentro de 185
no total): nenhum `border-radius`, nenhuma sombra, e nenhuma cor fora da
amostragem do comp aprovado. O contrato de direção mora como comentário no topo
de `templates/base.html`, e o teste também verifica que ele continua lá.

**Trade-off aceito e registrado.** O princípio 4 do `PRODUCT.md` (leveza para o
visitante rural em conexão limitada) foi explicitamente sobrescrito pelo usuário
para este redesenho: o visual rico vale a página mais pesada, e vale
**igualmente em todo dispositivo** — não há versão magra para o celular. O
visitante rural em celular segue sendo o público primário e a página tem de
continuar legível e usável nele, mas o peso deixou de ser teto. Isto é uma
decisão de produto, não um descuido de implementação.

**Key Characteristics:**
- Papel de arquivo com grão em raster tileado (512px) como chão de toda tela
- Grade de folha de contato de borda a borda, sem coluna centrada e sem margem externa
- Goteira de 6px como único separador; canto reto e zero sombra em todo o sistema
- Fotografia como material da página, com legenda manuscrita sob cada quadro
- Cantoneira de álbum e cruz de registro como geometria assinatura
- Um único vermelho de nanquim como sinal; estado marcado por forma, não por matiz
- Archivo com algarismos tabulares para tudo que informa; Caveat só na legenda
- Um único momento de movimento: a folha revela

## Colors

Paleta de arquivo: papel morno, três valores de tinta e um vermelho. Todos os
sete tons base foram **amostrados** do comp aprovado
`.impeccable/mocks/comp-arquivo-b-folha.png` (registro em
`.impeccable/surfaces/templates-public-home-html.md`), nunca estimados; três
tons derivados existem só para estado de interação.

### Primary
- **Vermelho de Nanquim** (`ink-red`, `#8B211A`): O único sinal do sistema.
  Preenche a ação primária (célula inteira na home, `.cta` nas demais telas),
  pinta a data de cada linha de lista datada, o `caret-color`, o anel de
  `:focus-visible`, o `accent-color` de caixas de seleção, a chamada de nota de
  rodapé, o link em hover, e o tom `open` do selo de estado. Sua raridade é o
  mecanismo: numa tela cheia de papel e cinza, ele resolve "para onde ir" e "o
  que ainda espera você" sem legenda.
- **Vermelho de Nanquim Escuro** (`ink-red-hover`, `#6F1A14`): Exclusivamente
  hover da ação primária. É um corte mais escuro do mesmo vermelho, não um
  segundo sinal.

### Secondary
- **Grafite** (`graphite`, `#222527`): A tinta do sistema. Cor de texto do corpo,
  de todo link em repouso, do wordmark e da navegação; preenche a chapa da ação
  secundária (WhatsApp) e o chip do skip-link. Sobre grafite o texto é papel.
- **Grafite Escuro** (`graphite-hover`, `#15181A`): Só hover de chapa grafite.
- **Preto de Fotografia** (`photo-black`, `#111313`): A tinta mais funda,
  reservada ao buraco de vídeo do `.media-embed` e ao texto na impressão. Não é
  cor de superfície nem de texto em tela.

### Neutral
- **Papel de Arquivo** (`paper`, `#ECE8E2`): O chão de toda tela, com o raster de
  grão `static/img/paper.png` tileado a 512px por cima. Também é a cor do texto
  sobre chapa grafite.
- **Fio e Goteira** (`paper-shade`, `#D4D0CA`): Todo fio de 1px de célula,
  chapa, painel, linha de lista e borda de campo de tabela. É a estrutura
  visível da folha. Também é o fundo de reserva de uma fotografia que não
  carregou.
- **Papel Morno** (`paper-warm`, `#F4F1EC`): Interior de chapa e de painel — um
  papel um passo mais claro que o chão, o que faz a chapa ler como montada
  sobre a folha sem nenhuma sombra.
- **Branco de Montagem** (`mount`, `#F9F9F9`): O valor mais alto do sistema e por
  isso o mais escasso. Preenche a chapa da chapa do próximo culto (o elemento
  dominante da home), o interior de campo de formulário, a chave PIX, a caixa de
  mensagem, e é o texto sobre vermelho de nanquim.
- **Cinza de Arquivo** (`archive-gray`, `#74706C`): Texto secundário — rótulo,
  legenda manuscrita, lede, meta de notícia, `helptext`, rodapé, cabeçalho de
  tabela, e o tom `settled`/`closed` do selo. Também é o fio da régua sob a
  navegação e acima do rodapé, e a cor do traço da cantoneira e da cruz de
  registro.

### Named Rules

**A Regra do Único Sinal.** O vermelho de nanquim é a única cor de sinal do
sistema. Não existe verde de sucesso, âmbar de atenção nem um segundo vermelho.
Sucesso, pendência e recusa se distinguem pela forma da marca. O teste
`test_the_ink_red_is_the_only_signal_colour` reprova um segundo vermelho.

**A Regra da Amostragem.** Toda cor do sistema veio da amostragem do comp
aprovado ou é um escurecimento declarado dela. Nenhuma cor é estimada. Um hex
novo na folha de estilo reprova em
`test_every_colour_was_sampled_and_none_estimated`; introduzir um tom exige
amostrar de novo e atualizar o conjunto do teste, conscientemente.

**A Regra do Papel como Chão.** A página é papel de arquivo claro. Grafite e
vermelho são chapas *sobre* a folha — uma ação, um cabeçalho invertido, um chip.
Nunca são fundo de tela, de seção nem de área privada.

## Typography

**Display Font:** Archivo, self-hosted (com Segoe UI, system-ui, sans-serif)
**Body Font:** Archivo, self-hosted (a mesma face; não há segunda face de texto)
**Accent Font:** Caveat, self-hosted — exclusivamente legenda de quadro
**Label/Mono Font:** ui-monospace, Cascadia Mono, Consolas, monospace — só chave PIX

**Character:** Uma grotesca de arquivo faz todo o trabalho informativo — o
horário do culto, o wordmark, a navegação, as ações, as listas e o corpo — com
peso 600 e tracking largo em caixa alta fazendo a hierarquia nos tamanhos
pequenos, e tracking negativo apertando os tamanhos grandes. Ao lado dela,
uma única voz manuscrita anota as fotografias, como quem escreveu a lápis sob a
prova. Ambas são SIL OFL, servidas do próprio repositório como woff2 variável
com subsets latin e latin-ext e `font-display: swap`. `font-variant-numeric:
tabular-nums` está ligado no `body`: toda data e todo horário alinham em coluna.

### Hierarchy
- **Display** (600, `clamp(1.7rem, 3.6vw, 3.4rem)`, line-height 1.05, tracking
  -0.015em, tabular): O horário do próximo culto na chapa branca da home
  (`h1.service-when`). O maior tipo do sistema; existe só ali.
- **Headline** (600, `clamp(1.5rem, 3.4vw, 2.05rem)`, line-height 1.15, tracking
  -0.01em): Título de página interna (`h1`), dentro de um `.page-head` fechado
  por régua de cinza de arquivo. Sem chapa atrás.
- **Title** (600, 1.15rem, line-height 1.15): `h2` de conteúdo dentro de texto
  rico. Não é o cabeçalho de célula.
- **Section Label** (600, 0.7rem, tracking 0.15em, caixa alta, com régua de 1px
  embaixo): Cabeçalho de célula da folha (`.cell-heading`) e de painel
  (`.panel h2`/`h3`). É o rótulo de uma gaveta do arquivo — a voz padrão de
  título de bloco no sistema, mais frequente que o Title.
- **Lede** (400, 1.05rem, cinza de arquivo): Frase de apoio sob um título de
  página, e o endereço na chapa do próximo culto (aí em peso 500 e grafite).
- **Body** (400, 1rem, line-height 1.55, tabular): Leitura padrão. Prosa mede no
  máximo 66ch, mesmo com a casca de borda a borda.
- **Label** (600, 0.63rem, tracking 0.16em, caixa alta, cinza de arquivo):
  Rótulo de dado sobre chapa e rótulo de campo de formulário (0.68rem / 0.13em
  no formulário). Sobre chapa grafite ou vermelha, o rótulo é papel a 70%.
- **Nav** (500, 0.63rem, tracking 0.15em, caixa alta): Links da fileira de
  navegação e do rodapé social. O wordmark é o mesmo tamanho de família em 0.78rem
  / 600 / tracking 0.22em.
- **CTA** (600, 0.72rem, tracking 0.14em, caixa alta): Botões e a célula-ação da
  folha (0.13em de tracking, line-height 1.35 quando quebra em duas linhas).
- **State** (600, 0.68rem, tracking 0.12em, caixa alta, tabular): Texto do selo
  de estado e da tag de ledger (0.62rem / 0.13em).
- **Caption** (Caveat, 0.9rem, line-height 1.15, cinza de arquivo): Legenda sob
  a fotografia. Em viewport ≤560px cai a 0.82rem.
- **Frame Date** (Archivo 0.6rem, tracking 0.08em, caixa alta): A data à direita
  na legenda de um quadro. Volta para a grotesca de propósito — data é dado, não
  anotação.
- **Mono** (400, 0.9rem): Só a chave PIX, com `user-select: all`. Nunca título,
  nunca navegação.

### Named Rules

**A Regra das Duas Vozes.** Archivo escreve tudo que informa. Caveat escreve
apenas a legenda de uma fotografia — é a mão de quem anotou o acervo. Um rótulo,
um botão, um cabeçalho ou uma data em Caveat quebra a regra; a data dentro da
própria legenda é Archivo justamente por isso.

**A Regra dos Algarismos Tabulares.** Horário, data e valor alinham em coluna.
`tabular-nums` está no `body` e no selo de estado; não desligue localmente.

**A Regra do Rótulo, Não do Chapéu.** A caixa alta tracked rotula um dado ou uma
gaveta — "PRÓXIMO CULTO" acima do horário, "AGENDA" acima da lista. Ela nunca é
um chapéu decorativo acima de um título de página.

## Layout

A casca é de borda a borda: `.wrap` ocupa 100% da largura com uma goteira de 6px
de respiro nas laterais e no pé. **Não existe coluna centrada.** A folha de
contato tem de encostar nas bordas para ler como folha de contato; uma coluna de
720px centrada é outro mundo.

O ritmo é a goteira (`--gutter: 6px`, 4px em ≤560px), que faz o `gap` da grade, a
margem entre painéis e o `gap` da fileira de ações. A escala de espaço interno é
0.25 / 0.5 / 1 / 1.5 / 2.75rem. Fios são sempre `--hair: 1px`.

**Casca.** Uma fileira de navegação em linha única com o wordmark à esquerda e
todos os destinos visíveis, fechada por régua de 1px em cinza de arquivo. Não há
hamburger em nenhuma largura — a fileira quebra em várias linhas e continua
inteira. O rodapé é a mesma ideia invertida: régua acima, texto em cinza de
arquivo.

**Home.** `.contact-sheet` é uma grade de 6 colunas com `grid-auto-flow: row
dense`. Cada região ocupa células inteiras por `grid-area` fixo: a chapa do
próximo culto num bloco 2×1 no alto à esquerda, a ação primária e a secundária
uma célula cada logo abaixo, as listas de Agenda, Sermões e Notícias em blocos de
duas colunas, a alça do Instagram no pé à esquerda, e os doze quadros
preenchendo o resto — vinte e quatro células no total. A densidade é um
compromisso da composição, não um humor: uma grade remontada com uma fração dos
quadros é outro desenho. Acima de 901px a folha ganha 4 fileiras iguais e altura
`calc(100svh - 3.5rem)` com piso de 33rem, e a fotografia toma a altura que a
fileira deixa depois da legenda em vez de forçar o quadrado.

**Páginas internas.** `.cms-page` tem teto em `--sheet: 74rem` e **encosta na
esquerda**, sem margem automática. Não é uma coluna centrada — é uma folha de
registro alinhada à mancha da navegação, que é sangria em toda página; a margem
sobra de um lado só, à direita, como papel em volta da folha. Centralizar deixaria
o conteúdo alinhado a nada, e não pôr teto nenhum fazia a linha do registro correr
1.893px numa tela de 1920, onde nada é varrível. A home fica de fora deste teto: a
folha de contato é sangria por desenho.

Dentro da folha, a prosa tem o seu próprio teto (`--measure: min(66ch, 100%)`),
aplicado em lede, texto rico, nota do registro, nota de rodapé e no convite do
rodapé; campos de formulário param em 28rem e áreas de texto em 44rem.
`.panel-set` distribui painéis em `auto-fit / minmax(min(19rem, 100%), 1fr)`,
então eles se ladrilham na folha em telas largas em vez de empilhar num vazio.

**Adaptação.** Dois pontos de quebra autorais. Em ≤900px a grade cai para 4
colunas e as regiões abandonam o `grid-area` fixo para seguir a ordem do DOM —
que já é a ordem de leitura: fatos, ações, listas datadas, depois o acervo.
Chapa e listas ocupam as 4 colunas, ação e alça ocupam 2. Em ≤560px a grade cai
para 2 colunas, a goteira afina para 4px e cada ação ocupa uma coluna. A ordem
do DOM é a rede de segurança do layout; mantenha-a legível sem CSS.

**Impressão.** Fundo branco, texto em preto de fotografia, navegação e ações
ocultas, e todo fio promovido de `paper-shade` para `archive-gray` porque o fio
claro desaparece na impressora. A marca do selo força `print-color-adjust:
exact`. Isto é papel operacional (escala de ministério, coletânea), não um
segundo layout público.

### Named Rules

**A Regra da Célula Inteira.** A página é uma grade de células e toda região
ocupa células inteiras. Nada flutua entre células, nada sangra pela metade de
uma goteira.

**A Regra da Medida.** A casca é de borda a borda; a prosa não. Todo bloco de
texto corrido mede no máximo 66ch. Campo de formulário tem o mesmo dever: uma
linha de 730px de largura para digitar um usuário é defeito, não amplitude.

**A Regra da Ordem de Leitura.** O posicionamento fixo da folha é um luxo de
viewport largo. Em qualquer largura menor a grade volta para a ordem do DOM, e a
ordem do DOM é sempre fatos, ações, listas, acervo.

## Elevation & Depth

**Este sistema não tem sombra nenhuma.** Nem `box-shadow`, nem `text-shadow`,
nem elevação, nem vidro, nem gradiente de profundidade. O teste `test_no_shadows`
reprova a primeira que aparecer.

A profundidade vem de duas coisas: a **goteira**, que separa uma chapa da
seguinte sem precisar levantá-la, e a **inversão de valor**, que classifica. Uma
chapa lê como montada sobre a folha porque seu interior é um papel um passo mais
claro (`paper-warm`) dentro de um fio de 1px, e porque tem 6px de papel escuro em
volta. É como uma prova fica sobre a folha de contato: apoiada, não flutuando.

O hover nunca levanta, nunca escala, nunca translada. Ele **escurece o material**
(vermelho para vermelho escuro, grafite para grafite escuro), aprofunda a
fotografia e traz a legenda de cinza de arquivo para grafite.

### Named Rules

**A Regra da Chapa Plana.** Nenhuma superfície tem sombra, em nenhum estado. Se
um bloco precisa se destacar, ele inverte ou ganha goteira — não altura.

**A Regra da Inversão como Hierarquia.** A ordem de patente é branco de montagem
> papel morno > papel > fotografia, com grafite e vermelho de nanquim fora dessa
escala, reservados a ação. O elemento mais importante de uma tela é o mais claro,
não o mais alto.

## Shapes

**Canto reto em absolutamente tudo** — chapa, célula, fotografia, campo, botão,
chip, mensagem. `border-radius` não existe no sistema e `test_no_rounded_corners`
reprova qualquer valor diferente de zero. Esta é a invariante mais fácil de
perder por cópia de um trecho de CSS de outro projeto, e é a que mais depressa
transforma o arquivo em cartão de site de igreja.

A gramática de forma é fio e retângulo. Todo contorno é um fio de 1px: em
`paper-shade` quando delimita material dentro da folha (chapa, painel, quadro,
linha de lista, célula de tabela), em `archive-gray` quando é estrutura de
página (régua da navegação, régua do rodapé, `page-head`, cabeçalho de tabela,
borda de campo de formulário).

Duas geometrias assinatura, ambas SVG autorado, e nenhuma delas é opcional:

- **Cantoneira de álbum** (`static/img/corner.svg`): triângulo chapado de 16px em
  branco de montagem com traço de 0.75 em cinza de arquivo, um por canto, cada um
  girado 90°, ancorado em -1px para morder o fio da chapa. Segura a chapa do
  próximo culto na folha.
- **Cruz de registro** (`static/img/tick.svg`): cruz de centro aberto de 12px em
  cinza de arquivo a 70% de opacidade, posicionada no canto superior esquerdo de
  cada quadro com deslocamento de `-6px - var(--gutter)/2` — ou seja, ela cai na
  *interseção* da grade. Tilear essa cruz pelo container transforma a folha numa
  textura pontilhada, que não é o que o comp desenha.

Um quadro tem 5px de papel nas laterais e no topo e nada no pé: a legenda encosta
na base. A marca do selo de estado é uma caixa de 0.62em com fio de 1px em
`currentcolor`. Estado em mensagem é barra esquerda de 4px, `solid` no padrão e
`double` no erro — peso de fio, não só matiz.

### Named Rules

**A Regra do Canto Reto.** Zero raio, em qualquer elemento, em qualquer estado.
Um canto arredondado é outro mundo, não uma variação deste.

**A Regra da Forma que Sobrevive ao Cinza.** Todo estado se distingue pela forma
antes da cor: caixa vazada, cheia ou cortada; fio simples ou duplo. As telas da
área privada são impressas em preto e branco e lidas por quem não distingue
matiz. Uma diferença que só existe em cor não é uma diferença.

## Components

Chapas chapadas em papel de arquivo, separadas por goteira, classificadas por
inversão. Nenhum ícone de glifo em nenhum lugar do sistema — o que não é tipo é
SVG autorado.

### Buttons
- **Shape:** Retângulo reto (raio `0`), fio de 1px da própria cor.
- **Primary:** Preenchimento em vermelho de nanquim, texto em branco de montagem,
  caixa alta tracked, padding 0.8rem 1.5rem.
- **Secondary:** Fundo transparente, fio e texto em grafite, mesmo padding.
- **Hover / Focus:** A primária escurece para vermelho de nanquim escuro; a
  secundária **inverte** — preenche grafite com texto papel. Sem translado, sem
  escala, sem sombra. `:focus-visible` é sempre um contorno de 2px em vermelho de
  nanquim com 2px de deslocamento; no skip-link o contorno vira papel porque ele
  está sobre grafite.
- **Groups:** `.actions` alinha botões em linha que quebra, com a goteira de 6px
  de `gap`.

### Cards / Containers
- **Corner Style:** Reto (`0`).
- **Background:** Papel morno por padrão. Três variantes de inversão: branco de
  montagem (a mais alta), grafite (texto papel) e vermelho de nanquim (texto
  branco de montagem).
- **Shadow Strategy:** Nenhuma — ver Elevation & Depth.
- **Border:** Fio de 1px em `paper-shade`; nas variantes invertidas o fio assume a
  própria cor de preenchimento, então a chapa lê como um bloco chapado.
- **Internal Padding:** 1rem; a chapa do próximo culto abre para 1.5rem/1rem.
  Painéis se separam por 6px de goteira, não por margem grande.

### Inputs / Fields
- **Style:** Interior em branco de montagem, fio de 1px em cinza de arquivo,
  canto reto, padding 0.6rem 0.7rem, tipo 0.95rem herdado da grotesca. Texto,
  e-mail, número, telefone, data, datetime-local, senha, busca, URL, arquivo,
  `textarea` e `select` dividem a receita. Caixa de seleção e rádio ficam em
  largura automática, com `accent-color` vermelho.
- **Width:** `100%` com teto — 28rem no campo de uma linha, 44rem na `textarea`
  (mínimo de 7rem de altura). O teto é decisão, não acidente: sem ele o campo de
  usuário do login esticava a 730px, o que estraga a medida e faz a tela parecer
  um formulário administrativo.
- **Label:** 0.68rem / 600 / tracking 0.13em / caixa alta em cinza de arquivo,
  acima do campo.
- **Focus:** O fio do campo passa a vermelho de nanquim, somado ao anel de
  `:focus-visible` do sistema. Sem brilho, sem halo.
- **Error:** `.errorlist` e `.form-errors` são listas sem marcador em branco de
  montagem com texto vermelho e **barra esquerda de 4px em `double`** — a duplicação
  do fio é o que carrega o erro no preto e branco.

### Navigation
- **Style:** Fileira única de links em caixa alta 0.63rem / 500 / tracking 0.15em,
  em grafite, sem sublinhado, com fio inferior transparente reservado. Hover e
  `aria-current="page"` pintam texto e fio em vermelho de nanquim — o sublinhado
  não aparece do nada, ele acende. A régua de 1px em cinza de arquivo sob a
  fileira é o que a torna uma banda de arquivo e não uma barra de app. O
  wordmark é tipo letra-espaçada (0.22em) à esquerda, não há arquivo de logo.
- **Mobile:** A mesma fileira, quebrando em linhas, com `gap` de 0.35rem/1rem em
  ≤560px. Nunca há hamburger, nunca há gaveta, nunca há barra fixa.

### Lists
- **Sheet list** (célula datada da home): cabeçalho de célula com régua, linhas
  separadas por fio de 1px, última linha sem fio. A data é um bloco fixo em
  vermelho de nanquim 0.78rem / 600 à esquerda do título; o título é grafite sem
  sublinhado e ganha vermelho com sublinhado em hover. Estado vazio é uma frase
  em cinza de arquivo, não uma ilustração.
- **News list** (herdada): a mesma lógica em 0.55rem de padding vertical com meta
  em caixa alta 0.78rem em cinza de arquivo. Continua servindo as listas da área
  privada; nos índices públicos datados foi substituída pelo registro.

### Dated register (signature)
O índice do acervo (`.register` em agenda, sermões e notícias). É o componente que
distingue um índice de arquivo de uma lista de cartões: **a data é o índice, não
uma legenda**. Cada entrada é uma grade de duas colunas — coluna de data de 5.5rem
e corpo — onde o dia sai em `clamp(1.5rem, 3.2vw, 2rem)` / 600 em preto de
fotografia com algarismos tabulares, e mês, ano e hora ficam abaixo em 0.63rem /
600 / tracking 0.16em em caixa alta, cinza de arquivo.

A coluna de data termina num fio vertical de 1px em `paper-shade` que se estende
por toda a altura da entrada; cruzando com o fio inferior de cada linha, esses
encontros são a mesma marca de registro da folha de contato — a grade do acervo
reaparece no índice.

O hover **aquece o material** (`paper-warm`) e leva o título ao vermelho de
nanquim com sublinhado; nunca levanta, nunca ganha sombra. Abaixo de 34rem a
grade colapsa para uma coluna, a data vira linha de cabeçalho da entrada em
`flex-direction: row`, o fio vertical desaparece e o dia cai para 1.3rem.

As etiquetas da entrada (`.register-tag`) são chips de fio reto em cinza de
arquivo; `--asks` as promove a vermelho de nanquim e é reservada ao que **pede
algo do visitante** (exige inscrição). Vale aqui a regra Marcar a Exceção: só o
caso informativo ganha etiqueta — um sermão sem mídia recebe "Somente texto",
porque a mídia é a norma, e nenhum evento recebe etiqueta por ser comum.

### Tables
O ledger do arquivo. Largura total, `border-collapse: collapse`, tipo 0.9rem,
célula com padding 0.5rem 0.6rem e alinhamento superior, fio inferior em
`paper-shade`. O `th` é rótulo: 0.63rem / 600 / tracking 0.14em em caixa alta,
cinza de arquivo, com o fio inferior promovido a cinza de arquivo.

### Tags
Chip retangular de fio de 1px, 0.62rem em caixa alta tracked. O estado está na
forma do fio: `--confirmed` inverte para grafite chapado com texto papel,
`--pending` mantém o fio `dashed`, `--refused` usa fio `double` de 3px em
vermelho de nanquim. Serve linha de ledger; para estado de fluxo da área
privada, use o selo.

### Messages
Lista sem marcador de notas em branco de montagem com fio de 1px e barra
esquerda de 4px em grafite. `.error` troca a barra para `double` em vermelho de
nanquim e o texto para vermelho. Sem ícone, sem fundo colorido, sem verde de
sucesso.

### State seal (signature)
O selo de estado (`{% state %}` em `apps/private_area/templatetags/state_tags.py`,
marcação em `templates/private_area/_state.html`) é o componente assinatura da
área privada, que é modo Operar: quem abre "Minhas convocações" precisa ver de
relance qual linha ainda espera resposta dela.

Três tons, e o que os distingue é a **forma da marca**:

| Tom | Marca | Cor | Significado |
|---|---|---|---|
| `open` | caixa vazada | vermelho de nanquim | ainda espera alguém |
| `settled` | caixa cheia | cinza de arquivo | resolvido |
| `closed` | caixa cortada na diagonal | cinza de arquivo | resolvido pelo não |

O selo é um chip de fio em `currentcolor` com a marca de 0.62em à esquerda do
rótulo, em caixa alta 0.68rem tracked e algarismos tabulares. A marca é
`aria-hidden`; o significado do tom vai em texto visualmente oculto para leitor
de tela. O mapa de tons cobre todos os vocabulários de status do código —
`AssignmentStatus`, `BudgetLineStatus`, `SongStatus`,
`EventRegistration.Status`, `PixStatus` — e uma chave desconhecida cai em `open`
de propósito: um estado que o desenho não previu é exatamente o que a liderança
precisa notar, não esconder. Oito testes cobrem esse mapeamento.

### Service mount plate (signature)
A chapa do próximo culto (`.plate.plate--mount.sheet-mount`) é o elemento
dominante da home e o mais claro da tela: bloco 2×1 em branco de montagem,
segurado pelas quatro cantoneiras de álbum, com rótulo "PRÓXIMO CULTO", o
horário em display, o endereço e a linha institucional, centrado verticalmente.
Horário e endereço vêm do CMS; o desenho não inventa fato nenhum.

### Contact-sheet frame (signature)
Um quadro é uma fotografia em `aspect-ratio: 1` com `object-fit: cover` sobre
mount de papel morno, legenda manuscrita embaixo à esquerda e data em grotesca
miúda à direita, cruz de registro no canto e fio de 1px em volta. A imagem leva
`filter: saturate(0.4) contrast(1.07) brightness(0.97)` para ler como prova de
arquivo — quase monocromática, casta quente, pretos fundos — e o hover devolve
saturação (`0.9`) e escurece a legenda. `height: auto` no `img` é estrutural: os
atributos `width`/`height` da marcação são uma dica de apresentação que vence o
`aspect-ratio` e estica a fileira sem ele.

A fonte dos quadros (`apps/public/archive.py`) tem três níveis, nesta ordem:
acervo sincronizado da API oficial do Instagram, acervo curado no CMS, e quadros
semeados sintéticos que acompanham o repositório. **Os doze quadros que hoje
sobem são rasters sintéticos gerados, não fotografia da igreja**, e a home
declara isso numa nota de rodapé (`#acervo-exemplo`). Eles nunca afirmam fato: não
carregam data nem nome de pessoa. Serão substituídos automaticamente quando a
congregação conectar uma conta profissional do Instagram (Creator ou Business —
uma conta pessoal não tem acesso a nenhuma API oficial desde a retirada da Basic
Display). Toda fotografia que o site sobe carrega procedência: o prompt de
geração no raster sintético, o permalink e o timestamp na mídia real.

### Media embed
Host de 16/9 em largura total, preenchido com preto de fotografia e fio de 1px,
com o iframe cobrindo o interior. Nada dá autoplay. O preto de fotografia aqui é
o buraco de vídeo; não promova ele a cor de superfície nem de texto.

### PIX key
Chip em branco de montagem com fio de 1px, `ui-monospace` 0.9rem, padding
0.4rem 0.6rem, `user-select: all`. É dado para copiar uma vez, não é tag nem
botão.

### Footnote
Nota de arquivo: 0.78rem em cinza de arquivo, com teto de 66ch, régua de 1px
acima e `scroll-margin-top`. A chamada no corpo (`.footnote-ref`) é um
sobrescrito em vermelho de nanquim. Ao receber `:target` a régua acende em
vermelho e o texto vai a grafite. É assim que o site declara o que ele não sabe
ou o que é provisório — inclusive as fotografias de exemplo.

### Motion
Um único momento, e ele pertence ao acervo: `@keyframes develop` traz cada
fotografia da home de opacidade 0 a 1 em 0.5s `ease-out`, escalonada por
`--frame-index * 55ms` na ordem de leitura — uma prova subindo na bandeja. Nada
desliza, nada escala, nada levanta. `prefers-reduced-motion: reduce` entrega a
folha já revelada, sem escalonamento. Não há coreografia de entrada em nenhuma
outra tela.

## Do's and Don'ts

### Do:
- **Do** manter a folha de borda a borda: `.wrap` em 100% com 6px de goteira, sem
  coluna centrada.
- **Do** fazer toda região ocupar células inteiras da grade, separadas pela
  goteira de 6px.
- **Do** classificar por inversão de valor — branco de montagem acima de papel
  morno, acima de papel, acima de fotografia.
- **Do** usar o vermelho de nanquim só como sinal: a próxima ação, a data de uma
  linha, o foco, o que ainda espera resposta.
- **Do** marcar todo estado pela forma antes da cor — caixa vazada, cheia ou
  cortada; fio simples ou duplo — para que sobreviva à impressão em preto e branco.
- **Do** manter cantoneira de álbum, cruz de registro e legenda manuscrita: é a
  geometria assinatura, não enfeite.
- **Do** amostrar do comp aprovado antes de introduzir qualquer cor, e atualizar
  o conjunto de `test_design_contract.py` no mesmo commit.
- **Do** limitar prosa e campo de formulário à medida (66ch; 28rem/44rem em
  campo), mesmo com a casca larga.
- **Do** tirar horário, endereço, WhatsApp, PIX e handle do CMS, e declarar em
  nota de rodapé o que for provisório.
- **Do** honrar `prefers-reduced-motion` entregando a folha já revelada.

### Don't:
- **Don't** tratar o mundo anterior — parede de cal, chapa de esmalte, latão,
  Overpass, cantos de 1.15rem, parafusos de canto, sombra deslocada — como o
  sistema atual. Aquele mundo está aposentado.
- **Don't** introduzir `border-radius` em nada, em nenhum estado.
- **Don't** introduzir sombra, elevação, vidro ou gradiente de profundidade;
  profundidade é goteira e inversão.
- **Don't** adicionar uma segunda cor de sinal — nem verde de sucesso, nem âmbar,
  nem um segundo vermelho.
- **Don't** usar grafite ou vermelho de nanquim como fundo de tela ou de seção;
  eles são chapa de ação sobre papel claro.
- **Don't** escrever rótulo, botão, cabeçalho ou data em Caveat; ela é só a
  legenda da fotografia.
- **Don't** pôr um chapéu decorativo acima de um título de página. A caixa alta
  tracked rotula um dado ou uma gaveta, e nada mais.
- **Don't** usar ícone de glifo, fonte de ícone ou emoji como sinal de interface;
  o que não é tipo é SVG autorado.
- **Don't** levantar, escalar ou transladar no hover; escureça o material.
- **Don't** rebaixar as fotografias a uma faixa decorativa nem remontar a folha
  com uma fração dos quadros — a densidade de vinte e quatro células é o desenho.
- **Don't** tilear a cruz de registro pelo container; ela mora na interseção da
  grade, uma por célula.
- **Don't** trocar a marca do selo de estado por uma bolinha colorida, nem
  distinguir dois estados só por matiz.
- **Don't** apresentar as fotografias sintéticas como acervo da igreja, nem
  remover a nota de rodapé que as declara enquanto elas estiverem no ar.
- **Don't** promover o preto de fotografia do `.media-embed` a cor de superfície
  ou de texto, e nunca dê autoplay em vídeo.
- **Don't** promover as regras de impressão (fundo branco, chrome oculto, fio em
  cinza de arquivo) para o layout de tela.
