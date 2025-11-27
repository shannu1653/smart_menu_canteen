from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [

    # -------------------------
    # Django Admin Panel
    # -------------------------
    path('admin/', admin.site.urls),

    # -------------------------
    # Authentication (Global)
    # -------------------------
    path('login/',
         auth_views.LoginView.as_view(template_name='auth/login.html'),
         name='login'),

    path('logout/',
         auth_views.LogoutView.as_view(next_page='home'),
         name='logout'),

    # -------------------------
    # Main App Routes
    # -------------------------
    path('', include('menu_app.urls')),     # menu, menu-pro, cart, register, dashboard

    # -------------------------
    # API Routes
    # -------------------------
    path('api/', include('menu_app.api_urls')),

]

# -------------------------
# MEDIA (Images)
# -------------------------
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
