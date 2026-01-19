from django.db import models
from authentication.models import CustomUser
from decimal import Decimal
from super_admin_dashboard.models import LocalBody

class WasteCollection(models.Model):
    collector = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='collections')
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='waste_collected')
    # localbody = models.ForeignKey(LocalBody, on_delete=models.CASCADE, null=True, blank=True)
    localbody = models.ForeignKey(
    LocalBody,
    on_delete=models.SET_NULL,
    null=True,
    blank=True
)


    ward = models.CharField(max_length=50)
    location = models.CharField(max_length=200)
    building_no = models.CharField(max_length=50)
    street_name = models.CharField(max_length=100)
    kg = models.DecimalField(max_digits=6, decimal_places=2)
    rate_per_kg = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('50.00'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    photo = models.ImageField(upload_to='collection_photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Booking and scheduled dates
    booking_date = models.DateTimeField(auto_now_add=True)  # When the order was placed
    scheduled_date = models.DateField(null=True, blank=True)  # When the collection is scheduled

    def save(self, *args, **kwargs):
        if not self.rate_per_kg:
            self.rate_per_kg = Decimal('50.00')
        self.total_amount = self.kg * self.rate_per_kg
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Waste collected by {self.collector.username} from {self.customer.username}"


class Wallet(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Wallet - ₹{self.balance}"

    def deposit(self, amount):
        """Add funds to the wallet"""
        if amount > 0:
            self.balance += amount
            self.save()
            # Create transaction record
            WalletTransaction.objects.create(
                wallet=self,
                transaction_type='deposit',
                amount=amount,
                balance_after_transaction=self.balance
            )
            return True
        return False

    def withdraw(self, amount):
        """Withdraw funds from the wallet"""
        if 0 < amount <= self.balance:
            self.balance -= amount
            self.save()
            # Create transaction record
            WalletTransaction.objects.create(
                wallet=self,
                transaction_type='withdrawal',
                amount=amount,
                balance_after_transaction=self.balance
            )
            return True
        return False

    def can_afford(self, amount):
        """Check if wallet has sufficient balance"""
        return self.balance >= amount


class WalletTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('payment', 'Payment'),
        ('refund', 'Refund'),
    ]

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    balance_after_transaction = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.wallet.user.username} - {self.transaction_type} - ₹{self.amount}"
