

# customer_dashboard/forms.py
from django import forms
from .models import CustomerWasteInfo

class CustomerWasteInfoForm(forms.ModelForm):
    pickup_slot = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=False,
        label="Pickup Slot Date"
    )
    class Meta:
        model = CustomerWasteInfo
        fields = ['district', 'localbody', 'ward', 'number_of_bags', 'waste_type']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Remove 'user' from kwargs before calling super
        super().__init__(*args, **kwargs)



