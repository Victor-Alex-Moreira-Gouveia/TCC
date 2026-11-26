"""
orientacoes.py — Módulo de serviço com mapa de orientações imediatas para denúncias
"""

ORIENTACOES_URGENCIA = {
    'Ferimento grave': (
        'Mantenha a calma e evite movimentos bruscos no animal para não piorar a lesão. '
        'Pressione um pano limpo levemente sobre o sangramento. '
        'Ligue imediatamente para um veterinário de plantão ou serviço de resgate animal e prepare um transporte seguro.'
    ),
    'Engasgo': (
        'Abra a boca do animal com cuidado para verificar se há objeto visível (remova apenas se for fácil alcançá-lo sem empurrar). '
        'Em pets de menor porte, mantenha a cabeça levemente inclinada para baixo. '
        'Ligue para uma clínica veterinária 24h ou leve-o imediatamente.'
    ),
    'Convulsão': (
        'Afaste móveis e objetos cortantes ao redor para evitar traumas físicos. '
        'NÃO coloque as mãos ou objetos na boca do animal. '
        'Cronometre a Duração da crise e contate um veterinário com urgência.'
    ),
    'Doença contagiosa': (
        'Isole o animal de outros pets e pessoas imediatamente para evitar contágio. '
        'Utilize luvas e proteção ao manuseá-lo. '
        'Contate a vigilância sanitária ou veterinário responsável.'
    ),
    'Envenenamento': (
        'NÃO induza o vômito por conta própria, pois substâncias corrosivas podem piorar as lesões. '
        'Guarde a embalagem ou amostra do veneno/alimento ingerido. '
        'Ligue para o atendimento veterinário emergencial imediatamente.'
    ),
    'Atropelamento': (
        'Não puxe o animal pelas patas ou cauda. '
        'Utilize uma superfície rígida ou lençol esticado como maca improvisada para movê-lo com cuidado. '
        'Acione o resgate veterinário, zoonoses ou polícia ambiental.'
    ),
    'Queimaduras ou exposição a produtos químicos': (
        'NÃO aplique pomadas, manteiga ou gelo na lesão. '
        'Se for produto químico líquido, lave com água corrente em abundância. '
        'Procure atendimento veterinário emergencial imediatamente.'
    ),
}

ORIENTACAO_PADRAO = (
    'Este site registra o relato e apresenta canais de contato. Ele não aciona serviços, '
    'não realiza resgates e não substitui atendimento profissional.'
)


def obter_orientacao_imediata(nivel_urgencia: str, tipo_denuncia: str = None) -> str:
    """Retorna a orientação imediata correspondente ao nível de urgência informado."""
    if not nivel_urgencia:
        return ORIENTACAO_PADRAO
    return ORIENTACOES_URGENCIA.get(nivel_urgencia.strip(), ORIENTACAO_PADRAO)


def obter_canal_recomendado(tipo_animal: str, situacao: str) -> dict:
    """Retorna canais oficiais de SP; a pessoa escolhe e inicia o contato."""
    animal_silvestre = tipo_animal == 'Animal Silvestre'

    if situacao == 'violencia_em_andamento':
        return {
            'titulo': 'Violência ou maus-tratos acontecendo agora',
            'descricao': 'Ligue para a Polícia Militar pelo 190. O site não realiza a ligação nem envia a denúncia.',
            'telefones': [{'rotulo': 'Ligar 190', 'numero': '190', 'href': 'tel:190'}],
            'links': [],
            'aviso': 'Se for fauna silvestre, informe que se trata de ocorrência ambiental. Não tente capturar o animal.',
        }

    if animal_silvestre and situacao in ('risco_imediato', 'animal_ferido', 'resgate'):
        return {
            'titulo': 'Fauna silvestre ferida ou em risco',
            'descricao': 'A Polícia Militar de SP orienta acionar os Bombeiros pelo 193 ou a Polícia Ambiental. Não tente resgatar ou manusear o animal.',
            'telefones': [{'rotulo': 'Ligar 193 — Bombeiros', 'numero': '193', 'href': 'tel:193'}],
            'links': [{
                'rotulo': 'Canais da Polícia Ambiental de SP',
                'href': 'https://www.policiamilitar.sp.gov.br/unidades/ambiental/faq.html',
            }],
            'aviso': 'O município e a situação podem determinar a unidade responsável. O 193 é uma orientação de acionamento, não uma ambulância veterinária.',
        }

    if situacao in ('risco_imediato', 'animal_ferido'):
        return {
            'titulo': 'Atendimento veterinário urgente',
            'descricao': 'Procure diretamente um hospital ou serviço veterinário de urgência da sua região. São Paulo não tem um telefone estadual único de ambulância veterinária.',
            'telefones': [],
            'links': [],
            'aviso': 'Se a situação envolver violência acontecendo neste momento, ligue também para 190. O site não aciona serviços.',
        }

    if tipo_animal == 'Resgate e acolhimento' or situacao == 'resgate':
        return {
            'titulo': 'Resgate e acolhimento na sua região',
            'descricao': 'Procure o serviço municipal de proteção animal ou centro de zoonoses do município onde o animal está.',
            'telefones': [],
            'links': [],
            'aviso': 'Os contatos variam por município. Este site não possui uma central de resgate e não aciona equipes.',
        }

    if animal_silvestre:
        return {
            'titulo': 'Relato ambiental não emergencial',
            'descricao': 'Registre a ocorrência pelos canais da Polícia Ambiental de SP. A Linha Verde do IBAMA recebe denúncias e informações em dias úteis, das 7h às 19h.',
            'telefones': [{'rotulo': 'IBAMA — Linha Verde (dias úteis, 7h–19h)', 'numero': '0800 061 8080', 'href': 'tel:08000618080'}],
            'links': [
                {'rotulo': 'Denúncia Ambiental de SP', 'href': 'https://denuncia.sigam.sp.gov.br/'},
                {'rotulo': 'Orientações da Polícia Ambiental', 'href': 'https://www.policiamilitar.sp.gov.br/unidades/ambiental/denuncie.html'},
            ],
            'aviso': 'A Linha Verde não é serviço de emergência ou resgate imediato.',
        }

    return {
        'titulo': 'Denúncia não emergencial de maus-tratos',
        'descricao': 'Use o portal oficial da Delegacia Eletrônica de Proteção Animal (DEPA). Para contato telefônico, a SEMIL lista a divisão policial especializada.',
        'telefones': [
            {'rotulo': 'Divisão de Maus-Tratos a Animais', 'numero': '(11) 3338-0155', 'href': 'tel:+551133380155'},
            {'rotulo': 'Divisão de Maus-Tratos a Animais', 'numero': '(11) 3338-1380', 'href': 'tel:+551133381380'},
        ],
        'links': [
            {'rotulo': 'Abrir portal oficial DEPA', 'href': 'https://www.webdenuncia.sp.gov.br/depa/'},
            {'rotulo': 'Conferir contatos na SEMIL', 'href': 'https://semil.sp.gov.br/duvidas-frequentes/'},
        ],
        'aviso': 'A denúncia registrada neste site permanece apenas no sistema e não é enviada à DEPA nem gera protocolo oficial.',
    }
