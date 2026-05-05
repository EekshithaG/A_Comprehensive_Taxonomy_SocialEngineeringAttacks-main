from django import forms

class PredictionForm(forms.Form):
    input_data = forms.CharField(
        label='Enter comma-separated input',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. -1,1,1,...'})
    )
