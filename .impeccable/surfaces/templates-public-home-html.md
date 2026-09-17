---
version: 1
slug: "templates-public-home-html"
primary_target: "templates/public/home.html"
related_targets: ["templates/base.html","static/css/ib-conecta.css","templates/accounts/login.html","templates/private_area/home.html"]
---

# Editorial acolhedor — aprovação em 2026-09-16

O usuário escolheu explicitamente Encontro — editorial acolhedor após ver a prévia, preservada em .impeccable/mocks/comp-editorial.png com aprovação no sidecar. Essa escolha substitui o antigo Arquivo da Congregação. Execução comp-led; a prévia exibida foi aprovada pelo nome nesta conversa, sem necessidade de outra escolha de estilo.

Escopo: homepage (Persuade), páginas públicas de leitura e formulários, autenticação e aparência compartilhada das ferramentas privadas (Operate). Preservar conteúdo editável, permissões, dados e URLs.

Composição: logo original, navegação agrupada, convite editorial em serifada à esquerda e foto ampla à direita. Faixa vinho com culto, endereço e visita. Agenda e sermões em colunas; galeria com fotos maiores; notícias, oração e rodapé. Celular empilha e usa menu com disclosure acessível. Página interna é centralizada, com títulos editoriais e formulários legíveis.

O texto configurado no CMS prevalece sobre a frase ilustrativa da prévia. Headline padrão mostra a frase aprovada; headline personalizada permanece intacta. Horários, endereço, WhatsApp e redes vêm do CMS. Fotos sintéticas da prévia NÃO serão extraídas nem utilizadas como reais. Fotos existentes continuam claramente identificadas até entrada do acervo autêntico.

Materiais: DM Serif Display local (normal e itálico) + Archivo local; fundo claro #faf9f6, vinho #862d36, texto #262722. Fotos: raster original da galeria; logo: anexo original, corte de apresentação por CSS; controles, grids e seta: HTML/CSS/SVG. Cantos 8–18px, sem sombra ou textura. Animação curta apenas na revelação da foto, desativada em reduced-motion.

Verificação: desktop 1536×1024 e celular 390×1024, home/visita/login/oração/agenda/área privada/coletânea. 209 testes Django passaram. Os quatro ajustes pedidos pelo revisor foram classificados como resolvidos, disposition ship, no escopo dessas correções. Comp, screenshots e conteúdo verdadeiro precisam ser considerados separadamente. A base isolada de preview apresenta aviso de dados fictícios; não é confirmação de fatos da igreja.
