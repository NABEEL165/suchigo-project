from django import forms
from .models import WasteCollection
from authentication.models import CustomUser





class WasteCollectionForm(forms.ModelForm):

    photo_data = forms.CharField(widget=forms.HiddenInput(), required=True)

    class Meta:
        model = WasteCollection
        fields = [
            'customer', 'localbody', 'ward', 'location', 'building_no',
            'street_name', 'kg', 'rate_per_kg', 'scheduled_date'
        ]
        widgets = {
            'localbody': forms.Select(attrs={'required': True}),
            'ward': forms.TextInput(attrs={'required': True}),
            'location': forms.TextInput(attrs={'required': True}),
            'building_no': forms.TextInput(attrs={'required': True}),
            'street_name': forms.TextInput(attrs={'required': True}),
            'kg': forms.NumberInput(attrs={'required': True}),
            'rate_per_kg': forms.NumberInput(attrs={'required': True}),
            'scheduled_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Show only users with role = "customer"
        self.fields['customer'].queryset = CustomUser.objects.filter(role=0)
        # Populate localbody choices
        from super_admin_dashboard.models import LocalBody
        self.fields['localbody'].queryset = LocalBody.objects.all()
        # Set default rate
        self.fields['rate_per_kg'].initial = 50.00

    def clean(self):
        cleaned_data = super().clean()
        photo_data = self.data.get('photo_data')
        if not photo_data:
            raise forms.ValidationError("Please capture a photo using the camera before submitting.")
        return cleaned_data








