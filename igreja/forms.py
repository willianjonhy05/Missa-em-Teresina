from django import forms
from .models import Usuario, Igreja


class UsuarioCreateForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput
    )

    password2 = forms.CharField(
        label="Confirmar senha",
        widget=forms.PasswordInput
    )

    is_staff = forms.BooleanField(
        label="Pode acessar o painel administrativo",
        required=False,
        initial=True
    )

    is_active = forms.BooleanField(
        label="Usuário ativo",
        required=False,
        initial=True
    )

    class Meta:
        model = Usuario
        fields = [
            "nome",
            "email",
            "is_staff",
            "is_active",
        ]

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Já existe um usuário cadastrado com este e-mail.")

        return email

    def clean(self):
        cleaned_data = super().clean()

        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("As senhas não conferem.")

        return cleaned_data

    def save(self, commit=True):
        usuario = super().save(commit=False)

        usuario.set_password(self.cleaned_data["password1"])
        usuario.is_superuser = False

        if commit:
            usuario.save()

        return usuario
    
    
class IgrejaCreateForm(forms.ModelForm):
    class Meta:
        model = Igreja
        fields = [
            "nome",
            "endereco",
            "bairro",
            "cidade",
            "paroquia",
            "capela",
            "aberta_ao_publico",
            "latitude",
            "longitude",
            "sacerdotes",
            "telefone",
            "imagem",
            "email",
            "site",
            "facebook",
            "instagram",
            "youtube",
            "maps",
            "contato_whatsapp",
        ]
