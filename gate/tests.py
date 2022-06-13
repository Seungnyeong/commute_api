from django.test import TestCase, Client
from users.models import User
from rest_framework.views import status
from rest_framework.authtoken.models import Token


class GateWebHookAPITestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(username="testuser",
                                        password="test",
                                        is_superuser=True
                                        )
        self.token = Token.objects.create(user=self.user).key

    def test_gate_api(self):
        header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(self.token),
            'Content-Type': "application/json; charset=utf-8"
        }

        # 사용자 출근
        in_response = self.client.post(path='/gate/api/v1/hook/', data={
            "user_id": self.user.id,
            "tag": "IN",
            "check_time": "2022-06-12 09:00:00"
        }, **header)

        self.assertEqual(in_response.status_code, status.HTTP_201_CREATED)

        # 사용자 퇴근
        out_response = self.client.post(path='/gate/api/v1/hook/', data={
            "user_id": self.user.id,
            "tag": "OUT",
            "check_time": "2022-06-12 12:00:00"
        }, **header)
        self.assertEqual(out_response.status_code, status.HTTP_201_CREATED)

        # 사용자 데이터 확인
        gate_response = self.client.get('/gate/api/v1/user/', {'user_id': self.user.id, 'pass_day': "2022-06-12"},
                                        **header)

        self.assertEqual(gate_response.status_code, status.HTTP_200_OK)
        self.assertEqual(gate_response.data.get('in_date'), '2022-06-12 09:00:00')
        self.assertEqual(gate_response.data.get('out_date'), '2022-06-12 12:00:00')

        # 근무시간 3시간
        self.assertEqual(gate_response.data.get('work_time'), 180)

        # 다시 쉬고옴
        self.client.post(path='/gate/api/v1/hook/', data={
            "user_id": self.user.id,
            "tag": "IN",
            "check_time": "2022-06-12 13:00:00"
        }, **header)

        gate_response = self.client.get('/gate/api/v1/user/', {'user_id': self.user.id, 'pass_day': "2022-06-12"},
                                        **header)

        # 휴식 시간
        self.assertEqual(gate_response.data.get('break_time'), 60)

        # 퇴근
        self.client.post(path='/gate/api/v1/hook/', data={
            "user_id": self.user.id,
            "tag": "OUT",
            "check_time": "2022-06-12 18:00:00"
        }, **header)

        gate_response = self.client.get('/gate/api/v1/user/', {'user_id': self.user.id, 'pass_day': "2022-06-12"},
                                        **header)

        # 여섯시 퇴근 이후 근무시간
        self.assertEqual(gate_response.data.get('work_time'), 480)

        # 오늘 일한 시간
        gate_response = self.client.get('/gate/api/v1/user/', {'user_id': self.user.id, },
                                        **header)

        self.assertEqual(gate_response.data.get('work_time'), 480)

    def test_today_real_time(self):
        header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(self.token),
            'Content-Type': "application/json; charset=utf-8"
        }

        # 사용자 출근
        in_response = self.client.post(path='/gate/api/v1/hook/', data={
            "user_id": self.user.id,
            "tag": "IN",
            "check_time": "2022-06-13 00:00:00"
        }, **header)

        self.assertEqual(in_response.status_code, status.HTTP_201_CREATED)

        # 실시간 근무시간 조회
        real_work_time_response = self.client.get("/gate/api/v1/today/", **header)
        self.assertEqual(real_work_time_response.status_code, status.HTTP_200_OK)
        self.assertEqual(real_work_time_response.data.get('real_work_time'), 18)
