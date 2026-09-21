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
    'Para qualquer suspeita ou ocorrência de maus-tratos, garanta a segurança do animal e do local. '
    'Procure assistência veterinária emergencial e acione os órgãos competentes (Polícia Ambiental / Zoonoses / 190).'
)


def obter_orientacao_imediata(nivel_urgencia: str, tipo_denuncia: str = None) -> str:
    """Retorna a orientação imediata correspondente ao nível de urgência informado."""
    if not nivel_urgencia:
        return ORIENTACAO_PADRAO
    return ORIENTACOES_URGENCIA.get(nivel_urgencia.strip(), ORIENTACAO_PADRAO)
