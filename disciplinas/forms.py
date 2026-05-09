from django import forms

from .models import Disciplina


class DisciplinaForm(forms.ModelForm):
    class Meta:
        model = Disciplina
        fields = ["nome"]

        widgets = {
            "nome": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Digite o nome da disciplina",
                "autocomplete": "off",
            })
        }

        labels = {
            "nome": "Nome da disciplina"
        }

    def clean_nome(self):
        nome = self.cleaned_data.get("nome")

        if nome:
            nome = nome.strip()

        if Disciplina.objects.filter(nome__iexact=nome).exclude(id=self.instance.id).exists():
            raise forms.ValidationError("Já existe uma disciplina com esse nome.")

        return nome