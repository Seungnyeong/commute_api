"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.contrib import admin
from django.conf import settings
from django.urls import path

schema_view = get_schema_view(
    openapi.Info(
        title="Wanted LAB",  # 타이틀
        default_version='v1',  # 버전
        description="지원자 김승녕",  # 설명
        terms_of_service="wantedlab",
        contact=openapi.Contact(
            email="workingsnkim@gamil.com", name="개발자에게 이메일 보내기"),
    ),
    validators=['flex'],
    public=True,
    authentication_classes = (),
    permission_classes = ()
    
)

urlpatterns = [
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    # swagger URL
    urlpatterns += [
        path(r'swagger(?P<format>\.json|\.yaml)', schema_view.without_ui(
            cache_timeout=0), name='schema-json'),
        path('swagger/', schema_view.with_ui(
            'swagger', cache_timeout=0), name='schema-swagger-ui'),
        path(r'redoc/', schema_view.with_ui(
            'redoc', cache_timeout=0), name='schema-redoc-v1'),
        path('admin/', admin.site.urls)
    ]


