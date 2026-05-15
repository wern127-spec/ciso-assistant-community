from rest_framework import serializers

from core.serializers import BaseModelSerializer
from core.serializer_fields import FieldsRelatedField

from .models import (
    BusinessService,
    ServiceAssetLink,
    ContinuityPlan,
    ContinuityPlanTest,
    AssetRecoveryProcedure,
)


class BusinessServiceReadSerializer(BaseModelSerializer):
    str = serializers.CharField(source="__str__")
    folder = FieldsRelatedField()
    owner = FieldsRelatedField(["id", "email", "first_name", "last_name"])
    criticality = serializers.CharField(source="get_criticality_display")
    status = serializers.CharField(source="get_status_display")

    class Meta:
        model = BusinessService
        exclude = ["assets"]


class BusinessServiceWriteSerializer(BaseModelSerializer):
    class Meta:
        model = BusinessService
        exclude = ["assets"]


class ServiceAssetLinkReadSerializer(BaseModelSerializer):
    str = serializers.CharField(source="__str__")
    folder = FieldsRelatedField()
    business_service = FieldsRelatedField()
    asset = FieldsRelatedField(["id", "name", "folder"])
    dependency_type = serializers.CharField(source="get_dependency_type_display")

    class Meta:
        model = ServiceAssetLink
        exclude = []


class ServiceAssetLinkWriteSerializer(BaseModelSerializer):
    class Meta:
        model = ServiceAssetLink
        fields = "__all__"


class AssetRecoveryProcedureReadSerializer(BaseModelSerializer):
    str = serializers.CharField(source="__str__")
    folder = FieldsRelatedField()
    asset = FieldsRelatedField(["id", "name", "folder"])
    owner = FieldsRelatedField(["id", "email", "first_name", "last_name"])
    evidence = FieldsRelatedField()
    procedure_type = serializers.CharField(source="get_procedure_type_display")

    class Meta:
        model = AssetRecoveryProcedure
        exclude = []


class AssetRecoveryProcedureWriteSerializer(BaseModelSerializer):
    class Meta:
        model = AssetRecoveryProcedure
        fields = "__all__"


class ContinuityPlanReadSerializer(BaseModelSerializer):
    str = serializers.CharField(source="__str__")
    folder = FieldsRelatedField()
    business_service = FieldsRelatedField()
    referenced_asset_procedures = FieldsRelatedField(many=True)
    status = serializers.CharField(source="get_status_display")

    class Meta:
        model = ContinuityPlan
        exclude = []


class ContinuityPlanWriteSerializer(BaseModelSerializer):
    class Meta:
        model = ContinuityPlan
        fields = "__all__"


class ContinuityPlanTestReadSerializer(BaseModelSerializer):
    str = serializers.CharField(source="__str__")
    folder = FieldsRelatedField()
    continuity_plan = FieldsRelatedField()
    evidence = FieldsRelatedField()
    test_type = serializers.CharField(source="get_test_type_display")
    result = serializers.CharField(source="get_result_display")

    class Meta:
        model = ContinuityPlanTest
        exclude = []


class ContinuityPlanTestWriteSerializer(BaseModelSerializer):
    class Meta:
        model = ContinuityPlanTest
        fields = "__all__"
