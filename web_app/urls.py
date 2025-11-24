import web_app.views as views
from django.urls import path

urlpatterns = [
    path("", views.index, name='index'),
    path("profile/", views.profile, name='profile'),
    path("accounts/signup/", views.create_user, name='create_user'),
    path("profile/edit/", views.edit_user, name='edit_user'),
    path("work_in_progress/", views.wip_view, name='wip'),
    path("profile/properties_list", views.properties_list, name='properties'),
    path("profile/properties_list/create", views.create_property, name='create_property'),
    path("profile/properties_list/<int:pk>/edit", views.edit_property, name='edit_property'),
    path("profile/properties_list/<int:pk>/delete", views.delete_property, name='delete_property'),
    path("profile/properties_list/<int:pk>/images", views.property_images, name='images'),
    path("leases_list/", views.leases_list, name='leases'),
    path("leases_list/<int:pk>/detail", views.property_detail, name='property_detail' )
]