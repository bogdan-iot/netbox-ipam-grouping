from netbox.api.routers import NetBoxRouter
from . import views

router = NetBoxRouter()
router.register("applications", views.ApplicationViewSet)
router.register("groups", views.GroupViewSet)

urlpatterns = router.urls
