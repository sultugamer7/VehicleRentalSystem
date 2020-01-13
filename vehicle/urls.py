from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.index, name="index"),
    path("register", views.register_view, name="register"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("search", views.search_view, name="search"),
    path("vehicle/<brand>/<model>", views.vehicle_view, name="vehicle"),
    path("book", views.book_view, name="book"),
    path("bookings", views.bookings_view, name="bookings"),
    path("bookings/booking/<int:booking_id>", views.booking_details_view, name="booking_details"),
    path("extend", views.extend_view, name="extend"),
    path("cancel_booking", views.cancel_booking_view, name="cancel_booking"),


    # Password change and reset links (ref: https://github.com/django/django/blob/master/django/contrib/auth/views.py)
    # https://github.com/mitchtabian/CodingWithMitch-Blog-Course/tree/Reset-Password-and-Change-Password-(Django)
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), 
        name='password_change_done'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change.html'), 
        name='password_change'),
    path('password_reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_done.html'),
     name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
     name='password_reset_complete'),
]
