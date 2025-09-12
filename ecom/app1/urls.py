from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('logreg/', views.logreg, name="logreg"),
    path('LogOut/', views.LogOut, name="LogOut"),
    path('all_books/', views.all_books, name="all_books"),
    path('my_orders/', views.my_orders, name="my_orders"),
    path('myCart/', views.myCart, name="myCart"),
    path('update_cart/', views.update_cart, name="update_cart"),
    path('checkout/', views.checkout, name="checkout"),
    path('reviews/', views.reviews, name="reviews"),
    path('payment_handler/', views.payment_handler, name="payment_handler"),
    path('remove_from_cart/', views.remove_from_cart, name="remove_from_cart"),
    path('book_details/<int:id>/', views.book_details, name="book_details"),
    path('buy_now/<int:id>/', views.buy_now, name="buy_now"),
    path('add_to_cart/<int:id>/', views.add_to_cart, name="add_to_cart"),
    path('order_success/<int:id>/', views.order_success, name="order_success"),
    path('delete_review/<int:id>/', views.delete_review, name="delete_review"),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
