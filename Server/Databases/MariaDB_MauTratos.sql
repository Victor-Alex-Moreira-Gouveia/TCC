CREATE DATABASE IF NOT EXISTS MausTratosDB;
USE MausTratosDB;

-- Tabela de usuários
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome_usuario VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela Noticias
CREATE TABLE noticias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    corpo TEXT NOT NULL,
    imagem_url VARCHAR(500) NULL,
    data_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela Ajuda (Denúncias)
CREATE TABLE ajuda (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    corpo TEXT NOT NULL,
    tipo_denuncia VARCHAR(80) NOT NULL DEFAULT 'Animal doméstico',
    nivel_urgencia VARCHAR(80) NOT NULL DEFAULT 'Não informado',
    autor VARCHAR(150) NOT NULL DEFAULT 'anon'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela de Comentários em Notícias
CREATE TABLE comentarios_noticias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    noticia_id INT NOT NULL,
    usuario_id INT NOT NULL,
    autor_nome VARCHAR(150) NOT NULL,
    texto TEXT NOT NULL,
    data_criacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (noticia_id) REFERENCES noticias(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela de Curtidas em Notícias (1 curtida por usuário por notícia)
CREATE TABLE curtidas_noticias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    noticia_id INT NOT NULL,
    usuario_id INT NOT NULL,
    data_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_noticia_usuario (noticia_id, usuario_id),
    FOREIGN KEY (noticia_id) REFERENCES noticias(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Carga inicial de notícias pré-cadastradas
INSERT INTO noticias (titulo, corpo, imagem_url, data_hora) VALUES
('Mais de 100 animais são resgatados em situação de maus-tratos na Grande SP', 'Mais de 100 animais foram resgatados de uma situação de maus-tratos em um sítio localizado em Mairiporã, na Grande São Paulo.\n\nA ação teve início após uma denúncia registrada em boletim de ocorrência. Policiais da 3ª Delegacia de Crimes contra Animais (Diima) cumpriram mandados de busca e apreensão no local.\n\nAo todo, foram encontrados 125 animais, sendo 60 cães, 55 gatos e 10 porcos. O responsável pelo local é investigado por não prestar os cuidados necessários aos animais.', '/static/img_posts/Imagem1.jpg', '2025-08-26 10:00:00'),
('\'Serial killer\' de gatos: homem é preso por suspeita de maus-tratos a animais em São Paulo', 'Um homem foi preso em Francisco Morato por maus-tratos a 18 animais, ameaça a pessoas e crime ambiental após denúncias de moradores e familiares.\n\nGuardas civis foram até o imóvel e encontraram 18 animais (13 gatos e 5 cães) em estado crítico, além de quatro gatos mortos e restos de animais enterrados.\n\nOs animais vivos foram encaminhados para atendimento veterinário. A polícia solicitou perícia no local e pediu a conversão da prisão em flagrante para preventiva.', '/static/img_posts/Imagem2.png', '2025-08-21 10:00:00'),
('Caso Cão Orelha: agressão a cachorro comunitário mobiliza investigação em Florianópolis', 'Na madrugada entre 3 e 4 de janeiro, o cão comunitário Orelha foi vítima de maus-tratos no bairro Praia Brava, em Florianópolis (SC).\n\nEncontrado por moradores em uma área de mata com graves ferimentos na cabeça, o cão foi socorrido, mas precisou ser submetido à eutanásia devido à severidade das lesões.\n\nO caso ganhou repercussão nacional. Mandados de busca e apreensão foram cumpridos contra suspeitos e pessoas indiciadas por coação de testemunhas.', '/static/img_posts/Imagem3.jpg', '2026-01-26 10:00:00'),
('Tutor que cortou patas de cavalo em Bananal é investigado pela Polícia Civil', 'A morte de um cavalo branco em Bananal, no interior de SP, gerou revolta nacional após imagens mostrarem o animal mutilado com um facão durante uma cavalgada.\n\nO tutor de 21 anos prestou depoimento e alegou acreditar que o equino já estivesse morto ao golpeá-lo, versão contestada por testemunhas.\n\nA Polícia Civil de São Paulo abriu inquérito para apurar as circunstâncias e responsabilidades pelo crime de maus-tratos.', '/static/img_posts/Imagem5.jpg', '2025-08-18 10:00:00'),
('China: Advogado de Xangai é acusado de torturar e matar milhares de gatos para vídeos online', 'Um caso chocante de crueldade contra animais veio à tona em Xangai, onde um advogado local é acusado de torturar e matar felinos desde 2017 para comercializar vídeos na internet.\n\nA descoberta ocorreu após flagrante em um estacionamento subterrâneo por voluntários de proteção animal. Análises indicam mais de 300 vídeos produzidos e cerca de 4.000 gatos vitimados.\n\nOrganizações internacionais e protetores locais cobram punições severas e endurecimento das leis de proteção animal no país.', '/static/img_posts/Imagem6.jpg', '2025-09-26 10:00:00'),
('PRF resgata dois bezerros em situação de maus-tratos na BR-116 na Bahia', 'Dois bezerros foram resgatados pela Polícia Rodoviária Federal (PRF) em ação conjunta com a Agência de Defesa Agropecuária da Bahia (Adab) na BR-116 em Vitória da Conquista.\n\nOs animais eram transportados trancados na gaveta lateral de um caminhão boiadeiro, sem ventilação, higiene ou espaço mínimo de mobilidade.\n\nOs bezerros foram encaminhados para assistência e o motorista assinou um Termo Circunstanciado de Ocorrência (TCO) por crime de maus-tratos.', '/static/img_posts/Imagem7.jpg', '2025-08-18 11:00:00'),
('Cavalos mantidos amarrados sob sol forte e feridos geram denúncias em Santarém', 'Vídeos gravados por moradores do bairro São Cristóvão, em Santarém (PA), mostram dois cavalos mantidos amarrados e abandonados sob sol escaldante em um terreno baldio.\n\nUm dos animais apresentava ferimento visível na pata dianteira e exaustão extrema. Moradores relatam que a situação é recorrente e cobram fiscalização dos órgãos ambientais.', '/static/img_posts/Imagem8.jpg', '2025-08-15 10:00:00'),
('Homem é preso com mais de 1 mil aves silvestres no RJ; 180 morreram no transporte', 'Em uma operação conjunta na BR-040 em Petrópolis, a PRF e a Polícia Federal resgataram 1.080 pássaros silvestres trazidos de Minas Gerais para venda ilegal em feiras no Rio de Janeiro.\n\nAproximadamente 180 aves foram encontradas mortas por asfixia e amontoamento em caixas de madeira e papelão. 820 pássaros com condições de saúde foram reabilitados para soltura.', '/static/img_posts/Imagem9.jpg', '2025-09-10 10:00:00'),
('Cão negligenciado com corrente pesada recebe resgate emocionante em Minas Gerais', 'Denúncias mobilizaram a Sociedade Viçosense de Proteção aos Animais (SOVIPA) e a Polícia Ambiental em uma propriedade rural em Viçosa (MG).\n\nCães eram mantidos acorrentados entre entulhos e sujeira. O cão Ted foi resgatado debilitado e assustado, recebendo tratamento médico veterinário e acolhimento adequado.', '/static/img_posts/Imagem10.jpg', '2025-10-15 10:00:00'),
('“Zara, a mamãe esqueleto”: cadela em pele e osso usa últimas forças para amamentar no lixo em SP', 'Uma cadela com severo quadro de desnutrição foi resgatada em Itariri (SP) após um pedido de socorro mobilizar voluntários e protetores locais.\n\nMesmo sem forças, Zara se mantinha deitada sob blocos de concreto e entulho para amamentar sua ninhada recém-nascida. A família foi transferida para um centro de reabilitação e adoção.', '/static/img_posts/Imagem4.jpg', '2025-06-30 10:00:00'),
('Filhote de anta de 15 dias é resgatado com fratura na pata no interior de SP', 'Um filhote de anta de apenas 15 dias de vida foi resgatado nas proximidades de Planalto do Sul, interior paulista, apresentando fratura na pata traseira.\n\nO animal recebeu atendimento da Polícia Ambiental e da Associação Protetora dos Animais Silvestres de Assis. Assim que se recuperar, será reintroduzido ao habitat natural.', '/static/img_posts/Imagem12.jpg', '2025-09-07 10:00:00'),
('Polícia investiga maus-tratos após descoberta de animais enterrados em terreno em Adamantina', 'A Polícia Civil de Adamantina (SP) instaurou inquérito para apurar crime ambiental após encontrar corpos de animais de pequeno e grande porte enterrados em um terreno.\n\nAs buscas iniciaram a partir de vídeos gravados por moradores. Cães sobreviventes encontrados no local foram acolhidos por uma ONG parceira.', '/static/img_posts/Imagem13.jpg', '2025-10-07 10:00:00');