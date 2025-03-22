from django.contrib import admin
from .models import XeroAccount


@admin.register(XeroAccount)
class XeroChartOfAccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'account_type', 'status', 'fetch_status', 'fetched_at')
    search_fields = ('name', 'code', 'account_id')
    list_filter = ('status', 'account_type', 'fetch_status')
    readonly_fields = ('fetched_at',)
