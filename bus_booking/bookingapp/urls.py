from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('buses/', views.view_buses, name='view_buses'),
    path('book/<int:bus_id>/', views.book_ticket, name='book_ticket'),
    path('bookings/', views.view_bookings, name='view_bookings'),
    path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('signup/', views.signup_user, name='signup'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('search/', views.search_buses, name='search_buses'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('download-ticket/<int:booking_id>/', views.download_ticket, name='download_ticket'),

]