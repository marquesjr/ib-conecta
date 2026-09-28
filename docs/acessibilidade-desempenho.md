# Checklist WCAG 2.2 AA e desempenho móvel

Execução de 28/09/2026 (issue #38). Base: `seed_demo` em SQLite, servida por
gunicorn com WhiteNoise e gzip (aproxima o Caddy de produção, que também
comprime com gzip/zstd).

## Superfícies verificadas

Home, Planeje sua visita, Agenda (lista e evento com inscrição de retiro),
Notícias (lista e notícia), Contribuições, Pedido de oração, Quero conhecer e
Privacidade.

## Como foi verificado

- **axe-core** com as regras `wcag2a`, `wcag2aa`, `wcag21a`, `wcag21aa`,
  `wcag22aa` e `best-practice`, em 390 px e 1280 px.
- **Reflow** em 320 px (sem rolagem horizontal da página).
- **Teclado:** Tab por todas as páginas conferindo o indicador de foco;
  Esc fecha o submenu e o menu móvel; link "Ir para o conteúdo" funciona.
- **Tamanho de alvo (2.5.8):** controles com pelo menos 24 × 24 px.
- **Formulários:** envio com erros para conferir `aria-invalid`,
  `aria-describedby` e para onde vai o foco.
- **Lighthouse 12 (perfil móvel, 4G simulado)** nas sete superfícies principais.

## Metas mínimas acordadas

| Métrica (Lighthouse móvel) | Meta |
| --- | --- |
| Acessibilidade | 100 |
| Desempenho | ≥ 90 |
| LCP | ≤ 2,5 s |
| CLS | ≤ 0,1 |
| TBT | ≤ 200 ms |

## Resultado depois das correções

| Página | Desempenho | Acessib. | LCP | CLS | Peso |
| --- | --- | --- | --- | --- | --- |
| Home | 99 | 100 | 2,0 s | 0,021 | 194 KiB |
| Planeje sua visita | 100 | 100 | 1,5 s | 0,001 | 112 KiB |
| Agenda | 100 | 100 | 1,7 s | 0,003 | 112 KiB |
| Notícias | 100 | 100 | 1,5 s | 0,007 | 112 KiB |
| Contribuições | 100 | 100 | 1,7 s | 0,001 | 112 KiB |
| Pedido de oração | 100 | 100 | 1,5 s | 0,001 | 112 KiB |
| Quero conhecer | 100 | 100 | 1,5 s | 0,001 | 112 KiB |

TBT foi 0 ms em todas. Boas práticas e SEO ficaram em 100. O axe não aponta
nenhuma violação nas dez páginas.

## Itens verificados

| Critério | Situação |
| --- | --- |
| 1.1.1 Alternativas em texto | OK: logo, fotos e quadros têm `alt`; ícones SVG são `aria-hidden`. |
| 1.3.1 Informação e relações | Corrigido: erros gerais do formulário ficavam numa lista dentro de outra lista. |
| 1.3.5 Propósito do campo | Corrigido: nome, e-mail e telefone agora têm `autocomplete`; telefone usa `type="tel"`. |
| 1.4.3 Contraste | OK pelo axe e pelo Lighthouse. |
| 1.4.10 Reflow | OK em 320 px; só o mural da home rola na horizontal, dentro do próprio trilho. |
| 2.1.1 Teclado | Corrigido: a tabela de retenção da privacidade rolava na horizontal sem poder receber foco. |
| 2.4.1 Pular blocos | OK: "Ir para o conteúdo" leva ao `main`. |
| 2.4.7 / 2.4.11 Foco visível | Corrigido: campos de formulário ganharam contorno de foco explícito (o campo de data perdia o contorno). |
| 2.5.8 Tamanho do alvo | Corrigido: caixas de seleção passaram de 18 para 24 px; links do rodapé e redes sociais ganharam altura mínima de 24 px. |
| 3.3.1 Identificação de erro | Melhorado: depois de enviar com erro, o foco vai para o primeiro campo inválido ou para o aviso geral (`role="alert"`). |
| 3.3.2 Rótulos | OK: todos os campos têm `label`; o campo-armadilha anti-spam agora fica oculto para leitores de tela. |
| 4.1.2 Nome, função, valor | OK: botão de menu com `aria-expanded`/`aria-controls`; página atual com `aria-current`. |

## Desempenho: o que foi corrigido

- **Salto de layout no celular (CLS 0,14 → 0,02).** O menu aparecia aberto e
  só fechava quando `navigation.js` rodava, empurrando o conteúdo. A classe
  `has-js` agora é aplicada por um script de uma linha no `<head>`, antes da
  primeira pintura.
- **Meta description.** As páginas não tinham; agora usam a descrição de busca
  da página do Wagtail ou um texto padrão da igreja.

## Pendências não bloqueantes

- Fontes DM Serif Display em `.ttf` (sem subconjunto). Converter para `woff2`
  com subconjunto latino reduziria algumas dezenas de KiB por fonte (o `.ttf` regular tem 69 KiB) e o pequeno salto de fonte da home.
- A imagem da home (quadros do mural) pode ganhar `srcset`/tamanhos menores
  quando houver fotos reais maiores que as do seed.
- O menu móvel depende de JavaScript para abrir; se `navigation.js` falhar ao
  carregar, a navegação fica oculta. O script é local e pequeno, então o risco
  é baixo.
- Área privada fora do escopo desta rodada, como a issue define.
- Repetir o Lighthouse no domínio de produção depois do go-live (#40), porque
  latência real e HTTP/2 do Caddy mudam os números.
