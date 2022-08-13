# CoinBot_withDB-Web
Django와 SQLite를 이용한 코인 자동매매 프로그램 입니다.

실행 순서

0. (재실행 시) db.sqlite3 파일 복사본 생성 후 디렉토리 삭제, 새로 git clone
1. (기존 데이터 존재 시) db.sqlite3 파일 위치에 삽임
2. settings.py Autorized HOST 값 해당 서버 IP로 변경
3. manage.py에서 migrate 실행, createsuperuser 실행
4. slack token 변경
5. 상세 Values 변경
6. 투자 금액 (total) 변경
7. 금지 코인들 List 변경
8. access, secret키 변경
9. main 백그라운드로 실행