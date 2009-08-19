from django.forms import ModelForm
from reader.models import Feed
from django import forms

class FeedForm(ModelForm):
    class Meta:
        model = Feed