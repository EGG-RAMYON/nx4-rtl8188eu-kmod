# GitHub 게시

소스 전용 공개본이며 커널 모듈 바이너리, 차량별 진단 기록, NX4 전용 커널 설정은 포함하지 않습니다. 공개 저장소: https://github.com/EGG-RAMYON/nx4-rtl8188eu-kmod OWNER는 본인 계정 또는 조직명으로 바꿉니다.

```sh
git init
git add .
git diff --cached --stat
git commit -m "Publish NX4 RTL8188EU diagnostic sources and provenance"
git branch -M main
git remote add origin https://github.com/EGG-RAMYON/nx4-rtl8188eu-kmod.git
git push -u origin main
```

권장 설명: Experimental RTL8188EU cfg80211 port and initialization diagnostics for NX4 Gen5W / Linux 3.18.24-tcc.

초기 버전명 제안: `v0.1.0-diagnostic-r3`. 특정 NX4 R6 구성에서 Wi-Fi/IP/ADB 성공이 실차에서 보고되었습니다. Release 바이너리는 성공 시험 `.ko`와 hash/build record가 대조되기 전까지 성공 검증품으로 표시하지 마세요. 검증 현황은 [VALIDATION.md](VALIDATION.md)를 참조하세요.

원래 진단 키트 ZIP을 그대로 올리기보다 이 공개본을 사용하세요. 실차 수집 로그를 이슈에 올릴 때는 SSID, MAC, IP, VIN, 경로의 개인 식별정보를 지우세요. 이 저장소에는 원본 bcmdhd나 Android 시스템 파일이 들어 있지 않습니다.
