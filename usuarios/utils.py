def calcular_progresso_nivel(xp_total):
    nivel_atual = 1
    xp_inicio_nivel = 0
    xp_necessario_nivel = 100

    while xp_total >= xp_inicio_nivel + xp_necessario_nivel:
        xp_inicio_nivel += xp_necessario_nivel
        nivel_atual += 1
        xp_necessario_nivel += 100

    xp_no_nivel = xp_total - xp_inicio_nivel
    xp_para_proximo_nivel = xp_necessario_nivel
    xp_faltante = xp_para_proximo_nivel - xp_no_nivel

    percentual_nivel = 0
    if xp_para_proximo_nivel > 0:
        percentual_nivel = round((xp_no_nivel / xp_para_proximo_nivel) * 100, 1)

    return {
        "nivel_atual": nivel_atual,
        "xp_total": xp_total,
        "xp_inicio_nivel": xp_inicio_nivel,
        "xp_no_nivel": xp_no_nivel,
        "xp_para_proximo_nivel": xp_para_proximo_nivel,
        "xp_faltante": xp_faltante,
        "percentual_nivel": percentual_nivel,
    }