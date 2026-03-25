from django.urls import include, path

from auth_service.api.v1.urls import urlpatterns_v1

app_name = "auth-service"

urlpatterns = [
    path("v1/", include(urlpatterns_v1)),
]
