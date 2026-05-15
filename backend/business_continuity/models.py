from django.db import models
from django.utils.translation import gettext_lazy as _
from auditlog.registry import auditlog

from iam.models import FolderMixin
from core.base_models import AbstractBaseModel, NameDescriptionMixin


class BusinessService(NameDescriptionMixin, FolderMixin):
    """
    Central unit of business continuity (service-centric approach).
    A service belongs to exactly one domain (folder) and aggregates
    the assets, continuity plans and tests that keep it running.
    """

    class Criticality(models.TextChoices):
        CRITICAL = "critical", _("Critical")
        HIGH = "high", _("High")
        MEDIUM = "medium", _("Medium")
        LOW = "low", _("Low")

    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        ACTIVE = "active", _("Active")
        DEPRECATED = "deprecated", _("Deprecated")

    ref_id = models.CharField(
        max_length=100, blank=True, verbose_name=_("Reference ID")
    )
    owner = models.ForeignKey(
        "iam.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_business_services",
        verbose_name=_("Owner"),
    )
    criticality = models.CharField(
        max_length=20,
        choices=Criticality.choices,
        default=Criticality.MEDIUM,
        verbose_name=_("Criticality"),
    )
    rto_hours = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_("RTO (hours)"),
        help_text=_("Recovery Time Objective in hours"),
    )
    rpo_hours = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_("RPO (hours)"),
        help_text=_("Recovery Point Objective in hours"),
    )
    mtpd_hours = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_("MTPD (hours)"),
        help_text=_("Maximum Tolerable Period of Disruption in hours"),
    )
    domain_impact_description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Domain impact description"),
        help_text=_("How this service impacts its domain"),
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name=_("Status"),
    )

    assets = models.ManyToManyField(
        "core.Asset",
        through="ServiceAssetLink",
        related_name="business_services",
        blank=True,
        verbose_name=_("Assets"),
    )

    class Meta:
        verbose_name = _("Business service")
        verbose_name_plural = _("Business services")

    def __str__(self) -> str:
        return self.name


class ServiceAssetLink(AbstractBaseModel, FolderMixin):
    """
    M:N link between a BusinessService and a technical Asset, carrying
    the nature of the dependency and its impact on the service.
    """

    class DependencyType(models.TextChoices):
        CRITICAL = "critical", _("Critical")
        IMPORTANT = "important", _("Important")
        SUPPORTING = "supporting", _("Supporting")

    business_service = models.ForeignKey(
        BusinessService,
        on_delete=models.CASCADE,
        related_name="asset_links",
        verbose_name=_("Business service"),
    )
    asset = models.ForeignKey(
        "core.Asset",
        on_delete=models.CASCADE,
        related_name="service_links",
        verbose_name=_("Asset"),
    )
    dependency_type = models.CharField(
        max_length=20,
        choices=DependencyType.choices,
        default=DependencyType.IMPORTANT,
        verbose_name=_("Dependency type"),
    )
    asset_impact_description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Asset impact description"),
        help_text=_("How this asset impacts this service"),
    )
    notes = models.TextField(null=True, blank=True, verbose_name=_("Notes"))

    class Meta:
        verbose_name = _("Service-asset link")
        verbose_name_plural = _("Service-asset links")
        unique_together = ["business_service", "asset"]

    def __str__(self) -> str:
        return f"{self.business_service} ↔ {self.asset}"


class AssetRecoveryProcedure(NameDescriptionMixin, FolderMixin):
    """
    Technical recovery document attached to a single Asset. A continuity
    plan may reference one or more of these procedures.
    """

    class ProcedureType(models.TextChoices):
        BACKUP = "backup", _("Backup")
        RESTORE = "restore", _("Restore")
        FAILOVER = "failover", _("Failover")
        HARDENING = "hardening", _("Hardening")
        MONITORING = "monitoring", _("Monitoring")

    asset = models.ForeignKey(
        "core.Asset",
        on_delete=models.CASCADE,
        related_name="recovery_procedures",
        verbose_name=_("Asset"),
    )
    procedure_type = models.CharField(
        max_length=20,
        choices=ProcedureType.choices,
        default=ProcedureType.BACKUP,
        verbose_name=_("Procedure type"),
    )
    content = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Content"),
        help_text=_("Procedure content (markdown)"),
    )
    version = models.CharField(
        max_length=50, blank=True, default="1.0", verbose_name=_("Version")
    )
    last_updated = models.DateField(
        null=True, blank=True, verbose_name=_("Last updated")
    )
    owner = models.ForeignKey(
        "iam.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_recovery_procedures",
        verbose_name=_("Owner"),
    )
    evidence = models.ForeignKey(
        "core.Evidence",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recovery_procedures",
        verbose_name=_("Evidence"),
    )

    class Meta:
        verbose_name = _("Asset recovery procedure")
        verbose_name_plural = _("Asset recovery procedures")

    def __str__(self) -> str:
        return f"{self.name} ({self.asset})"


