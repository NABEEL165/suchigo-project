from django.db import models
from authentication.models import CustomUser
from decimal import Decimal
class WasteCollection(models.Model):
    collector = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='collections')
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='waste_collected')
    localbody = models.CharField(max_length=100)

    ward = models.CharField(max_length=50)
    location = models.CharField(max_length=200)
    building_no = models.CharField(max_length=50)
    street_name = models.CharField(max_length=100)
    kg = models.DecimalField(max_digits=6, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    photo = models.ImageField(upload_to='collection_photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.total_amount = self.kg *  Decimal('50.00')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Waste collected by {self.collector.username} from {self.customer.username}"
