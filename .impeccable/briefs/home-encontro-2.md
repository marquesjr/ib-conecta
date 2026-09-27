# Proposta: Encontro 2 — homepage com o acervo real do Instagram

Status: **aprovada e implementada** em 27/09/2026. Evolui o Editorial acolhedor aprovado em 16/09/2026; não troca identidade, paleta nem tipografia.

Referências visuais:

- Estado atual: `.impeccable/mocks/atual-2026-09-27-desktop.jpg` e `-celular.jpg` (seed de demonstração + as 9 fotos do Instagram).
- Proposta: `.impeccable/mocks/comp-encontro-2-desktop.jpg` e `-celular.jpg`; maquete HTML em `.impeccable/mocks/encontro-2/index.html`.

## Diagnóstico do design atual

O sistema (serifada, vinho, faixa de visita, listas editoriais) funciona. O que quebrou foi o encontro entre o layout e o acervo real: o desenho supunha fotografias, e o Instagram da igreja é na maior parte **artes com texto**.

Das 9 publicações importadas, 3 são fotografia (Consagração, Missões, Pedra Malha), 1 é foto com texto sobreposto (Dia dos Pais) e 5 são cartazes (27 anos, 139 anos, Sexta-feira Santa, Casais, Mutirão).

1. **Abertura com cartaz recortado.** A foto de abertura é sempre a publicação mais recente — hoje o cartaz dos 27 anos. O `object-fit: cover` corta o título ("IGREJA BATISTA EM" some) e o cartaz compete com a headline. A abertura deixou de mostrar pessoas.
2. **Galeria corta textos.** "Parabén… Leopoldina 139 a", "…LIMPEZA… DA VITÓR", "liz Dia dos Pa": recortes de cartaz parecem erro, não editorial.
3. **Resolução.** Os arquivos têm 640×640. A abertura ocupa ~730px de largura (≈1460px em tela retina) e a primeira foto da galeria ~870px: ficam borradas.
4. **Acervo misturado.** Com 9 quadros reais e 12 vagas, entram 3 imagens ilustrativas no fim da grade, e o aviso "as imagens de exemplo são ilustrativas" aparece sobre uma galeria quase toda real. A última linha fica com um quadro só.
5. **Legendas ruidosas.** Cada quadro repete "Instagram @igrejabatista.santaleopoldina" (o link já está no título da seção) e os meses saíam em inglês ("aug 2026"). No celular a legenda ocupa até cinco linhas por foto de 2 colunas.
6. **Logo em caixa branca.** O PNG tem fundo branco sobre o fundo morno `#faf9f6`: aparece como um adesivo retangular.
7. **Detalhes de navegação.** O `<summary>` de "Conheça a igreja" mostra o triângulo padrão do navegador (▶), destoando dos demais links.
8. **Agenda sem o que o visitante procura.** "27.09 Culto de celebração" não diz dia da semana nem horário.
9. **Faixa de visita.** Endereço sem link de mapa e sem acesso direto ao WhatsApp, embora `map_url` e o WhatsApp existam no CMS.
10. **Versículo três vezes** na primeira tela e rodapé (logo, abertura, rodapé).

## Proposta

1. **Separar fotografia de arte.** Novo campo em Quadro do acervo: `tipo` = Fotografia | Arte/cartaz (a comunicação marca no CMS; a importação pode sugerir). Adicionar `destaque` para escolher a foto da abertura.
2. **Abertura = fotografia real em destaque**, em retrato 4:5 com no máximo 32rem de largura (perto da resolução do arquivo) e legenda fora da imagem. Sem destaque, usa a fotografia mais recente; cartaz nunca abre a página. No celular a foto vem antes do título (4:3), e os botões continuam na primeira tela.
3. **Mural da igreja** (novo): cartazes inteiros, quadrados, `object-fit: contain`, em faixa horizontal com scroll-snap. Legenda curta + mês. O link do Instagram fica só no título da seção.
4. **A vida em comunidade** só com fotografias: mosaico 1 grande + menores, legenda sobreposta curta. Se faltarem fotos, um cartão convida a enviar fotos à comunicação (com autorização de quem aparece) em vez de completar com imagem ilustrativa. Ilustrativas só quando não há nenhuma foto real.
5. **Faixa de visita com três respostas e três ações:** quando (→ horários), onde (→ mapa, `map_url`), primeira vez (→ WhatsApp).
6. **Agenda e sermões com data empilhada**: dia em serifada, dia da semana e mês; linha secundária com horário e local.
7. **Logo** com `mix-blend-mode: multiply` até a igreja fornecer versão com fundo transparente/vetorial. Remover o versículo repetido da abertura (já está na logo e no rodapé).
8. **Chevron SVG** no lugar do triângulo do `<summary>`.
9. **Pedir à comunicação os originais** das fotos (≥1600px). O Instagram entrega 640px; a abertura precisa de mais.

Já corrigido junto com esta proposta: mês das legendas em português (`apps/public/archive.py`).

## Implementação

- `ArchiveFrame.kind` (Fotografia | Arte ou cartaz) e `ArchiveFrame.featured`; migração 0014 marca os cinco cartazes importados em 0012.
- `apps/public/archive.home_archive()` divide abertura, mosaico e mural. O limite configurado dá a vez às fotografias primeiro.
- Versículo removido da abertura (fica na logo e no rodapé). Item 9 (originais em alta) depende da comunicação.

## Fora do escopo

Paleta, fontes, páginas internas e área privada seguem como estão. Nenhum horário, endereço ou texto novo é afirmado como fato: os da maquete vêm do seed de demonstração.
