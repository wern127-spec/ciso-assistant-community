from datetime import date

import pytest

from iam.models import Folder
from core.models import Asset, Evidence
from business_continuity.models import (
    BusinessService,
    ServiceAssetLink,
    ContinuityPlan,
    ContinuityPlanTest,
    AssetRecoveryProcedure,
)


@pytest.mark.django_db
class TestBusinessContinuityModels:
    def _folder(self):
        return Folder.get_root_folder()

    def test_create_business_service(self):
        folder = self._folder()
        svc = BusinessService.objects.create(
            name="Service Desk",
            folder=folder,
            criticality=BusinessService.Criticality.CRITICAL,
            rto_hours=4,
            rpo_hours=1,
            mtpd_hours=24,
            status=BusinessService.Status.ACTIVE,
        )
        assert svc.pk is not None
        assert svc.criticality == "critical"
        assert str(svc) == "Service Desk"

    def test_link_two_assets(self):
        folder = self._folder()
        svc = BusinessService.objects.create(name="Email Service", folder=folder)
        asset1 = Asset.objects.create(name="Mail Server", folder=folder)
        asset2 = Asset.objects.create(name="LDAP", folder=folder)

        ServiceAssetLink.objects.create(
            business_service=svc,
            asset=asset1,
            folder=folder,
            dependency_type=ServiceAssetLink.DependencyType.CRITICAL,
            asset_impact_description="Without it no mail flows",
        )
        ServiceAssetLink.objects.create(
            business_service=svc,
            asset=asset2,
            folder=folder,
            dependency_type=ServiceAssetLink.DependencyType.SUPPORTING,
        )

        assert svc.asset_links.count() == 2
        assert svc.assets.count() == 2
        assert asset1.business_services.first() == svc

    def test_create_continuity_plan(self):
        folder = self._folder()
        svc = BusinessService.objects.create(name="Payroll", folder=folder)
        plan = ContinuityPlan.objects.create(
            name="Payroll DR Plan",
            folder=folder,
            business_service=svc,
            scenario="Datacenter outage",
            recovery_strategy="Failover to DR site",
            status=ContinuityPlan.Status.APPROVED,
        )
        assert plan.pk is not None
        assert svc.continuity_plans.first() == plan

    def test_create_continuity_plan_test(self):
        folder = self._folder()
        svc = BusinessService.objects.create(name="CRM", folder=folder)
        plan = ContinuityPlan.objects.create(
            name="CRM Plan", folder=folder, business_service=svc
        )
        test = ContinuityPlanTest.objects.create(
            continuity_plan=plan,
            folder=folder,
            test_date=date(2026, 1, 15),
            test_type=ContinuityPlanTest.TestType.SIMULATION,
            result=ContinuityPlanTest.Result.SUCCESS,
            findings="All targets met",
        )
        assert test.pk is not None
        assert plan.tests.first() == test
        assert test.result == "success"

    def test_create_asset_recovery_procedure_and_reference(self):
        folder = self._folder()
        asset = Asset.objects.create(name="DB Cluster", folder=folder)
        evidence = Evidence.objects.create(name="Backup log", folder=folder)
        proc = AssetRecoveryProcedure.objects.create(
            name="DB Restore Procedure",
            folder=folder,
            asset=asset,
            procedure_type=AssetRecoveryProcedure.ProcedureType.RESTORE,
            content="1. Stop DB\n2. Restore snapshot",
            evidence=evidence,
        )
        assert proc.pk is not None
        assert asset.recovery_procedures.first() == proc

        svc = BusinessService.objects.create(name="Reporting", folder=folder)
        plan = ContinuityPlan.objects.create(
            name="Reporting Plan", folder=folder, business_service=svc
        )
        plan.referenced_asset_procedures.add(proc)
        assert plan.referenced_asset_procedures.count() == 1
        assert proc.continuity_plans.first() == plan
