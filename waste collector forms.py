from django import forms
from .models import WasteCollection
from authentication.models import CustomUser





class WasteCollectionForm(forms.ModelForm):

    photo_data = forms.CharField(widget=forms.HiddenInput(), required=True)

    class Meta:
        model = WasteCollection
        fields = [
            'customer', 'localbody', 'ward', 'location', 'building_no',
            'street_name', 'kg'
        ]
        widgets = {
            'localbody': forms.TextInput(attrs={'required': True}),
            'ward': forms.TextInput(attrs={'required': True}),
            'location': forms.TextInput(attrs={'required': True}),
            'building_no': forms.TextInput(attrs={'required': True}),
            'street_name': forms.TextInput(attrs={'required': True}),
            'kg': forms.NumberInput(attrs={'required': True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Show only users with role = "customer"
        self.fields['customer'].queryset = CustomUser.objects.filter(role=0)

    def clean(self):
        cleaned_data = super().clean()
        photo_data = self.data.get('photo_data')
        if not photo_data:
            raise forms.ValidationError("Please capture a photo using the camera before submitting.")
        return cleaned_data








