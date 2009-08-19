from django.forms import ModelForm
from feedparser.models import FeedForm
from django import forms

class FeedForm(ModelForm):
    class Meta:
        model = models.Feed