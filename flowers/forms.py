from django import forms
from django.core.exceptions import ValidationError


from .models import Flower


class CategoryForm(forms.Form):
    
    FAVORITE_COLORS_CHOICES = {
    "blue": "Blue",
    "green": "Green",
    "black": "Black",
}
    favorite_colors = forms.MultipleChoiceField(
        required=False,
        widget=forms.NullBooleanSelect,
        choices=FAVORITE_COLORS_CHOICES,
    )
    
    title = forms.CharField(max_length=100, min_length=10, required=True)
    image = forms.ImageField(required=True)
    
    def clean_title(self):
        data = super().clean()
        title = data['title']
        
        if len(title) < 12:
            raise ValidationError('Title must be more than 12 symbols')
    
    
class FlowersForm(forms.ModelForm):
    
    class Meta:
        model = Flower
        fields = ['category', 'title', 'description', 'price', 'image']
        
        widgets = {
            'category': forms.CheckboxSelectMultiple()
        }
        

    def clean(self):
        data = super().clean()
        
        flower = Flower.objects.get(title=data['title'])
        
        if flower:
            raise ValidationError('Flower exists!')