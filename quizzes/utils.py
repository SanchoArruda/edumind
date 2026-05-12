from datetime import timedelta

from .models import Alternativa

from django.db.models import Case, IntegerField, When


def calcular_xp_tentativa(quantidade_acertos):
    return quantidade_acertos * 5


def calcular_percentual_acertos(quantidade_acertos, total_questoes):
    if total_questoes <= 0:
        return 0

    return round((quantidade_acertos / total_questoes) * 100, 2)


def obter_mensagem_resultado_quiz(percentual_acertos):
    if percentual_acertos == 100:
        return "Excelente desempenho!"

    if percentual_acertos >= 70:
        return "Muito bem! Continue assim!"

    if percentual_acertos >= 40:
        return "Bom esforço! Continue praticando!"

    return "Continue praticando!"


def obter_emoji_resultado_quiz(percentual_acertos):
    if percentual_acertos == 100:
        return "🏆"

    if percentual_acertos >= 70:
        return "🎉"

    if percentual_acertos >= 40:
        return "👏"

    return "💪"


def corrigir_respostas_quiz(questoes, post_data):
    quantidade_acertos = 0
    quantidade_erros = 0
    respostas_usuario = {}

    for questao in questoes:
        alternativa_id = post_data.get(f"questao_{questao.id}")

        if alternativa_id:
            respostas_usuario[str(questao.id)] = int(alternativa_id)

            alternativa = Alternativa.objects.filter(
                id=alternativa_id,
                questao=questao
            ).first()

            if alternativa and alternativa.correta:
                quantidade_acertos += 1
            else:
                quantidade_erros += 1
        else:
            quantidade_erros += 1

    return {
        "quantidade_acertos": quantidade_acertos,
        "quantidade_erros": quantidade_erros,
        "respostas_usuario": respostas_usuario,
    }


def finalizar_tentativa_quiz(tentativa, questoes, post_data):
    total_questoes = questoes.count()

    resultado = corrigir_respostas_quiz(
        questoes=questoes,
        post_data=post_data,
    )

    quantidade_acertos = resultado["quantidade_acertos"]
    quantidade_erros = resultado["quantidade_erros"]
    respostas_usuario = resultado["respostas_usuario"]

    percentual_acertos = calcular_percentual_acertos(
        quantidade_acertos=quantidade_acertos,
        total_questoes=total_questoes,
    )

    pontuacao = calcular_xp_tentativa(quantidade_acertos)

    desempenho_geral = obter_mensagem_resultado_quiz(percentual_acertos)

    tempo_gasto_segundos = int(
        post_data.get("tempo_gasto_segundos", 0) or 0
    )

    tentativa.respostas = respostas_usuario
    tentativa.pontuacao = pontuacao
    tentativa.quantidade_acertos = quantidade_acertos
    tentativa.quantidade_erros = quantidade_erros
    tentativa.percentual_acertos = percentual_acertos
    tentativa.desempenho_geral = desempenho_geral
    tentativa.tempo_gasto = timedelta(seconds=tempo_gasto_segundos)
    tentativa.concluida = True
    tentativa.aprovado = False
    tentativa.save()

    return tentativa


def montar_revisao_quiz(questoes, respostas_usuario):
    revisao_questoes = []

    for indice, questao in enumerate(questoes, start=1):
        alternativas = list(questao.alternativas.all())
        alternativa_correta = next(
            (alternativa for alternativa in alternativas if alternativa.correta),
            None
        )

        alternativa_marcada_id = respostas_usuario.get(str(questao.id))

        acertou = False

        if alternativa_correta and alternativa_marcada_id:
            acertou = str(alternativa_correta.id) == str(alternativa_marcada_id)

        revisao_questoes.append({
            "numero": indice,
            "questao": questao,
            "alternativas": alternativas,
            "alternativa_correta_id": str(alternativa_correta.id) if alternativa_correta else None,
            "alternativa_marcada_id": str(alternativa_marcada_id) if alternativa_marcada_id else None,
            "acertou": acertou,
            "explicacao": questao.explicacao_resposta,
        })

    return revisao_questoes


def obter_questoes_ordenadas_da_tentativa(request, tentativa):
    chave_sessao = f"tentativa_{tentativa.id}_questoes"

    questoes_ids = request.session.get(chave_sessao)

    if not questoes_ids:
        questoes_ids = list(
            tentativa.quiz.questoes.values_list("id", flat=True)
        )

    ordenacao = Case(
        *[
            When(id=questao_id, then=posicao)
            for posicao, questao_id in enumerate(questoes_ids)
        ],
        output_field=IntegerField()
    )

    return tentativa.quiz.questoes.filter(
        id__in=questoes_ids
    ).prefetch_related(
        "alternativas"
    ).order_by(ordenacao)