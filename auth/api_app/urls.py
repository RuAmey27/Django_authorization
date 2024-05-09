from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import YourModelViewSet
from .views import GetAccessTokenView

router = DefaultRouter()
router.register(r'your-model', YourModelViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('get-access-token/', GetAccessTokenView.as_view(), name='get-access-token'),
]


