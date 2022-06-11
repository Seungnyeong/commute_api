from django.db import models
from core.models import TimeStampedModel
from django.core.validators import MinValueValidator, MaxValueValidator


# Create your models here.
class Gate(models.Model):
    pass_day = models.DateField(null=False)

    in_date = models.DateTimeField(null=True)
    out_date = models.DateTimeField(null=True)

    work_time = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(3600)])
    break_time = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(3600)])

    user = models.ForeignKey("users.User", on_delete=models.DO_NOTHING, null=False)

    def __str__(self):
        return self.user.username

    class Meta:
        db_table = "gate"
        managed = True
        verbose_name_plural = "일별출입기록"


class InOutRecord(models.Model):
    IN = "IN"
    OUT = "OUT"

    TAG_CHOICE = (
        (IN, "출근"),
        (OUT, "퇴근"),
    )

    check_time = models.DateTimeField()

    gate = models.ForeignKey("Gate", on_delete=models.CASCADE, related_name="inout", null=False)
    user = models.ForeignKey("users.User", on_delete=models.DO_NOTHING, related_name="inout", null=False)

    tag = models.CharField(
        choices=TAG_CHOICE,
        max_length=6, null=True
    )

    def __str__(self):
        return f"[{self.tag}] {self.user}"

    class Meta:
        verbose_name_plural = "출입기록"