
from django.contrib import admin
from django.urls import path
from mess_portal import views

admin.site.site_header="Mess Admin Portal"
admin.site.site_title="Mess Admin Portal"
admin.site.site_url="Mess Admin Portal"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('menu/', views.menu, name='menu'),
    path('menu/weekly/', views.menu_sheet, name='menu_sheet'),
    path('committee/', views.committee, name='committee'),
    path('contact/', views.contact, name='contact'),
    path('complaints/', views.complaints, name='complaints'),
]