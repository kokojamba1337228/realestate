from django import forms
from .models import Property, Tag

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class PropertyForm(forms.ModelForm):
    images = MultipleFileField(required=False)

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Property
        fields = ['title', 'description', 'price', 'location', 'size', 'tags'] 

class SupportMessageForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={
        'placeholder': 'Ваш вопрос...',
        'rows': 4
    }), max_length=1000)


