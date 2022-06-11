from django.urls import path
from . import views
app_name = "gate"


urlpatterns = [
    path("api/v1/hook/", views.GateAPIView.as_view()),
    path("api/v1/gate/<int:id>/", views.GateDetailAPIView.as_view()),
    path("api/v1/gate/user/", views.GateUserDetail.as_view()),
]

