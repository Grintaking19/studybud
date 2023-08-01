from django.forms import ModelForm, Textarea
from .models import Room, Message


class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['participants']
        # widgits = {
        #     'description': Textarea(attrs={ 'rows': 5})
        # }


class MessageForm(ModelForm):
    class Meta:
        model = Message
        fields = ['body']
        