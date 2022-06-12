# WantedLab Python 개발자 면접 과제
## 출근 기록 API

✔️ **REST API 기능**

- [GET] 직원 출퇴근 기록 조회
- [PUT] 출입 기록 수정
- [DELETE] 출입 기록 삭제
- [POST] 출퇴근 WebHook


✔️ **REST API 명세서**
- http://127.0.0.1:8000/swagger/ (명세서 URL)
- 해당 DB에는 사용자가 없음.
- 유저 생성 API는 존재하지 않음.
- <code>python manage.py createsuperuser</code> 를 통하여 관리자 계정 생성 이후, /admin 접속 이후 유저 및 토큰 생성
- swagger Authorization 에 Token {value}를 해줘야함

<br>

✔️ **구동 방법**
<br>
- migrations 파일이 없다면 <code>python manage.py makemigrations</code> 필요
#### Docker 구동시
#### 자동 migrate 진행
<code>
    docker-compose -f ./dcoker-compose.yml up -d
</code>

#### 로컬 구동시
<code>
    python manage.py runserver --settings=config.settings_local
</code>


## 과제
1. 출근은 하루 중 가장 먼저 들어온 시간, 퇴근은 하루 중 가장 마지막으로 나간 시간입니다.
2. 하루 중 사무실에 들어와서 나간 시간까지의 합이 근무시간이며, 근무 시간 중에 나가 있었던 시간은 휴게 시간이 됩니다.
3. 하루의 기준은 오전 6시에서 다음날 오전 6시까지 입니다.
4. 직원들은 종종 태그를 찍지 않고 출입합니다.

