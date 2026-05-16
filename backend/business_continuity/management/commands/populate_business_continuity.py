"""
Demo data for the Business Continuity module.

Creates two realistic business services (Service Desk, Email Service) with
linked assets, recovery procedures, a continuity plan and a test history each,
so the aggregate service view can be shown "from real life".

Idempotent: everything is created under a dedicated demo domain folder; running
again (or with --fresh) wipes the previous demo data first.

    python manage.py populate_business_continuity
    python manage.py populate_business_continuity --fresh
    python manage.py populate_business_continuity --clean
"""

from datetime import date, timedelta

from django.core.management.base import BaseCommand

from core.models import Asset
from iam.models import Folder, User

from business_continuity.models import (
    AssetRecoveryProcedure,
    BusinessService,
    ContinuityPlan,
    ContinuityPlanTest,
    ServiceAssetLink,
)

DEMO_FOLDER_NAME = "BC Demo - IT Operations"


class Command(BaseCommand):
    help = "Populates realistic demo data for the Business Continuity module"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clean",
            action="store_true",
            help="Delete the demo data only (do not recreate it)",
        )
        parser.add_argument(
            "--fresh",
            action="store_true",
            help="Delete existing demo data and recreate it (default behaviour)",
        )

    # ------------------------------------------------------------------ #
    def _wipe(self):
        folder = Folder.objects.filter(name=DEMO_FOLDER_NAME).first()
        if not folder:
            return 0
        # Children cascade on folder delete; assets live in the demo folder too.
        Asset.objects.filter(folder=folder).delete()
        folder.delete()
        return 1

    # ------------------------------------------------------------------ #
    def handle(self, *args, **options):
        if options["clean"] or options["fresh"]:
            n = self._wipe()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Removed previous demo data ({n} demo domain)."
                )
            )
            if options["clean"]:
                self.stdout.write(self.style.SUCCESS("Clean done. Nothing created."))
                return
        else:
            # default run is also idempotent
            self._wipe()

        root = Folder.get_root_folder()
        owner = User.objects.filter(is_active=True).order_by("id").first()

        domain = Folder.objects.create(
            name=DEMO_FOLDER_NAME,
            description="Demo domain showcasing the Business Continuity module.",
            parent_folder=root,
            content_type=Folder.ContentType.DOMAIN,
        )
        self.stdout.write(f"Created demo domain: {domain.name}")

        today = date.today()

        # ============================================================== #
        # SERVICE 1 — Service Desk
        # ============================================================== #
        service_desk = BusinessService.objects.create(
            folder=domain,
            name="Service Desk",
            ref_id="BS-001",
            description="Single point of contact for all IT incident and request handling.",
            owner=owner,
            criticality=BusinessService.Criticality.HIGH,
            status=BusinessService.Status.ACTIVE,
            rto_hours=4,
            rpo_hours=2,
            mtpd_hours=8,
            domain_impact_description=(
                "## Impact on the organisation\n\n"
                "If the Service Desk is unavailable:\n\n"
                "- Employees **cannot report incidents**, slowing recovery of every other service.\n"
                "- SLA breaches accumulate quickly with **financial penalties**.\n"
                "- Visible drop in user satisfaction and trust in IT.\n\n"
                "The Service Desk is a *force multiplier* — its outage amplifies the impact "
                "of any other concurrent incident."
            ),
        )

        sd_ticketing = Asset.objects.create(
            folder=domain,
            name="Ticketing System (Jira Service Management)",
            description="Core ITSM platform recording all incidents and requests.",
            type=Asset.Type.PRIMARY,
            ref_id="DEMO-AST-0001",
        )
        sd_telephony = Asset.objects.create(
            folder=domain,
            name="Telephony / Call Centre Platform",
            description="Inbound phone line and call distribution for the Service Desk.",
            type=Asset.Type.SUPPORT,
            ref_id="DEMO-AST-0002",
        )
        sd_kb = Asset.objects.create(
            folder=domain,
            name="Knowledge Base (Confluence)",
            description="Self-service articles and agent runbooks.",
            type=Asset.Type.SUPPORT,
            ref_id="DEMO-AST-0003",
        )

        ServiceAssetLink.objects.create(
            folder=domain,
            business_service=service_desk,
            asset=sd_ticketing,
            dependency_type=ServiceAssetLink.DependencyType.CRITICAL,
            asset_impact_description="Without ticketing, no incident can be tracked or prioritised.",
        )
        ServiceAssetLink.objects.create(
            folder=domain,
            business_service=service_desk,
            asset=sd_telephony,
            dependency_type=ServiceAssetLink.DependencyType.IMPORTANT,
            asset_impact_description="Loss of phone channel; users fall back to email/portal only.",
        )
        ServiceAssetLink.objects.create(
            folder=domain,
            business_service=service_desk,
            asset=sd_kb,
            dependency_type=ServiceAssetLink.DependencyType.SUPPORTING,
            asset_impact_description="Agents lose runbooks; resolution time increases.",
        )

        AssetRecoveryProcedure.objects.create(
            folder=domain,
            asset=sd_ticketing,
            name="Restore Ticketing System from backup",
            description="Step-by-step restore of the ITSM database and application node.",
            procedure_type=AssetRecoveryProcedure.ProcedureType.RESTORE,
            version="1.2",
            last_updated=today - timedelta(days=30),
            owner=owner,
            content=(
                "1. Provision a clean application node.\n"
                "2. Restore the latest **nightly database snapshot**.\n"
                "3. Replay transaction logs up to the last consistent point.\n"
                "4. Smoke-test login and ticket creation.\n"
                "5. Re-point the load balancer to the restored node."
            ),
        )
        AssetRecoveryProcedure.objects.create(
            folder=domain,
            asset=sd_telephony,
            name="Failover to backup telephony provider",
            description="Switch inbound numbers to the secondary SIP trunk.",
            procedure_type=AssetRecoveryProcedure.ProcedureType.FAILOVER,
            version="1.0",
            last_updated=today - timedelta(days=60),
            owner=owner,
            content=(
                "1. Open the carrier portal.\n"
                "2. Redirect the main hotline to the **backup SIP trunk**.\n"
                "3. Verify a test call is routed to an agent queue."
            ),
        )
        AssetRecoveryProcedure.objects.create(
            folder=domain,
            asset=sd_kb,
            name="Knowledge Base read-only mirror",
            description="Bring up the static read-only mirror of the KB.",
            procedure_type=AssetRecoveryProcedure.ProcedureType.BACKUP,
            version="1.0",
            last_updated=today - timedelta(days=15),
            owner=owner,
            content="Publish the latest static export to the standby web server.",
        )

        sd_plan = ContinuityPlan.objects.create(
            folder=domain,
            business_service=service_desk,
            name="Service Desk Continuity Plan",
            ref_id="CP-001",
            version="2.0",
            description="Continuity plan covering Service Desk outage scenarios.",
            responsible_team="IT Operations / Service Management",
            status=ContinuityPlan.Status.APPROVED,
            last_review_date=today - timedelta(days=90),
            next_review_date=today + timedelta(days=275),
            scenario=(
                "## Scenario\n\n"
                "Primary data centre hosting the ticketing system becomes "
                "**unavailable** (power or network loss) during business hours."
            ),
            recovery_strategy=(
                "## Recovery strategy\n\n"
                "- Activate the **warm standby** ticketing node in the secondary site.\n"
                "- Switch the call centre to the backup SIP trunk.\n"
                "- Communicate the alternate portal URL to all staff."
            ),
            procedure_steps=(
                "1. Incident Manager declares a continuity event.\n"
                "2. Execute *Restore Ticketing System from backup*.\n"
                "3. Execute *Failover to backup telephony provider*.\n"
                "4. Announce service restoration and start backlog catch-up."
            ),
        )

        ContinuityPlanTest.objects.create(
            folder=domain,
            continuity_plan=sd_plan,
            test_date=today - timedelta(days=300),
            test_type=ContinuityPlanTest.TestType.TABLETOP,
            participants="Service Management, IT Ops, Incident Manager",
            objectives="Validate roles and decision flow during a Service Desk outage.",
            result=ContinuityPlanTest.Result.PARTIAL,
            findings="Escalation contact list was outdated.",
            actions="Updated on-call roster; added quarterly review.",
        )
        ContinuityPlanTest.objects.create(
            folder=domain,
            continuity_plan=sd_plan,
            test_date=today - timedelta(days=150),
            test_type=ContinuityPlanTest.TestType.WALKTHROUGH,
            participants="IT Ops, Telephony vendor",
            objectives="Walk through telephony failover procedure end to end.",
            result=ContinuityPlanTest.Result.SUCCESS,
            findings="Failover completed within target.",
            actions="None.",
        )
        ContinuityPlanTest.objects.create(
            folder=domain,
            continuity_plan=sd_plan,
            test_date=today - timedelta(days=20),
            test_type=ContinuityPlanTest.TestType.SIMULATION,
            participants="Full IT Operations team",
            objectives="Simulate full data-centre loss and recover within RTO (4h).",
            result=ContinuityPlanTest.Result.SUCCESS,
            findings="Recovered in 3h10m, within RTO.",
            actions="Document optimisation of the DB restore step.",
        )

        # ============================================================== #
        # SERVICE 2 — Email Service
        # ============================================================== #
        email = BusinessService.objects.create(
            folder=domain,
            name="Email Service",
            ref_id="BS-002",
            description="Corporate email and calendaring for all employees.",
            owner=owner,
            criticality=BusinessService.Criticality.CRITICAL,
            status=BusinessService.Status.ACTIVE,
            rto_hours=2,
            rpo_hours=1,
            mtpd_hours=4,
            domain_impact_description=(
                "## Impact on the organisation\n\n"
                "Email is the **primary communication channel**. An outage:\n\n"
                "- Stops internal and customer communication.\n"
                "- Blocks workflows that rely on email approvals.\n"
                "- Damages reputation if customer messages bounce."
            ),
        )

        em_mailbox = Asset.objects.create(
            folder=domain,
            name="Mailbox Servers (Exchange cluster)",
            description="Clustered mailbox storage and transport.",
            type=Asset.Type.PRIMARY,
            ref_id="DEMO-AST-0004",
        )
        em_gateway = Asset.objects.create(
            folder=domain,
            name="Mail Gateway / Anti-spam",
            description="Inbound/outbound mail filtering and routing.",
            type=Asset.Type.SUPPORT,
            ref_id="DEMO-AST-0005",
        )

        ServiceAssetLink.objects.create(
            folder=domain,
            business_service=email,
            asset=em_mailbox,
            dependency_type=ServiceAssetLink.DependencyType.CRITICAL,
            asset_impact_description="No mailbox cluster means total loss of email.",
        )
        ServiceAssetLink.objects.create(
            folder=domain,
            business_service=email,
            asset=em_gateway,
            dependency_type=ServiceAssetLink.DependencyType.IMPORTANT,
            asset_impact_description="Without the gateway, external mail flow stops.",
        )

        AssetRecoveryProcedure.objects.create(
            folder=domain,
            asset=em_mailbox,
            name="Mailbox cluster failover",
            description="Promote the passive mailbox node and remount databases.",
            procedure_type=AssetRecoveryProcedure.ProcedureType.FAILOVER,
            version="2.1",
            last_updated=today - timedelta(days=10),
            owner=owner,
            content=(
                "1. Confirm the active node is unhealthy.\n"
                "2. Trigger **cluster failover** to the passive node.\n"
                "3. Mount databases and verify mail flow.\n"
                "4. Monitor replication health."
            ),
        )
        AssetRecoveryProcedure.objects.create(
            folder=domain,
            asset=em_gateway,
            name="Restore mail gateway configuration",
            description="Rebuild the gateway from the configuration backup.",
            procedure_type=AssetRecoveryProcedure.ProcedureType.RESTORE,
            version="1.3",
            last_updated=today - timedelta(days=45),
            owner=owner,
            content="Deploy a fresh gateway and import the latest config backup.",
        )

        em_plan = ContinuityPlan.objects.create(
            folder=domain,
            business_service=email,
            name="Email Service Continuity Plan",
            ref_id="CP-002",
            version="1.5",
            description="Continuity plan for corporate email outages.",
            responsible_team="Messaging Team / IT Operations",
            status=ContinuityPlan.Status.APPROVED,
            last_review_date=today - timedelta(days=120),
            next_review_date=today + timedelta(days=245),
            scenario=(
                "## Scenario\n\n"
                "Active mailbox node fails and the **anti-spam gateway** is "
                "simultaneously degraded."
            ),
            recovery_strategy=(
                "## Recovery strategy\n\n"
                "- Fail over the mailbox cluster to the passive node.\n"
                "- Rebuild the mail gateway from backup.\n"
                "- Use the cloud relay for outbound mail in the meantime."
            ),
            procedure_steps=(
                "1. Declare an email continuity event.\n"
                "2. Execute *Mailbox cluster failover*.\n"
                "3. Execute *Restore mail gateway configuration*.\n"
                "4. Confirm inbound and outbound flow, then close the event."
            ),
        )

        ContinuityPlanTest.objects.create(
            folder=domain,
            continuity_plan=em_plan,
            test_date=today - timedelta(days=200),
            test_type=ContinuityPlanTest.TestType.SIMULATION,
            participants="Messaging Team, IT Ops",
            objectives="Simulate active mailbox node failure.",
            result=ContinuityPlanTest.Result.SUCCESS,
            findings="Failover within RTO (2h).",
            actions="None.",
        )
        ContinuityPlanTest.objects.create(
            folder=domain,
            continuity_plan=em_plan,
            test_date=today - timedelta(days=40),
            test_type=ContinuityPlanTest.TestType.FULL_RECOVERY,
            participants="Messaging Team, IT Ops, Security",
            objectives="Full recovery of mailbox + gateway from backups.",
            result=ContinuityPlanTest.Result.FAILURE,
            findings="Gateway config backup was 2 weeks stale; rules missing.",
            actions="Automated daily gateway config backup; re-test scheduled.",
        )

        # ============================================================== #
        self.stdout.write(self.style.SUCCESS("\nDemo data created:"))
        self.stdout.write(f"  Domain:             {domain.name}")
        self.stdout.write(
            f"  Business services:  {BusinessService.objects.filter(folder=domain).count()}"
        )
        self.stdout.write(
            f"  Assets:             {Asset.objects.filter(folder=domain).count()}"
        )
        self.stdout.write(
            f"  Recovery procedures:{AssetRecoveryProcedure.objects.filter(folder=domain).count()}"
        )
        self.stdout.write(
            f"  Continuity plans:   {ContinuityPlan.objects.filter(folder=domain).count()}"
        )
        self.stdout.write(
            f"  Plan tests:         {ContinuityPlanTest.objects.filter(folder=domain).count()}"
        )
        self.stdout.write(
            self.style.SUCCESS(
                "\nOpen any service from the Business services list to see the aggregate view."
            )
        )
