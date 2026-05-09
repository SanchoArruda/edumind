from datetime import timedelta

from quizzes.models import Alternativa


def calcular_estrelas_desafio(percentual_acertos):
    if percentual_acertos == 0:
        return 0

    if percentual_acertos >= 80:
        return 5

    if percentual_acertos >= 60:
        return 4

    if percentual_acertos >= 40:
        return 3

    if percentual_acertos >= 20:
        return 2

    return 1


def obter_mensagem_desafio(estrelas):
    if estrelas == 5:
        return "Excelente desempenho!"

    if estrelas == 4:
        return "Muito bem!"

    if estrelas == 3:
        return "Bom esforço!"

    if estrelas == 2:
        return "Você está evoluindo!"

    return "Continue treinando!"


def obter_emoji_desafio(estrelas):
    if estrelas == 5:
        return "🏆"

    if estrelas == 4:
        return "🎉"

    if estrelas == 3:
        return "💪"

    return "📚"


def calcular_percentual_desafio(quantidade_acertos, total_questoes):
    if total_questoes <= 0:
        return 0

    return round((quantidade_acertos / total_questoes) * 100, 2)


def corrigir_respostas_desafio(questoes, post_data):
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


def finalizar_tentativa_desafio(tentativa, questoes, post_data):
    total_questoes = questoes.count()

    resultado = corrigir_respostas_desafio(
        questoes=questoes,
        post_data=post_data,
    )

    quantidade_acertos = resultado["quantidade_acertos"]
    quantidade_erros = resultado["quantidade_erros"]
    respostas_usuario = resultado["respostas_usuario"]

    percentual_acertos = calcular_percentual_desafio(
        quantidade_acertos=quantidade_acertos,
        total_questoes=total_questoes,
    )

    estrelas = calcular_estrelas_desafio(percentual_acertos)
    desempenho_geral = obter_mensagem_desafio(estrelas)
    aprovado = estrelas >= 4

    tempo_gasto_segundos = int(
        post_data.get("tempo_gasto_segundos", 0) or 0
    )

    tentativa.respostas = respostas_usuario
    tentativa.pontuacao = estrelas
    tentativa.quantidade_acertos = quantidade_acertos
    tentativa.quantidade_erros = quantidade_erros
    tentativa.percentual_acertos = percentual_acertos
    tentativa.desempenho_geral = desempenho_geral
    tentativa.tempo_gasto = timedelta(seconds=tempo_gasto_segundos)
    tentativa.concluida = True
    tentativa.aprovado = aprovado
    tentativa.save()

    return tentativa


def montar_revisao_desafio(questoes, respostas_usuario):
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