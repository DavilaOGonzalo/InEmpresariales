from rest_framework.routers import SimpleRouter

from .views import HospitalViewSet

router = SimpleRouter()
router.register('', HospitalViewSet, basename='api-admin-hospital')

urlpatterns = router.urls
