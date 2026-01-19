from django import forms
from authentication.models import CustomUser

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    class Meta:
        model = CustomUser
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'contact_number',
            'role',  # Admin can update role
        ]




from customer_dashboard.models import CustomerWasteInfo, LocalBody

class WasteProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerWasteInfo
        fields = [
            "full_name",
            "secondary_number",
            "pickup_address",
            "landmark",
            "pincode",
            "state",
            "district",
            "localbody",
            "ward",
            "waste_type",
            "number_of_bags",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Show empty localbody queryset by default
        self.fields['localbody'].queryset = LocalBody.objects.none()

        if 'district' in self.data:
            try:
                district_id = int(self.data.get('district'))
                self.fields['localbody'].queryset = LocalBody.objects.filter(district_id=district_id).order_by("name")
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.district:
            # When editing an existing record → preload localbodies of its district
            self.fields['localbody'].queryset = LocalBody.objects.filter(district=self.instance.district).order_by("name")
