from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import CallSourceNumber, MissedCallVerification


@admin.register(CallSourceNumber)
class CallSourceNumberAdmin(admin.ModelAdmin):
    list_display = [
        'phone_number', 
        'label', 
        'is_active', 
        'verification_count',
        'created_at'
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['phone_number', 'label']
    readonly_fields = ['created_at', 'updated_at', 'verification_count']
    
    fieldsets = (
        (_('Number Information'), {
            'fields': ('phone_number', 'label', 'is_active')
        }),
        (_('Statistics'), {
            'fields': ('verification_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def verification_count(self, obj):
        """Display count of verifications using this number"""
        count = obj.verifications.count()
        if count > 0:
            url = reverse('admin:drf_missed_call_auth_missedcallverification_changelist')
            return format_html(
                '<a href="{}?expected_caller__id__exact={}">{} verifications</a>',
                url, obj.id, count
            )
        return '0 verifications'
    verification_count.short_description = _('Usage Count')


@admin.register(MissedCallVerification)
class MissedCallVerificationAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user_phone_display',
        'expected_caller',
        'status_badge',
        'attempt_count',
        'created_at',
        'expires_at'
    ]
    list_filter = [
        'is_verified',
        'created_at',
        'expires_at',
        'expected_caller'
    ]
    search_fields = [
        'id',
        'user_phone',
        'app_signature',
        'ip_address'
    ]
    readonly_fields = [
        'id',
        'user_phone',
        'app_signature',
        'expected_caller',
        'is_verified',
        'created_at',
        'expires_at',
        'verified_at',
        'ip_address',
        'attempt_count',
        'status_display',
        'time_remaining_display'
    ]
    
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (_('Session Information'), {
            'fields': (
                'id',
                'user_phone',
                'app_signature',
                'ip_address'
            )
        }),
        (_('Verification Details'), {
            'fields': (
                'expected_caller',
                'is_verified',
                'verified_at',
                'attempt_count',
                'status_display',
            )
        }),
        (_('Timing'), {
            'fields': (
                'created_at',
                'expires_at',
                'time_remaining_display'
            )
        }),
    )
    
    def has_add_permission(self, request):
        """Prevent manual creation of verifications through admin"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Make verifications read-only in admin"""
        return False
    
    def user_phone_display(self, obj):
        """Display sanitized phone number"""
        from .utils import sanitize_phone_for_logging
        return sanitize_phone_for_logging(obj.user_phone)
    user_phone_display.short_description = _('User Phone')
    
    def status_badge(self, obj):
        """Display status as colored badge"""
        if obj.is_verified:
            color = 'green'
            status = _('Verified')
            icon = '✓'
        elif obj.is_expired:
            color = 'red'
            status = _('Expired')
            icon = '✗'
        else:
            color = 'orange'
            status = _('Pending')
            icon = '⏳'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color, icon, status
        )
    status_badge.short_description = _('Status')
    
    def status_display(self, obj):
        """Detailed status information"""
        if obj.is_verified:
            return format_html(
                '<span style="color: green;">✓ Verified at {}</span>',
                obj.verified_at.strftime('%Y-%m-%d %H:%M:%S') if obj.verified_at else 'N/A'
            )
        elif obj.is_expired:
            return format_html(
                '<span style="color: red;">✗ Expired</span>'
            )
        else:
            return format_html(
                '<span style="color: orange;">⏳ Pending (valid)</span>'
            )
    status_display.short_description = _('Detailed Status')
    
    def time_remaining_display(self, obj):
        """Display time remaining or time since expiry"""
        if obj.is_expired:
            from django.utils.timezone import now
            elapsed = now() - obj.expires_at
            return format_html(
                '<span style="color: red;">Expired {} ago</span>',
                elapsed
            )
        else:
            remaining = obj.time_remaining
            return format_html(
                '<span style="color: green;">{}</span>',
                remaining
            )
    time_remaining_display.short_description = _('Time Status')
    
    actions = ['mark_as_expired']
    
    def mark_as_expired(self, request, queryset):
        """Admin action to manually expire sessions"""
        from django.utils import timezone
        count = queryset.update(expires_at=timezone.now())
        self.message_user(
            request,
            _('{} session(s) marked as expired.').format(count)
        )
    mark_as_expired.short_description = _('Mark selected as expired')