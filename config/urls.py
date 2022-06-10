from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.contrib import admin
from django.conf import settings
from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

schema_view = get_schema_view(
    openapi.Info(
        title="Wanted LAB",  # 타이틀
        default_version='v1',  # 버전
        description="지원자 김승녕",  # 설명
        terms_of_service="wantedlab",
        contact=openapi.Contact(
            email="workingsnkim@gamil.com", name="김승녕"),
    ),
    validators=['flex'],
    public=True,
    authentication_classes = (),
    permission_classes = ()
    
)

urlpatterns = []

api_url = []

urlpatterns = urlpatterns + api_url


if settings.DEBUG:
    # swagger URL
    urlpatterns += [
        path(r'swagger(?P<format>\.json|\.yaml)', schema_view.without_ui(
            cache_timeout=0), name='schema-json'),
        path('swagger/', schema_view.with_ui(
            'swagger', cache_timeout=0), name='schema-swagger-ui'),
        path(r'redoc/', schema_view.with_ui(
            'redoc', cache_timeout=0), name='schema-redoc-v1'),
        path('admin/', admin.site.urls),
    ] + staticfiles_urlpatterns()


