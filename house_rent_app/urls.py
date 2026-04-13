from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include

from . import views

urlpatterns = [
    path('', views.SignupView.as_view(), name='signup'),
    path('login', views.LoginView.as_view(), name='login'),
    path('logout', views.Logout.as_view(), name='logout'),
    path('owner_home', views.OwnerHome.as_view(), name='owner_home'),
    
    path('admin_home', views.AdminHome.as_view(), name='admin_home'),

    path('admin_houses', views.AdminHouseList.as_view(), name='admin_houses'),
    path('admin_owners', views.AdminOwnerList.as_view(), name='admin_owners'),
    path('admin_tenants', views.AdminTenantList.as_view(), name='admin_tenants'),
    path('admin_edit_property', views.AdminEditProprty.as_view(), name='admin_edit_property'),
    path('admin_edit_owner', views.AdminEditOwner.as_view(), name='admin_edit_owner'),
    path('admin_edit_tenant', views.AdminEditTenant.as_view(), name='admin_edit_tenant'),

    path('owner_add_property', views.OwnerAddProperty.as_view(), name='owner_add_property'),
    path('owner_info', views.OwnerInfo.as_view(), name='owner_info'),
    path('owner_requests', views.OwnerRequests.as_view(), name='owner_requests'),
    path('owner_change_password', views.OwnerChangePassword.as_view(), name='owner_change_password'),

    path('tenant_home', views.TenantHome.as_view(), name='tenant_home'),
    path('tenant_requests', views.TenantRequests.as_view(), name='tenant_requests'),
    path('tenant_info', views.TenantInfo.as_view(), name='tenant_info'),
    path('tenant_property_details/<int:pk>/', views.TenantPropDetails.as_view(), name='tenant_property_details'),
    path('tenant_change_password', views.TenantChangePassword.as_view(), name='tenant_change_password'),


    path('export_houses/', views.export_houses, name='export_houses'),

]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)