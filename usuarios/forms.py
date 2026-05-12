from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Usuario


from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Usuario


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Usuário ou e-mail",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Digite seu usuário ou e-mail",
        })
    )

    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Digite sua senha",
        })
    )

    error_messages = {
        "invalid_login": (
            "Usuário, e-mail ou senha inválidos. Verifique os dados e tente novamente."
        ),
        "inactive": "Esta conta está inativa.",
    }

    def clean(self):
        username = self.cleaned_data.get("username")

        if username and "@" in username:
            try:
                usuario = Usuario.objects.get(email__iexact=username)
                self.cleaned_data["username"] = usuario.username
            except Usuario.DoesNotExist:
                pass

        return super().clean()

class CadastroEstudanteForm(forms.ModelForm):
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Digite sua senha"
        })
    )

    confirmar_password = forms.CharField(
        label="Confirmar senha",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirme sua senha"
        })
    )

    class Meta:
        model = Usuario
        fields = ["nome", "email", "username"]
        widgets = {
            "nome": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Digite seu nome"
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Digite seu e-mail"
            }),
            "username": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Escolha um nome de usuário"
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Já existe um usuário com este e-mail.")

        return email

    def clean_username(self):
        username = self.cleaned_data.get("username")

        if Usuario.objects.filter(username=username).exists():
            raise forms.ValidationError("Já existe um usuário com este nome de usuário.")

        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirmar_password = cleaned_data.get("confirmar_password")

        if password and confirmar_password and password != confirmar_password:
            raise forms.ValidationError("As senhas não coincidem.")

        return cleaned_data
    

class UsuarioAdminForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ["nome", "username", "email", "is_active"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }