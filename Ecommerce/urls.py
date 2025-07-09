from django.contrib import admin
from django.urls import path
from Client_app import views
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path('', views.login_view, name='root_login'),
    path('admin/', admin.site.urls),
    path('signup/',views.signup,name='signup'),
    path('login/',views.login_view,name='login'),
    path('productadd/',views.productadd,name='add'),
    path('logout/',views.logout_user,name='logout'),
    path('home/', views.home, name='home'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('buy-now/<int:product_id>/', views.buy_now, name='buy_now'),
    path('update-cart/<int:product_id>/', views.update_cart, name='update_cart'),
    path('order-confirmation/', views.order_confirmation, name='order_confirmation'),
    path('admin-orders/', views.admin_orders, name='admin_orders'),
    path('product_filter/', views.product_filter, name='product_filter'),
    path('admin-products/', views.admin_products, name='admin_products'),
    path('admin-customers/', views.admin_customers, name='admin_customers'),
    #rest api url
    path('get_user_details/', views.get_user_details, name='get_user_details'),
    path('post_user_details/', views.post_user_details, name='post_user_details'),
    path('update_user_details/<int:user_id>/', views.update_user_details, name='update_user_details'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('orders/', views.user_orders, name='user_orders'),
    path('dashboard/orders/approve/<int:order_id>/', views.approve_order, name='approve_order'),
    path('dashboard/orders/reject/<int:order_id>/', views.reject_order, name='reject_order'),
    path('', views.login_view, name='root_login')

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

