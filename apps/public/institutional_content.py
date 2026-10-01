"""Texto inicial das páginas institucionais, em HTML de rich text do Wagtail.

Síntese do que as igrejas batistas brasileiras publicam sobre si (ver
``docs/institucional-pesquisa.md``). Só traz o que é comum aos batistas: história do
movimento, a Declaração Doutrinária da Convenção Batista Brasileira, o modo batista de
se organizar e o propósito que as igrejas declaram. Fatos próprios desta igreja
(fundação, nomes, ministérios) não estão aqui: a igreja os acrescenta pelo CMS.
"""

HISTORIA = """
<h2>De onde vêm os batistas</h2>
<p>Os batistas surgiram na Europa do início do século XVII, entre cristãos que buscavam viver a fé segundo as Escrituras, com liberdade de consciência. Em 1609, em Amsterdã, o pregador John Smyth e o advogado Thomas Helwys organizaram uma igreja que praticava o batismo de quem professa a fé em Jesus Cristo. Em 1612, Helwys voltou à Inglaterra e fundou uma igreja em Londres. Ele defendeu por escrito que a religião de cada pessoa é assunto entre ela e Deus, e que o Estado não deve punir ninguém por causa da fé.</p>
<p>O movimento chegou à América do Norte no século XVII (a igreja de Providence, em 1639, é uma das primeiras) e cresceu com o trabalho missionário.</p>

<h2>Os batistas no Brasil</h2>
<p>Em 31 de agosto de 1882, os missionários norte-americanos William Buck Bagby e Zachary Clay Taylor chegaram a Salvador. Em 15 de outubro daquele ano organizaram a primeira igreja batista do Brasil, com cinco membros. A Convenção Batista Brasileira foi fundada em 22 de junho de 1907, também em Salvador, para articular missões, educação religiosa e publicações. Hoje as igrejas batistas estão em todo o país.</p>

<h2>Nossa igreja</h2>
<p>A Igreja Batista em Santa Leopoldina faz parte dessa história: uma comunidade local que se reúne para adorar a Deus, estudar a Bíblia e servir ao próximo.</p>
"""

CRENCAS = """
<p>Os batistas brasileiros resumem sua fé na Declaração Doutrinária da Convenção Batista Brasileira. Estes são os pontos centrais.</p>

<h2>A Bíblia</h2>
<p>A Bíblia é a Palavra de Deus em linguagem humana, escrita por pessoas inspiradas pelo Espírito Santo. É a única regra de fé e de conduta, e deve ser lida à luz de Jesus Cristo.</p>

<h2>Deus</h2>
<p>Há um só Deus, vivo e verdadeiro, eterno e infinito, que se revela como Pai, Filho e Espírito Santo. Ele é o criador e sustentador de todas as coisas.</p>

<h2>A pessoa humana e o pecado</h2>
<p>Todo ser humano foi criado à imagem de Deus e tem valor e dignidade. Pela desobediência, todos se tornaram pecadores, separados de Deus e incapazes de salvar a si mesmos.</p>

<h2>Salvação</h2>
<p>A salvação é dom de Deus, concedido pela graça, mediante o arrependimento e a fé em Jesus Cristo, o único Salvador, que morreu por nossos pecados e ressuscitou.</p>

<h2>A igreja</h2>
<p>A igreja local é uma comunidade de pessoas que creram em Cristo e foram batizadas. É autônoma e democrática: as decisões são tomadas em assembleia, sob a autoridade de Cristo e da sua Palavra.</p>

<h2>Batismo e Ceia do Senhor</h2>
<p>São as duas ordenanças da igreja. O batismo, por imersão, é feito depois da profissão de fé. A Ceia do Senhor lembra a morte de Cristo.</p>

<h2>Missão e serviço</h2>
<p>A missão do povo de Deus é anunciar o evangelho e fazer discípulos em todas as nações. Também faz parte da fé cristã cuidar de quem precisa, participar do bem comum e educar na Palavra de Deus, em casa e na igreja.</p>

<h2>Liberdade de consciência</h2>
<p>Só Deus é Senhor da consciência. Igreja e Estado são separados, e cada pessoa responde diante de Deus por suas escolhas de fé.</p>

<h2>Família, vida e futuro</h2>
<p>A família é valorizada como lugar de cuidado e de ensino da fé. Os batistas creem que Cristo voltará para julgar, que os salvos viverão com Ele para sempre e que Deus consumará o seu reino.</p>
"""

MINISTERIOS = """
<p>Na igreja, servir é parte de seguir a Jesus. Cada pessoa recebe dons de Deus para o bem de todos, e os ministérios são os lugares em que esses dons são usados.</p>

<h2>Onde é possível servir</h2>
<p>As igrejas batistas costumam organizar o serviço em torno de algumas áreas:</p>
<ul>
  <li><strong>Adoração:</strong> louvor, música e preparo dos cultos.</li>
  <li><strong>Ensino:</strong> estudo bíblico e formação de crianças, jovens e adultos.</li>
  <li><strong>Acolhimento:</strong> receber visitantes e cuidar de quem chega.</li>
  <li><strong>Cuidado e ação social:</strong> visitar, orar com as pessoas e ajudar quem passa necessidade.</li>
  <li><strong>Missões e evangelização:</strong> levar o evangelho a outras pessoas e lugares.</li>
</ul>

<h2>Quer participar?</h2>
<p>Fale com a igreja pela página <em>Quero conhecer</em>, no menu <em>Participe</em>, ou por um dos canais de contato do rodapé. Vamos conversar sobre onde os seus dons podem servir.</p>
"""

LIDERANCA = """
<p>Entre os batistas, a igreja local governa a si mesma. A autoridade final é de Cristo e da sua Palavra, e a congregação decide em assembleia, com a participação dos seus membros.</p>

<h2>Como a igreja é conduzida</h2>
<ul>
  <li><strong>Pastores:</strong> são chamados por Deus e reconhecidos pela igreja para pregar a Palavra e cuidar do rebanho.</li>
  <li><strong>Diáconos:</strong> servem a igreja no cuidado das pessoas e das necessidades práticas da comunidade.</li>
  <li><strong>Assembleia:</strong> reúne os membros para decidir sobre a vida e o trabalho da igreja.</li>
  <li><strong>Ministérios e comissões:</strong> cada área de serviço tem líderes que prestam contas à igreja.</li>
</ul>

<h2>Falar com a liderança</h2>
<p>Você pode conversar com a liderança pela página <em>Quero conhecer</em>, no menu <em>Participe</em>, ou pelo WhatsApp da igreja.</p>
"""

INSTITUTIONAL_BODIES = {
    "historia": HISTORIA,
    "crencas": CRENCAS,
    "ministerios": MINISTERIOS,
    "lideranca": LIDERANCA,
}
