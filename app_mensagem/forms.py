from django import forms
from .models import MensagemPersonalizada


class MensagemPersonalizadaForm(forms.ModelForm):
    class Meta:
        model = MensagemPersonalizada
        fields = ["tipo_pedido", "mensagem"]
