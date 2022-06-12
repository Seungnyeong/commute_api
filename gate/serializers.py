from rest_framework import serializers
from . import models
from users.serializers import RelatedUserSerializer
import datetime

class GateSerializer(serializers.ModelSerializer):
    user = RelatedUserSerializer(read_only=True)
    class Meta:
        fields = (

            'id',
            'pass_day',
            'in_date',
            'out_date',
            'work_time',
            'break_time',
            'user',
        )
        model = models.Gate


class GateWebHookSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    tag = serializers.CharField()
    check_time = serializers.DateTimeField()

    def validate(self, data):
        return data

    def create_or_update(self):
        try:
            gate = models.Gate.objects.get(user_id=self.validated_data.get('user_id'),
                                           pass_day=self.validated_data.get('check_time'))
            if gate is not None:
                models.InOutRecord.objects.create(**self.validated_data, gate=gate).save()

                if self.validated_data.get('tag') == "OUT":
                    gate.out_date = self.validated_data.get('check_time')
                    gate.save()
                return gate
            else:
                return None
        except models.Gate.DoesNotExist:
            gate = models.Gate.objects.create(
                user_id=self.validated_data.get('user_id'),
                pass_day=self.validated_data.get('check_time'),
                in_date=self.validated_data.get('check_time')
            )

            if gate is not None:
                models.InOutRecord.objects.create(**self.validated_data, gate=gate).save()
                if self.validated_data.get('tag') == "OUT":
                    gate.out_date = self.validated_data.get('check_time')
                    gate.save()
                return gate
            else:
                return None


class GateGetQuerySerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    pass_day = serializers.DateField(input_formats=['%Y-%m-%d'], default=datetime.date.today())

    def get_gate(self):
        try:
            return models.Gate.objects.get(**self.validated_data)
        except models.Gate.DoesNotExist:
            return None
