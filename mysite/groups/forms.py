from django import forms
from django.core import validators
from .models import Group



class CreateGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'description', 'profile']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Group Name', 'id': 'group-name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Group Description', 'id': 'group-description'}),
            'profile': forms.FileInput(attrs={'class': 'form-control', 'placeholder': 'Enter Group Profile','id': 'group-profile'}),
        }
    
    join_this_group = forms.BooleanField(
        required=False, label="Join this group?", initial=True, widget=forms.CheckboxInput(
            attrs={'class': 'form-check-input', 'id': 'join-group'}
        )
    )
    
    def __init__(self,*args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(CreateGroupForm, self).__init__(*args, **kwargs)
        self.fields['name'].validators.extend([
            validators.MaxLengthValidator(50,'Group name must be at most 50 characters long.'),
            validators.MinLengthValidator(3,'Group name must be at least 3 characters long.'),
        ])
            
    
    def save(self, commit=True):
        group = super().save(commit=False)
        if commit:
            group.save()
            if self.cleaned_data['join_this_group']:
                group.members.add(self.user)
        return group