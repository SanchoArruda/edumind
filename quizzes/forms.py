from django import forms
from .models import Questao, Quiz 


class QuestaoForm(forms.ModelForm):
    class Meta:
        model = Questao
        fields = [
            "disciplina",
            "tipo_prova",
            "nivel_dificuldade",
            "enunciado",
            "explicacao_resposta",
        ]

        widgets = {
            "disciplina": forms.Select(attrs={
                "class": "form-control"
            }),
            "tipo_prova": forms.Select(attrs={
                "class": "form-control"
            }),
            "nivel_dificuldade": forms.Select(attrs={
                "class": "form-control"
            }),
            "enunciado": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Digite o enunciado da questão..."
            }),
            "explicacao_resposta": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Explicação da resposta correta..."
            }),
        }

        labels = {
            "disciplina": "Área de Conhecimento / Disciplina",
            "tipo_prova": "Tipo de prova",
            "nivel_dificuldade": "Nível de dificuldade",
            "enunciado": "Enunciado",
            "explicacao_resposta": "Explicação",
        }


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = [
            "titulo",
            "descricao",
            "disciplina",
            "tipo_prova",
        ]

        widgets = {
            "titulo": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex: Quiz de Banco de Dados"
            }),
            "descricao": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Descreva o objetivo do quiz"
            }),
            "disciplina": forms.Select(attrs={
                "class": "form-control"
            }),
            "tipo_prova": forms.Select(attrs={
                "class": "form-control"
            }),
        }

        labels = {
            "titulo": "Título",
            "descricao": "Descrição",
            "disciplina": "Disciplina / Área",
            "tipo_prova": "Tipo da Prova",
        }