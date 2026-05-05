from django import forms
from .models import Desafio


class DesafioForm(forms.ModelForm):
    tempo_total_formatado = forms.CharField(
        label="Tempo disponível",
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "id": "tempoTotalFormatadoInput",
            "readonly": "readonly",
        })
    )

    class Meta:
        model = Desafio
        fields = [
            "titulo",
            "tipo_prova",
            "nivel",
            "ordem",
            "quantidade_questoes",
            "ativo",
        ]

        widgets = {
            "titulo": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Digite o título do desafio"
            }),
            "tipo_prova": forms.Select(attrs={
                "class": "form-control",
                "id": "tipoProvaSelect",
            }),
            "nivel": forms.Select(attrs={
                "class": "form-control",
            }),
            "ordem": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "1"
            }),
            "quantidade_questoes": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "1",
                "id": "quantidadeQuestoesInput",
                "readonly": "readonly",
            }),
            "ativo": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),
        }

        labels = {
            "titulo": "Título do desafio",
            "tipo_prova": "Tipo de prova",
            "nivel": "Nível de dificuldade",
            "ordem": "Ordem",
            "quantidade_questoes": "Quantidade de questões",
            "ativo": "Desafio ativo",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk and self.instance.tempo_total_segundos:
            minutos = self.instance.tempo_total_segundos // 60
            segundos = self.instance.tempo_total_segundos % 60

            if segundos == 0:
                self.fields["tempo_total_formatado"].initial = f"{minutos} min"
            else:
                self.fields["tempo_total_formatado"].initial = f"{minutos} min e {segundos} seg"

    
    def clean(self):
        cleaned_data = super().clean()

        tipo_prova = cleaned_data.get("tipo_prova")
        ordem = cleaned_data.get("ordem")

        if tipo_prova and ordem:
            desafio_existente = Desafio.objects.filter(
                tipo_prova=tipo_prova,
                ordem=ordem
            )

            if self.instance and self.instance.pk:
                desafio_existente = desafio_existente.exclude(pk=self.instance.pk)

            if desafio_existente.exists():
                raise forms.ValidationError(
                    "Já existe um desafio com essa ordem para este tipo de prova."
                )

        return cleaned_data