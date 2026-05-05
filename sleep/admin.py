from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from sleep.models import SleepRecord


def fmt_duration(td):
    if not td:
        return "-"
    s = int(td.total_seconds())
    h, rem = divmod(s, 3600)
    m = rem // 60
    if h:
        return f"{h}h {m:02d}m"
    return f"{m}m"


@admin.register(SleepRecord)
class SleepRecordAdmin(ImportExportModelAdmin):
    list_display = (
        "user",
        "date",
        "fmt_total",
        "fmt_deep",
        "fmt_rem",
        "fmt_core",
        "fmt_awake",
    )
    list_filter = ("user", "date")
    search_fields = ("user__username", "user__email")
    date_hierarchy = "date"
    ordering = ("-date",)
    fieldsets = (
        (
            "Información básica",
            {"fields": ("user", "date", "sleep_start", "sleep_end")},
        ),
        (
            "Tiempo total",
            {"fields": ("total_sleep_time",)},
        ),
        (
            "Fases del sueño",
            {"fields": ("awake_time", "rem_time", "core_time", "deep_time")},
        ),
        (
            "Notas",
            {"fields": ("notes",)},
        ),
    )

    def fmt_total(self, obj):
        return fmt_duration(obj.total_sleep_time)
    fmt_total.short_description = "Total"
    fmt_total.admin_order_field = "total_sleep_time"

    def fmt_deep(self, obj):
        return fmt_duration(obj.deep_time)
    fmt_deep.short_description = "Profundo"
    fmt_deep.admin_order_field = "deep_time"

    def fmt_rem(self, obj):
        return fmt_duration(obj.rem_time)
    fmt_rem.short_description = "REM"
    fmt_rem.admin_order_field = "rem_time"

    def fmt_core(self, obj):
        return fmt_duration(obj.core_time)
    fmt_core.short_description = "Core"
    fmt_core.admin_order_field = "core_time"

    def fmt_awake(self, obj):
        return fmt_duration(obj.awake_time)
    fmt_awake.short_description = "Despierto"
    fmt_awake.admin_order_field = "awake_time"
