from collections import defaultdict
from radar.lib.foo import PatientMixin, Validator, Field, required, FacilityMixin, optional
from radar.lib.serializers import MetaSerializerMixin, FacilitySerializerMixin, ModelSerializer, PatientSerializerMixin, LookupField, \
    ValidationError
from radar.lib.views import FacilityDataMixin, PatientDataList, PatientDataDetail, ListView
from radar.models import Dialysis, DialysisType


class DialysisTypeLookupField(LookupField):
    model_class = DialysisType


class DialysisTypeSerializer(ModelSerializer):
    class Meta:
        model_class = DialysisType


class DialysisValidator(PatientMixin, FacilityMixin, Validator):
    from_date = Field(chain=[required])
    to_date = Field(chain=[optional])
    dialysis_type = Field(chain=[required])

    def validate(self, obj):
        errors = defaultdict(list)

        if obj.to_date and obj.to_date < obj.from_date:
            errors['to_date'].append('Must be on or after from date.')

        if errors:
            raise ValidationError(errors)

        return obj


class DialysisSerializer(MetaSerializerMixin, PatientSerializerMixin, FacilitySerializerMixin, ModelSerializer):
    dialysis_type = DialysisTypeSerializer(read_only=True)
    dialysis_type_id = DialysisTypeLookupField(write_only=True)

    class Meta:
        model_class = Dialysis


class DialysisList(FacilityDataMixin, PatientDataList):
    serializer_class = DialysisSerializer
    validator_class = DialysisValidator

    def get_query(self):
        return Dialysis.query


class DialysisDetail(FacilityDataMixin, PatientDataDetail):
    serializer_class = DialysisSerializer
    validator_class = DialysisValidator

    def get_query(self):
        return Dialysis.query


class DialysisTypeList(ListView):
    serializer_class = DialysisTypeSerializer

    def get_query(self):
        return DialysisType.query
