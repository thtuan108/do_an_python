from .models import Messages
from django import forms


class MessageForm(forms.ModelForm):

    class Meta:
        model = Messages
        fields = ('message_content', )
