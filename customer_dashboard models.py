



from django.db import models
from authentication.models import CustomUser
from django.utils import timezone
from super_admin_dashboard.models import State, District, LocalBody, LocalBodyCalendar
from django.conf import settings


class CustomerWasteInfo(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('collected', 'Collected'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='customer_info')
    full_name = models.CharField(max_length=255, default='', blank=True)
    secondary_number = models.CharField(max_length=15, blank=True, null=True)
    pickup_address = models.CharField(max_length=255, default="")
    landmark = models.CharField(max_length=255, blank=True, null=True)

    # Location coordinates from Google Maps
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        help_text="Latitude coordinate from Google Maps"
    )
    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        help_text="Longitude coordinate from Google Maps"
    )

    # Optional: Store the full formatted address from Google Maps
    formatted_address = models.TextField(
        blank=True,
        null=True,
        help_text="Full address from Google Maps Geocoding API"
    )

    # Optional: Store Google Maps place_id for future reference
    place_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Google Maps Place ID"
    )

    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True)
    localbody = models.ForeignKey(LocalBody, on_delete=models.SET_NULL, null=True)
    ward = models.CharField(max_length=50, null=True, blank=True)
    number_of_bags = models.IntegerField(null=True, blank=True)
    waste_type = models.CharField(max_length=100, null=True, blank=True)
    comments = models.TextField(blank=True, null=True)
    pincode = models.CharField(max_length=10)

    assigned_collector = models.ForeignKey(
        CustomUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='assigned_waste'
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Customer Waste Information"
        verbose_name_plural = "Customer Waste Information"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['localbody', 'status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.localbody}"

    def get_google_maps_url(self):
        """Generate a Google Maps URL for the pickup location"""
        if self.latitude and self.longitude:
            return f"https://www.google.com/maps?q={self.latitude},{self.longitude}"
        return None

    def get_coordinates(self):
        """Return coordinates as a tuple"""
        if self.latitude and self.longitude:
            return (float(self.latitude), float(self.longitude))
        return None


class CustomerPickupDate(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE
    )
    waste_info = models.ForeignKey(
        'CustomerWasteInfo',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    localbody_calendar = models.ForeignKey(
        LocalBodyCalendar,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "localbody_calendar")
        verbose_name = "Customer Pickup Date"
        verbose_name_plural = "Customer Pickup Dates"
        ordering = ['-created_at']
        indexes = []  # prevent Django from auto-creating duplicate indexes

    def __str__(self):
        return f"{self.user.username} - {self.localbody_calendar.date}"


# Optional: Model to track location history for analytics
class CustomerLocationHistory(models.Model):
    """Track location changes for audit and analytics purposes"""

    waste_info = models.ForeignKey(
        CustomerWasteInfo,
        on_delete=models.CASCADE,
        related_name='location_history'
    )
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    formatted_address = models.TextField(blank=True, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True
    )

    class Meta:
        verbose_name = "Location History"
        verbose_name_plural = "Location Histories"
        ordering = ['-changed_at']

    def __str__(self):
        return f"Location change for {self.waste_info.user.username} at {self.changed_at}"