class ContinuityPlan(NameDescriptionMixin, FolderMixin):
    """
    Business continuity plan. Always belongs to a BusinessService.
    """

    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        APPROVED = "approved", _("Approved")
        ARCHIVED = "archived", _("Archived")

    business_service = models.ForeignKey(
        BusinessService,
        on_delete=models.CASCADE,
        related_name="continuity_plans",
        verbose_name=_("Business service"),
    )
    ref_id = models.CharField(
        max_length=100, blank=True, verbose_name=_("Reference ID")
    )
    version = models.CharField(
        max_length=50, blank=True, default="1.0", verbose_name=_("Version")
    )
    scenario = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Scenario"),
        help_text=_("Disaster scenario this plan addresses"),
    )
    recovery_strategy = models.TextField(
        null=True, blank=True, verbose_name=_("Recovery strategy")
    )
    procedure_steps = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Procedure steps"),
        help_text=_("Step-by-step procedure (markdown)"),
    )
    responsible_team = models.TextField(
        null=True, blank=True, verbose_name=_("Responsible team")
    )
    last_review_date = models.DateField(
        null=True, blank=True, verbose_name=_("Last review date")
    )
    next_review_date = models.DateField(
        null=True, blank=True, verbose_name=_("Next review date")
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name=_("Status"),
    )
    referenced_asset_procedures = models.ManyToManyField(
        AssetRecoveryProcedure,
        blank=True,
        related_name="continuity_plans",
        verbose_name=_("Referenced asset procedures"),
    )

    class Meta:
        verbose_name = _("Continuity plan")
        verbose_name_plural = _("Continuity plans")

    def __str__(self) -> str:
        return self.name


class ContinuityPlanTest(AbstractBaseModel, FolderMixin):
    """
    A test/exercise of a ContinuityPlan.
    """

    class TestType(models.TextChoices):
        TABLETOP = "tabletop", _("Tabletop")
        WALKTHROUGH = "walkthrough", _("Walkthrough")
        SIMULATION = "simulation", _("Simulation")
        FULL_RECOVERY = "full_recovery", _("Full recovery")

    class Result(models.TextChoices):
        SUCCESS = "success", _("Success")
        PARTIAL = "partial", _("Partial")
        FAILURE = "failure", _("Failure")

    continuity_plan = models.ForeignKey(
        ContinuityPlan,
        on_delete=models.CASCADE,
        related_name="tests",
        verbose_name=_("Continuity plan"),
    )
    test_date = models.DateField(verbose_name=_("Test date"))
    test_type = models.CharField(
        max_length=20,
        choices=TestType.choices,
        default=TestType.TABLETOP,
        verbose_name=_("Test type"),
    )
    participants = models.TextField(
        null=True, blank=True, verbose_name=_("Participants")
    )
    objectives = models.TextField(
        null=True, blank=True, verbose_name=_("Objectives")
    )
    result = models.CharField(
        max_length=20,
        choices=Result.choices,
        default=Result.PARTIAL,
        verbose_name=_("Result"),
    )
    findings = models.TextField(null=True, blank=True, verbose_name=_("Findings"))
    actions = models.TextField(null=True, blank=True, verbose_name=_("Actions"))
    evidence = models.ForeignKey(
        "core.Evidence",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="continuity_plan_tests",
        verbose_name=_("Evidence"),
    )

    class Meta:
        verbose_name = _("Continuity plan test")
        verbose_name_plural = _("Continuity plan tests")
        ordering = ["-test_date"]

    def __str__(self) -> str:
        return f"{self.continuity_plan} — {self.test_date}"


common_exclude = ["created_at", "updated_at"]
auditlog.register(BusinessService, exclude_fields=common_exclude)
auditlog.register(ServiceAssetLink, exclude_fields=common_exclude)
auditlog.register(AssetRecoveryProcedure, exclude_fields=common_exclude)
auditlog.register(ContinuityPlan, exclude_fields=common_exclude)
auditlog.register(ContinuityPlanTest, exclude_fields=common_exclude)
