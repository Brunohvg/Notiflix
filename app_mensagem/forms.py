from django import forms
from .models import MensagemPadrao


class MensagemPersonalizadaForm(forms.ModelForm):
    class Meta:
        model = MensagemPadrao
        fields = ["tipo_pedido", "mensagem"]
