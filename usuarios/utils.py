def usuario_e_admin(user):
    return (
        user.is_authenticated
        and user.tipo_usuario
        and user.tipo_usuario.perfil.lower() == "administrador"
    )


def usuario_e_estudante(user):
    return (
        user.is_authenticated
        and user.tipo_usuario
        and user.tipo_usuario.perfil.lower() == "estudante"
    )


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


def calcular_taxa_acerto(total_acertos, total_questoes):
    if total_questoes <= 0:
        return 0

    return round((total_acertos / total_questoes) * 100, 1)


def calcular_resumo_tentativas_quiz(tentativas):
    total_quizzes = tentativas.count()
    total_acertos = sum(t.quantidade_acertos for t in tentativas)
    total_erros = sum(t.quantidade_erros for t in tentativas)
    total_questoes = total_acertos + total_erros
    xp_total = sum(t.pontuacao for t in tentativas)

    taxa_acerto = calcular_taxa_acerto(
        total_acertos=total_acertos,
        total_questoes=total_questoes,
    )

    progresso_nivel = calcular_progresso_nivel(xp_total)

    return {
        "total_quizzes": total_quizzes,
        "total_acertos": total_acertos,
        "total_erros": total_erros,
        "total_questoes": total_questoes,
        "xp_total": xp_total,
        "taxa_acerto": taxa_acerto,
        "progresso_nivel": progresso_nivel,
    }


def montar_desempenho_por_area(desempenho_por_area_qs):
    labels_area = [
        item["quiz__disciplina__nome"]
        for item in desempenho_por_area_qs
    ]

    dados_area = [
        round(item["media_acerto"], 1)
        for item in desempenho_por_area_qs
    ]

    desempenho_detalhado = [
        {
            "disciplina": item["quiz__disciplina__nome"],
            "media_acerto": round(item["media_acerto"], 1),
        }
        for item in desempenho_por_area_qs
    ]

    melhor_area = None
    pior_area = None

    if desempenho_detalhado:
        melhor_area = max(
            desempenho_detalhado,
            key=lambda item: item["media_acerto"]
        )

        pior_area = min(
            desempenho_detalhado,
            key=lambda item: item["media_acerto"]
        )

    return {
        "labels_area": labels_area,
        "dados_area": dados_area,
        "desempenho_detalhado": desempenho_detalhado,
        "melhor_area": melhor_area,
        "pior_area": pior_area,
    }


def adicionar_posicoes_ranking(ranking, usuario_id):
    ranking = list(ranking)
    minha_posicao = None

    for posicao, item in enumerate(ranking, start=1):
        total_questoes = item["total_acertos"] + item["total_erros"]

        taxa_acerto = calcular_taxa_acerto(
            total_acertos=item["total_acertos"],
            total_questoes=total_questoes,
        )

        item["posicao"] = posicao
        item["taxa_acerto"] = taxa_acerto

        if item["usuario__id"] == usuario_id:
            minha_posicao = item

    top_3 = [
        item for item in ranking
        if item["posicao"] <= 3
    ]

    ranking_restante = [
        item for item in ranking
        if item["posicao"] > 3
    ]

    return {
        "ranking": ranking,
        "top_3": top_3,
        "ranking_restante": ranking_restante,
        "minha_posicao": minha_posicao,
    }