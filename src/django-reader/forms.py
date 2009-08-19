from django.forms import ModelForm
from feedreader.models import Feed
from django import forms

class FeedForm(ModelForm):
    class Meta:
        model = Feed