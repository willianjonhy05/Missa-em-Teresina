from django import forms
from .models import Usuario, Igreja, TipoCelebracao


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


class CelebracaoForm(forms.ModelForm):
    class Meta:
        model = TipoCelebracao
        fields = [
            "igreja",
            "nome",
            "categoria",
            "recorrencia",
            "horario_inicio",
            "descricao",
            "dia",
            "dia_mes",
            "data_especifica",
            "exige_agendamento",
            "exibir_no_site",
            "ativo",
        ]

        widgets = {
            "igreja": forms.Select(attrs={
                "class": "form-select",
            }),
            "nome": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex: Missa Dominical",
            }),
            "categoria": forms.Select(attrs={
                "class": "form-select",
            }),
            "recorrencia": forms.Select(attrs={
                "class": "form-select",
            }),
            "horario_inicio": forms.TimeInput(attrs={
                "class": "form-control",
                "type": "time",
            }),
            "descricao": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Informe uma breve descrição da celebração",
            }),
            "dia": forms.Select(attrs={
                "class": "form-select",
            }),
            "dia_mes": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1,
                "max": 31,
                "placeholder": "Ex: 13",
            }),
            "data_especifica": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
            "exige_agendamento": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
            "exibir_no_site": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
            "ativo": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }

    def clean(self):
        cleaned_data = super().clean()

        recorrencia = cleaned_data.get("recorrencia")
        dia = cleaned_data.get("dia")
        dia_mes = cleaned_data.get("dia_mes")
        data_especifica = cleaned_data.get("data_especifica")

        if recorrencia == "semanal":
            if not dia:
                self.add_error(
                    "dia",
                    "Informe o dia da semana para celebrações semanais."
                )

            if dia_mes:
                self.add_error(
                    "dia_mes",
                    "Para celebrações semanais, deixe o dia do mês vazio."
                )

            if data_especifica:
                self.add_error(
                    "data_especifica",
                    "Para celebrações semanais, deixe a data específica vazia."
                )

        elif recorrencia == "mensal_dia_fixo":
            if not dia_mes:
                self.add_error(
                    "dia_mes",
                    "Informe o dia do mês para celebrações mensais."
                )

            if dia:
                self.add_error(
                    "dia",
                    "Para celebrações mensais em dia fixo, deixe o dia da semana vazio."
                )

            if data_especifica:
                self.add_error(
                    "data_especifica",
                    "Para celebrações mensais em dia fixo, deixe a data específica vazia."
                )

        elif recorrencia == "data_especifica":
            if not data_especifica:
                self.add_error(
                    "data_especifica",
                    "Informe a data específica da celebração."
                )

            if dia:
                self.add_error(
                    "dia",
                    "Para celebrações com data específica, deixe o dia da semana vazio."
                )

            if dia_mes:
                self.add_error(
                    "dia_mes",
                    "Para celebrações com data específica, deixe o dia do mês vazio."
                )

        return cleaned_data