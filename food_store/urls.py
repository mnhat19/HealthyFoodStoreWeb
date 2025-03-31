from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('store.urls')),
    path("accounts/login/", LoginView.as_view(template_name="store/login.html"), name="login"),
    path('accounts/', include('django.contrib.auth.urls')),  # For authentication views
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # For serving media files in development
