# Backend Directory

This directory is for backend.
---
## 데이터베이스 생성 및 연결

현재 **database서버**는 로컬에서 만들어서 돌리고 있습니다. test시에는 각자 로컬에서 MySQL 서버 실행 후 접속 바랍니다. 데이터베이스 연결 로직은 **database.py**와 **db_config.py**를 참고해 주시면 됩니다. (**db_config**는 **.gitignore** 되기 때문에 직접 만들어야 할 수도 있음 ==> 데이터베이스 생성 시, E-R Diagram 참고하면서 만들 것!)
---
## 필요한 pip 패키지 설치

```linux
pip install -r requirements.txt
```
---
## 서버 돌리기

Backend 서버를 돌리려면 backend 디렉토리로 들어 간 후 다음 명령어를 입력합니다.

```linux
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

이때 명령어의 뜻은 다음과 같습니다.
main.py 안에 있는 app 모듈을 실행한다.

```--reload``` : 자동으로 재로딩 되게한다(코드 수정하고 저장 시 자동으로 서버 리부트가 됨)

```--host 0.0.0.0``` : 모든 호스트들을 접속할 수 있게 한다

```--port 8000``` : 포트번호를 8000번으로 지정한다
