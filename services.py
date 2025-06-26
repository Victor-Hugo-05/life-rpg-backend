from flask import jsonify

def calculate_level_and_next(xp):
    """
    Calcula o nível atual e a quantidade de XP necessária para o próximo nível.

    Args:
        xp (int): XP atual do personagem.

    Returns:
        tuple: (nível atual, XP necessário para o próximo nível, XP restante até o próximo nível)
    """
    LEVEL_THRESHOLDS = [
        0, 100, 250, 450, 700, 1000, 1400, 1900, 2500, 3200,
        4000, 4900, 5900, 7000, 8200, 9500, 10900, 12400, 14000, 15700
    ]

    level = 1
    for i, threshold in enumerate(LEVEL_THRESHOLDS):
        if xp >= threshold:
            level = i + 1
        else:
            break

    if level < len(LEVEL_THRESHOLDS):
        next_threshold = LEVEL_THRESHOLDS[level]
        xp_to_next = next_threshold - xp
    else:
        next_threshold = None
        xp_to_next = 0  # já está no nível máximo

    return level, next_threshold, xp_to_next

def _build_cors_preflight_response():
    """
    Gera uma resposta de pré-flight CORS para requisições OPTIONS.

    Returns:
        Response: Resposta Flask com os headers CORS apropriados.
    """
    response = jsonify({"message": "Preflight accepted"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
    return response

def get_xp_by_difficulty(difficulty):
    """
    Retorna o XP correspondente à dificuldade da missão.

    Args:
        difficulty (str): Dificuldade da missão ('Fácil', 'Médio', 'Difícil').

    Returns:
        int: XP correspondente.
    """
    xp_values = {
        "Fácil": 30,
        "Médio": 50,
        "Difícil": 70
    }
    return xp_values.get(difficulty, 30)
