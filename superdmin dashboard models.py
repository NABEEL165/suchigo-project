from django.db import models


class State(models.Model):
    name = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.name


class District(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name="districts")
    name = models.CharField(max_length=120)

    class Meta:
        unique_together = ("state", "name")

    def __str__(self):
        return f"{self.name} ({self.state.name})"


class LocalBody(models.Model):
    TYPE_CHOICES = (
        ("corporation", "Corporation"),
        ("municipality", "Municipality"),
        ("panchayat", "Panchayat"),
    )

    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name="localbodies")
    name = models.CharField(max_length=200)
    body_type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    class Meta:
        unique_together = ("district", "name")

    def __str__(self):
        return f"{self.name} — {self.get_body_type_display()}"


class LocalBodyCalendar(models.Model):
    localbody = models.ForeignKey(LocalBody, on_delete=models.CASCADE, related_name="calendar_dates")
    date = models.DateField()

    class Meta:
        unique_together = ("localbody", "date")
        ordering = ("-date",)

    def __str__(self):
        return f"{self.localbody.name} - {self.date.isoformat()}"
