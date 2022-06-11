from django.contrib import admin
from .models import Gate, InOutRecord
# Register your models here.
@admin.register(Gate)
class Gate(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'pass_day',
        'in_date',
        'out_date',
        'work_time',
        'break_time',
    )
    exclude = ()


@admin.register(InOutRecord)
class InOutRecode(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'check_time',
        'tag',
    )
    exclude = ()