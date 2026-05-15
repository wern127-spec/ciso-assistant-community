from datetime import date

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from knox.models import AuthToken
from core.apps import startup
from core.models import Asset
from iam.models import User, UserGroup, Folder
from business_continuity.models import (
    BusinessService,
    ContinuityPlan,
    ContinuityPlanTest,
)

BASE = "/api/business-continuity"


@pytest.fixture
def admin_client(db):
    startup(sender=None)
    admin = User.objects.create_superuser("admin@tests.com", is_published=True)
    admin_group = UserGroup.objects.get(name="BI-UG-ADM")
    admin.folder = admin_group.folder
    admin.save()
    admin_group.user_set.add(admin)
    client = APIClient()
    token = AuthToken.objects.create(user=admin)[1]
    client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
    return client


@pytest.mark.django_db
class TestBusinessContinuityAPI:
    def test_list_endpoints_reachable(self, admin_client):
        for ep in [
            "business-services",
            "service-asset-links",
            "continuity-plans",
            "continuity-plan-tests",
            "asset-recovery-procedures",
        ]:
            r = admin_client.get(f"{BASE}/{ep}/")
            assert r.status_code == status.HTTP_200_OK, f"{ep}: {r.status_code}"

    def test_create_business_service(self, admin_client):
        folder = Folder.get_root_folder()
        r = admin_client.post(
            f"{BASE}/business-services/",
            {
                "name": "Service Desk",
                "folder": str(folder.id),
                "criticality": "critical",
                "status": "active",
                "rto_hours": 4,
            },
            format="json",
        )
        assert r.status_code == status.HTTP_201_CREATED, r.content
        assert BusinessService.objects.filter(name="Service Desk").exists()

    def test_choice_endpoints(self, admin_client):
        r = admin_client.get(f"{BASE}/business-services/criticality/")
        assert r.status_code == status.HTTP_200_OK
        assert "critical" in r.json()

        r = admin_client.get(f"{BASE}/continuity-plan-tests/result/")
        assert r.status_code == status.HTTP_200_OK
        assert "success" in r.json()

    def test_overview_endpoint(self, admin_client):
        folder = Folder.get_root_folder()
        svc = BusinessService.objects.create(
            name="Email Service",
            folder=folder,
            criticality=BusinessService.Criticality.HIGH,
            rto_hours=2,
            rpo_hours=1,
        )
        asset = Asset.objects.create(name="Mail Server", folder=folder)
        admin_client.post(
            f"{BASE}/service-asset-links/",
            {
                "business_service": str(svc.id),
                "asset": str(asset.id),
                "folder": str(folder.id),
                "dependency_type": "critical",
                "asset_impact_description": "Core mail flow",
            },
            format="json",
        )
        plan = ContinuityPlan.objects.create(
            name="Email DR", folder=folder, business_service=svc, scenario="DC outage"
        )
        ContinuityPlanTest.objects.create(
            continuity_plan=plan,
            folder=folder,
            test_date=date(2026, 2, 1),
            test_type=ContinuityPlanTest.TestType.SIMULATION,
            result=ContinuityPlanTest.Result.SUCCESS,
        )

        r = admin_client.get(f"{BASE}/business-services/{svc.id}/overview/")
        assert r.status_code == status.HTTP_200_OK, r.content
        data = r.json()
        assert data["name"] == "Email Service"
        assert data["domain"]["name"] == folder.name
        assert data["rto_hours"] == 2
        assert len(data["assets"]) == 1
        assert data["assets"][0]["dependency_type"] == "critical"
        assert len(data["continuity_plans"]) == 1
        assert len(data["tests"]) == 1
        assert data["tests"][0]["result"] == "success"
