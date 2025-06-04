def calculate_level_and_next(xp):
    
    # Constante com os thresholds de XP para cada nível
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
