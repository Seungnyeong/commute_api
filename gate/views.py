from .serializers import GateSerializer, GateWebHookSerializer, GateGetQuerySerializer

from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN, \
    HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from .models import InOutRecord, Gate
from django.db.models import Max
from datetime import datetime


# Create your views here.
class GateAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        request_body=GateWebHookSerializer,
        operation_description="출퇴근 WebHook",
        operation_summary="게이트웨이에서 출근시, 해당 API 호출하여 데이터 적재",
        deprecated=False,
        tags=['출퇴근 WebHook']
    )
    def post(self, request):
        today = datetime.today()
        serializer = GateWebHookSerializer(data=request.data)
        if serializer.is_valid():
            # 출근 오브젝트 생성 및, 출퇴근 기록 오브젝트 생성
            gate = serializer.create_or_update()

            # 카드를 찍은 시간
            check_time = serializer.validated_data.get('check_time')

            # 휴식 시간 저장
            if serializer.validated_data.get('tag') == "IN" and gate.out_date is not None:
                gate.break_time = gate.break_time + int((check_time - gate.out_date).seconds // 60)
                gate.save()

            # 휴식시간 저장
            elif serializer.validated_data.get('tag') == "OUT" and gate.in_date is not None:

                # 금일 날짜의, 최근 IN 태그를 가져온다. 사용자가 태그를 안찍을 수도 있기 때문에  금일날짜를 넣는다.
                last_in_date = InOutRecord.objects.filter(
                    user_id=serializer.validated_data.get('user_id'),
                    tag__exact="IN",
                    check_time__year=today.year,
                    check_time__month=today.month,
                    check_time__day=today.day
                ).aggregate(Max('check_time')).get('check_time__max')
                if last_in_date is not None:
                    if (
                            last_in_date.year == check_time.year and
                            last_in_date.month == check_time.month and
                            last_in_date.day == check_time.day
                    ):
                        # 휴식시간 저장
                        gate.work_time = gate.work_time + int((check_time - last_in_date).seconds // 60)
                        gate.save()
            return Response(status=HTTP_201_CREATED)
        else:
            return Response(status=HTTP_400_BAD_REQUEST, data=serializer.errors)


class GateDetailAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        request_body=GateSerializer(),
        operation_description="출입 기록 수정 API, user 수정 불가",
        operation_summary="출입 기록 수정",
        deprecated=False,
        tags=['출입기록']
    )
    def put(self, request, id):
        try:
            gate = Gate.objects.get(id=id)
        except Gate.DoesNotExist:
            gate = None

        if gate is not None:

            # 부분적으로 수정 가능
            serializer = GateSerializer(
                gate, data=request.data, partial=True
            )
            if serializer.is_valid():
                gate = serializer.save()
                return Response(GateSerializer(gate).data)
            else:
                return Response(data=serializer.errors, status=HTTP_400_BAD_REQUEST)
        else:
            return Response(status=HTTP_404_NOT_FOUND, data={
                "detail": "출근 기록이 없습니다."
            })

    @swagger_auto_schema(
        operation_description="관리자 권한에 의하여, 삭제할 수 있음.",
        operation_summary="출입 기록 삭제",
        deprecated=False,
        tags=['출입기록']
    )
    def delete(self, request, id):

        # 관리자 일 경우
        if request.user.is_superuser:
            try:
                # 해당 ID 삭제
                Gate.objects.get(id=id).delete()
                return Response(status=HTTP_204_NO_CONTENT)
            except Gate.DoesNotExist:
                return Response(status=HTTP_404_NOT_FOUND)
        else:
            return Response(status=HTTP_403_FORBIDDEN)


class GateUserDetail(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        query_serializer=GateGetQuerySerializer,
        operation_description="직원 식별자와 해당 날짜를 받아서, 출근시간, 퇴근시간, 휴게시간을 볼 수 있음.",
        operation_summary="직원 출퇴근 기록 조회",
        deprecated=False,
        tags=['직원 출입 기록 조회']
    )
    def get(self, request):
        serializer = GateGetQuerySerializer(data=request.GET)
        if serializer.is_valid():
            gate = serializer.get_gate()
            if gate is not None:
                return Response(status=HTTP_200_OK, data=GateSerializer(gate).data)
            else:
                return Response(status=HTTP_404_NOT_FOUND, data={
                    "detail": "출근 기록이 없습니다."
                })
        else:
            return Response(status=HTTP_400_BAD_REQUEST, data=serializer.errors)


class TodayWorkTime(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        operation_description="해당 토큰에서 인증 받은, 사용자의 실시간 근무시간 조회 API",
        operation_summary="실시간 근무시간 조회",
        deprecated=False,
        tags=['실시간 근무시간 조회']
    )
    def get(self, request):
        # 태그를 안 찍는 경우도 있기 때문에, 금일 기준으로 마지막 TAG를 가져오기 위함
        today = datetime.today()
        try:
            gate = Gate.objects.get(pass_day=today, user_id=request.user.id)

            # 마지막 save된 tag명 가져오기
            last_tag = InOutRecord.objects.filter(
                user_id=request.user.id,
                check_time__year=today.year,
                check_time__month=today.month,
                check_time__day=today.day
            ).last().tag

            # 퇴근을 찍고, 실시간 근무시간을 확인할 경우, 저장된 근무시간만을 보여준다.
            if last_tag == "OUT":
                return Response(data={
                    "real_work_time": gate.work_time
                })
            # 출근을 경우, 현재시간에서, 마지막 저장된 출근의 차이와 기존의 근무시간을 더해준다.
            else:
                last_in_date = InOutRecord.objects.filter(
                    user_id=request.user.id,
                    tag__exact="IN"
                ).aggregate(Max('check_time')).get('check_time__max')
                # 분 단위로 리턴
                real_time_work_time = gate.work_time + int((today - last_in_date).seconds // 60)
                return Response(data={
                    "real_work_time": real_time_work_time,
                }, status=HTTP_200_OK)
        except Gate.DoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND)
        except InOutRecord.DoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND)
