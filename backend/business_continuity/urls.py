from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    BusinessServiceViewSet,
    ServiceAssetLinkViewSet,
    ContinuityPlanViewSet,
    ContinuityPlanTestViewSet,
    AssetRecoveryProcedureViewSet,
)

router = DefaultRouter()
router.register(
    r"business-services", BusinessServiceViewSet, basename="business-services"
)
router.register(
    r"service-asset-links", ServiceAssetLinkViewSet, basename="service-asset-links"
)
router.register(
    r"continuity-plans", ContinuityPlanViewSet, basename="continuity-plans"
)
router.register(
    r"continuity-plan-tests",
    ContinuityPlanTestViewSet,
    basename="continuity-plan-tests",
)
router.register(
    r"asset-recovery-procedures",
    AssetRecoveryProcedureViewSet,
    basename="asset-recovery-procedures",
)

urlpatterns = [
    path("", include(router.urls)),
]
