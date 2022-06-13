from rest_framework import serializers
from . import models
from users.serializers import RelatedUserSerializer
import datetime

class GateSerializer(serializers.ModelSerializer):
    # 유저 객체 리턴
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

    def create_or_update(self):
        try:
            # 출근한 날짜와 유저 ID를 매칭하여, 출근 오브젝트 가져온다.
            gate = models.Gate.objects.get(user_id=self.validated_data.get('user_id'),
                                           pass_day=self.validated_data.get('check_time'))
            if gate is not None:
                models.InOutRecord.objects.create(**self.validated_data, gate=gate).save()

                # 퇴근일 경우, out_date 저장
                if self.validated_data.get('tag') == "OUT":
                    gate.out_date = self.validated_data.get('check_time')
                    gate.save()
                return gate
            else:
                return None
        # 해당 출근기록이 존재하지 않는다면
        except models.Gate.DoesNotExist:
            # 새로운 출근기록 생성
            gate = models.Gate.objects.create(
                user_id=self.validated_data.get('user_id'),
                pass_day=self.validated_data.get('check_time'),
                # 출근시간은 최초에 한번만 저장
                in_date=self.validated_data.get('check_time')
            )

            if gate is not None:
                # 해당 webhook에서 받은 기록 저장
                models.InOutRecord.objects.create(**self.validated_data, gate=gate).save()

                # 퇴근일 경우, 출근기록에 out_date 저장
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
