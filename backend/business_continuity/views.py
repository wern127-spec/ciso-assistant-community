from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.decorators import action
from rest_framework.response import Response

from core.views import BaseModelViewSet as AbstractBaseModelViewSet

from .models import (
    BusinessService,
    ServiceAssetLink,
    ContinuityPlan,
    ContinuityPlanTest,
    AssetRecoveryProcedure,
)

LONG_CACHE_TTL = 60  # minutes


class BaseModelViewSet(AbstractBaseModelViewSet):
    serializers_module = "business_continuity.serializers"


class BusinessServiceViewSet(BaseModelViewSet):
    model = BusinessService
    filterset_fields = ["folder", "owner", "criticality", "status"]
    search_fields = ["name", "ref_id", "description"]

    @method_decorator(cache_page(60 * LONG_CACHE_TTL))
    @action(detail=False, name="Get criticality choices")
    def criticality(self, request):
        return Response(dict(BusinessService.Criticality.choices))

    @method_decorator(cache_page(60 * LONG_CACHE_TTL))
    @action(detail=False, name="Get status choices")
    def status(self, request):
        return Response(dict(BusinessService.Status.choices))

    @action(detail=True, name="Get the full service overview")
    def overview(self, request, pk=None):
        service = self.get_object()

        folder = service.folder
        domain = {
            "id": str(folder.id),
            "name": folder.name,
            "path": [f.name for f in service.get_folder_full_path()],
        }

        asset_links = (
            ServiceAssetLink.objects.filter(business_service=service)
            .select_related("asset")
            .prefetch_related("asset__recovery_procedures")
        )
        assets = []
        for link in asset_links:
            assets.append(
                {
                    "id": str(link.id),
                    "asset": {
                        "id": str(link.asset.id),
                        "name": link.asset.name,
                    },
                    "dependency_type": link.dependency_type,
                    "dependency_type_display": link.get_dependency_type_display(),
                    "asset_impact_description": link.asset_impact_description,
                    "notes": link.notes,
                    "recovery_procedures": [
                        {
                            "id": str(p.id),
                            "name": p.name,
                            "procedure_type": p.procedure_type,
                        }
                        for p in link.asset.recovery_procedures.all()
                    ],
                }
            )

        plans = []
        for plan in ContinuityPlan.objects.filter(
            business_service=service
        ).prefetch_related("referenced_asset_procedures"):
            plans.append(
                {
                    "id": str(plan.id),
                    "name": plan.name,
                    "ref_id": plan.ref_id,
                    "version": plan.version,
                    "scenario": plan.scenario,
                    "recovery_strategy": plan.recovery_strategy,
                    "procedure_steps": plan.procedure_steps,
                    "responsible_team": plan.responsible_team,
                    "status": plan.status,
                    "status_display": plan.get_status_display(),
                    "last_review_date": plan.last_review_date,
                    "next_review_date": plan.next_review_date,
                    "referenced_asset_procedures": [
                        {"id": str(p.id), "name": p.name}
                        for p in plan.referenced_asset_procedures.all()
                    ],
                }
            )

        tests = []
        for test in (
            ContinuityPlanTest.objects.filter(
                continuity_plan__business_service=service
            )
            .select_related("continuity_plan")
            .order_by("-test_date")
        ):
            tests.append(
                {
                    "id": str(test.id),
                    "continuity_plan": {
                        "id": str(test.continuity_plan.id),
                        "name": test.continuity_plan.name,
                    },
                    "test_date": test.test_date,
                    "test_type": test.test_type,
                    "test_type_display": test.get_test_type_display(),
                    "result": test.result,
                    "result_display": test.get_result_display(),
                    "participants": test.participants,
                    "objectives": test.objectives,
                    "findings": test.findings,
                    "actions": test.actions,
                }
            )

        return Response(
            {
                "id": str(service.id),
                "name": service.name,
                "ref_id": service.ref_id,
                "description": service.description,
                "domain": domain,
                "owner": str(service.owner) if service.owner else None,
                "criticality": service.criticality,
                "criticality_display": service.get_criticality_display(),
                "status": service.status,
                "status_display": service.get_status_display(),
                "rto_hours": service.rto_hours,
                "rpo_hours": service.rpo_hours,
                "mtpd_hours": service.mtpd_hours,
                "domain_impact_description": service.domain_impact_description,
                "assets": assets,
                "continuity_plans": plans,
                "tests": tests,
            }
        )


class ServiceAssetLinkViewSet(BaseModelViewSet):
    model = ServiceAssetLink
    filterset_fields = ["business_service", "asset", "dependency_type", "folder"]
    search_fields = ["business_service__name", "asset__name"]

    @method_decorator(cache_page(60 * LONG_CACHE_TTL))
    @action(detail=False, name="Get dependency type choices")
    def dependency_type(self, request):
        return Response(dict(ServiceAssetLink.DependencyType.choices))


class ContinuityPlanViewSet(BaseModelViewSet):
    model = ContinuityPlan
    filterset_fields = ["business_service", "status", "folder"]
    search_fields = ["name", "ref_id", "scenario"]

    @method_decorator(cache_page(60 * LONG_CACHE_TTL))
    @action(detail=False, name="Get status choices")
    def status(self, request):
        return Response(dict(ContinuityPlan.Status.choices))


class ContinuityPlanTestViewSet(BaseModelViewSet):
    model = ContinuityPlanTest
    filterset_fields = ["continuity_plan", "test_type", "result", "folder"]
    search_fields = ["continuity_plan__name", "findings"]
    ordering = ["-test_date"]

    @method_decorator(cache_page(60 * LONG_CACHE_TTL))
    @action(detail=False, name="Get test type choices")
    def test_type(self, request):
        return Response(dict(ContinuityPlanTest.TestType.choices))

    @method_decorator(cache_page(60 * LONG_CACHE_TTL))
    @action(detail=False, name="Get result choices")
    def result(self, request):
        return Response(dict(ContinuityPlanTest.Result.choices))


class AssetRecoveryProcedureViewSet(BaseModelViewSet):
    model = AssetRecoveryProcedure
    filterset_fields = ["asset", "procedure_type", "owner", "folder"]
    search_fields = ["name", "content"]

    @method_decorator(cache_page(60 * LONG_CACHE_TTL))
    @action(detail=False, name="Get procedure type choices")
    def procedure_type(self, request):
        return Response(dict(AssetRecoveryProcedure.ProcedureType.choices))
