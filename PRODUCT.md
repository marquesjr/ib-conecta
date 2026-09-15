# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Dois públicos em par.

**Visitante ou buscador**, muitas vezes no celular, em Santa Leopoldina ou na zona rural, quer saber se é bem-vindo, quando é o culto, como chegar e como falar com a igreja.

**Membro ou liderança autenticados** (líder de ministério, comunicação, pastor, tesouraria, comissão de eventos, administração) usam a área privada para escalas, documentos, eventos, retiros, coletânea de louvores e playlists — sem tornar isso público.

Quem opera o CMS (comunicação, pastor, administração) publica o conteúdo da igreja; não é o usuário primário da experiência, e sim quem alimenta o portal.

## Product Purpose

O IB Conecta é o portal de comunicação, evangelização e gestão da Igreja Batista em Santa Leopoldina. Existe para que quem chega de fora encontre o culto e um canal humano, e para que a igreja opere o necessário (inscrições, escalas, documentos, louvor) num só lugar autenticado.

Sucesso público: o visitante chega ao próximo culto, ao endereço/referências e ao WhatsApp institucional em poucos toques, mesmo com conexão limitada. Sucesso interno: o membro autenticado encontra só o que o seu perfil libera, e a liderança publica e opera sem vazar conteúdo pastoral no site.

## Positioning

O produto acolhe quem chega de fora — zona rural, celular, conexão limitada — até o culto e o WhatsApp pastoral. A gestão interna existe na medida do necessário para a igreja funcionar; não é a reivindicação que um site genérico de igreja ou um grupo de WhatsApp poderia copiar com verdade.

## Operating Context

- Instituição: Igreja Batista em Santa Leopoldina (ES). Domínio canônico: `https://www.ibsantaleopoldina.com.br`.
- Canal pastoral permanente: WhatsApp institucional (número e mensagem configuráveis no admin). Não é plantão 24 horas.
- Ofertas: chave PIX da igreja, exibida publicamente. O portal não processa cartão nem armazena dados bancários de terceiros.
- Sermões e transmissão: URL externa (YouTube) incorporada; o portal não hospeda o vídeo.
- Conteúdo institucional, notícias, agenda, sermões e ao vivo saem do CMS Wagtail; rascunhos não são públicos até a publicação.
- Visita: horários, endereço, referências, mapa externo leve, acessibilidade física e transporte/carona para a zona rural — tudo configurável, sem hardcode.
- Área privada no celular: confirmação/recusa de escala, impressão A4, `.ics`, QR Code de referências de louvor (`/r/<token>/`), WhatsApp apontando para URL que continua exigindo login.
- Operação local: Django + Wagtail + PostgreSQL via Docker Compose; S3 de backups pode ser emulado com LocalStack (`scripts/deploy-local.bat`). Produção na AWS (`t4g.small` em Ohio, Caddy/HTTPS em `https://www.ibsantaleopoldina.com.br`, S3 só para backups criptografados com age — `docs/backup.md`). Fatias restantes do go-live (monitoramento, LGPD, treinamento) estão no épico #17.

## Capabilities and Constraints

Confirmado no produto:

- Superfícies públicas: home evangelística, Planeje sua visita, pedido de oração, Quero conhecer, contribuições PIX, notícias, agenda com inscrição, sermões, ao vivo.
- Pedidos de oração e contatos de Quero conhecer ficam na área da conta (pastor/comunicação); o conteúdo do pedido não é publicado.
- Área privada: biblioteca de documentos por perfil, ministérios e escalas mensais, comissão de eventos, check-in de retiro, coletânea de louvores, playlists semanais.
- Papéis: membro, líder de ministério, comunicação, pastor, tesouraria, comissão de eventos, administrador. 2FA para administradores. Ações sensíveis geram auditoria sem gravar senhas ou conteúdo pastoral.
- Retiros: inscrição familiar, dados médicos e de menores com descarte após prazo (`discard_retreat_sensitive_data`).
- Coletânea: não armazena material sem autorização de uso; referências externas saem impressas como QR para URL interna estável.
- Idioma da interface: português (`pt-BR`).
- Nenhum vídeo inicia automaticamente.
- Peso das páginas públicas: o visual rico tem precedência sobre a leveza, por decisão explícita do responsável pelo produto, e vale igual em qualquer aparelho. A home carrega o acervo fotográfico da congregação (doze quadros) porque a fotografia *é* a página nesta direção — ver `DESIGN.md`. O custo aceito é celular mais pesado e primeira carga mais lenta em conexão limitada. Isto substitui a regra anterior de manter as páginas públicas leves; se a leveza voltar a ser prioridade, é o desenho que muda, não só a compressão das imagens.

Aberto:

- Padrão formal de acessibilidade digital (WCAG 2.2 AA aparece na issue #17; não foi assumido como requisito de produto neste registro).
- Ambiente de produção ainda não é a fonte da verdade do conteúdo real da igreja.

## Brand Commitments

- Nome do produto: **IB Conecta**. Nome da instituição: **Igreja Batista em Santa Leopoldina**. Não substituir por nomes de trabalho descartados.
- Voz já no produto: acolhedora e pastoral, convite ao culto e à conversa, sem prometer atendimento 24h nem espetáculo.
- Código: MIT. Conteúdos e mídias da igreja permanecem com seus respectivos direitos.
- Administração edita WhatsApp, PIX, redes, horários, endereço e próximo culto no Wagtail; o código não é a fonte desses fatos.

## Evidence on Hand

- Copy e dados de culto/endereço/PIX/WhatsApp são configuráveis; os defaults do código e os fixtures de teste não são prova da igreja real.
- Não há no repositório logo oficial, fotos de culto, depoimentos, números de frequência, imprensa ou casos reais. Trabalho futuro não deve fabricar testemunhos, horários, endereço, chave PIX ou conteúdo pastoral.
- Páginas institucionais (história, crenças, ministérios, liderança) nascem com texto-semente para a igreja substituir no CMS.

## Product Principles

1. Primeiro o visitante no celular: culto, caminho e conversa humana, mesmo com rede ruim.
2. Público e privado em par — a vitrine não expõe a operação; a operação não compete com o acolhimento.
3. Gestão interna só o necessário para a igreja funcionar de verdade.
4. Leveza é restrição de produto, não polish: sem autoplay, sem mídia pesada hospedada aqui.
5. A igreja fala com a própria voz pelo CMS; o portal não inventa prova.
