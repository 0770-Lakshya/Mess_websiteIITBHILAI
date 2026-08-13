from django.contrib import admin
from .models import Announcement, Notice


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'kind', 'active', 'created_at')
    list_filter = ('kind', 'active')
    search_fields = ('title', 'message')
    list_editable = ('active',)
    



@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'active', 'created_at')
    list_filter = ('category', 'active')
    search_fields = ('title', 'text')
    list_editable = ('active',)