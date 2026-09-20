# Linux 서버 요새화 및 시스템 관제 자동화 프로젝트

본 프로젝트는 Ubuntu Linux 환경에서 서버 접속 보안을 강화하고, 최소 권한 원칙에 기반한 역할별 계정/권한 체계를 구축하며, Bash 쉘 스크립트와 `cron`을 활용해 애플리케이션 상태 및 시스템 자원(CPU, MEM, DISK)을 자동으로 관제 및 아카이빙하는 시스템 엔지니어링 실습 프로젝트입니다.

---

##  주요 기능 (Key Features)

1. **서버 요새화 (Network &amp; SSH Security)**

  * SSH 접속 기본 포트 변경 (`20022/tcp`) 및 Root 원격 접속 차단 (`PermitRootLogin no`)
  * UFW 방화벽 정책 적용: 필수 인바운드 포트(`20022/tcp`, `15034/tcp`)만 명시적 허용
2. **역할 기반 접근 제어 (RBAC &amp; ACL)**

  * 역할별 계정(`agent-admin`, `agent-dev`, `agent-test`) 및 그룹(`agent-common`, `agent-core`) 구성
  * Setgid(`2770`) 및 POSIX ACL(`setfacl`)을 활용한 디렉토리 권한 격리 및 최소 권한 원칙 준수

3. **애플리케이션 실행 환경 구축**

  * 전역 환경 변수(`/etc/environment`) 구성 및 보안 키 파일 관리
  * 일반 사용자 계정(`agent-admin`) 기반 서비스 독립 구동 (Boot Sequence 5단계 검증)

4. **시스템 관제 자동화 (`monitor.sh` &amp; Cron)**

  * 프로세스 및 포트 대기 상태 점검 (Health Check)
  * CPU(&gt;20%), MEM(&gt;10%), DISK(&gt;80%) 임계값 초과 경고 알림
  * `/var/log/agent-app/monitor.log` 실시간 기록 및 10MB/10개 파일 로그 로테이션
  * `crontab`을 활용한 매분 백그라운드 자동 실행

5. **보너스 기능 (Bonus Scripts)**

  * `report.sh`: `monitor.log` 파싱 기반 자원 사용량 통계/요약 리포트 생성
  * `archive_logs.sh`: 7일 경과 로그 압축 아카이빙 및 30일 경과 아카이브 자동 삭제

---


##  구축 및 설치 가이드 (Setup Guide)

### 1. SSH 보안 설정 및 UFW 방화벽 구축

```bash
# SSH 포트 20022 변경 및 Root 로그인 차단
sudo nano /etc/ssh/sshd\_config

sudo systemctl restart ssh
```


* `Port 22` -> **Port 20022**
* `PermitRootLogin yes` (또는 주석 처리된 항목) -> **PermitRootLogin no** 

#### : Ubuntu 24.04 `ssh.socket` 비활성화 및 서비스 재시작 

Ubuntu 24.04에서는 기본적으로 `ssh.socket`이 22번 포트를 선점하고 있어서 `sshd_config` 수정 내용이 반영되지 않을 수 있습니다. 소켓을 비활성화하고 `ssh` 서비스를 직접 구동하도록 전환합니다.

**ssh.socket 중지 및 비활성화**
```bash
sudo systemctl stop ssh.socket
sudo systemctl disable ssh.socket
```


**ssh 서비스 재시작 및 자동 실행 등록**

```bash

sudo systemctl restart ssh 
sudo systemctl enable ssh
```

# UFW 방화벽 포트 정책 적용
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 20022/tcp comment 'SSH'
sudo ufw allow 15034/tcp comment 'APP'
sudo ufw enable

```

### 2. 계정 / 그룹 및 디렉토리 권한 설정 (ACL)

```bash
# 그룹 및 계정 생성
sudo groupadd -f agent-common
sudo groupadd -f agent-core
sudo useradd -m -s /bin/bash agent-admin
sudo useradd -m -s /bin/bash agent-dev
sudo useradd -m -s /bin/bash agent-test

sudo usermod -aG agent-common,agent-core agent-admin
sudo usermod -aG agent-common,agent-core agent-dev
sudo usermod -aG agent-common agent-test

```
* -f : 강제 실행 및 중복 옵션 허용 ==> 요구사항 수행 내역서 작성하면서 처음부터 다시 해서 사용
* -m : 홈 디렉터리 자동 생성 옵션 => 사용자를 생성할 때 /home/사용자명 형태의 홈 디렉터리가 없다면 자동으로 만듬
* -s : 기본 쉘 지정 옵션입니다. 사용자가 로그인했을 때 사용할 쉘의 경로(/bin/bash) 지정
* aG : 기존 그룹 유지(a)하며 새 보조 그룹 추가(G)

# 디렉토리 생성 및 Setgid/ACL 권한 적용

```bash
AGENT_HOME=/home/agent-admin/agent-app
sudo mkdir -p $AGENT_HOME/{upload_files,api_keys,bin} /var/log/agent-app /var/log/monitor/agent-app/archive

sudo chown agent-admin:agent-core $AGENT_HOME
sudo chmod 750 $AGENT_HOME

sudo chown agent-admin:agent-common $AGENT_HOME/upload_files
sudo chmod 2770 $AGENT_HOME/upload_files

sudo chown agent-admin:agent-core $AGENT_HOME/api_keys
sudo chmod 2770 $AGENT_HOME/api_keys

sudo chown agent-admin:agent-core /var/log/agent-app
sudo chmod 2770 /var/log/agent-app

sudo setfacl -m g:agent-common:rwx $AGENT_HOME/upload_files
sudo setfacl -d -m g:agent-common:rwx $AGENT_HOME/upload_files

sudo setfacl -m g:agent-core:rwx $AGENT_HOME/api_keys
sudo setfacl -d -m g:agent-core:rwx $AGENT_HOME/api_keys

sudo setfacl -m g:agent-core:rwx /var/log/agent-app
sudo setfacl -d -m g:agent-core:rwx /var/log/agent-app

```
* -p : 상위 디렉토리 자동 생성(중간 단계 없어도 자동 생성)
* setgid (2) : 누가 파일을 새로 만들든 상관없이 그 파일의 소유 그룹이 이 디렉터리의 소유 그룹과 동일하게 지정
* chmod은 단 하나의 그룹만 지정할 수 있는 한계가 존재. 이를 극복하고 특정 그룹에게 타깃 권한을 직접 부여하기 위해 ACL 명령어 사용
* -m : 기존 ACL 규칙을 수정하거나 새로운 규칙을 추가
* -d : 해당 디렉터리의 default ACL을 설정 =>앞으로 이 디렉터리 내부에서 생성되는 모든 하위 파일과 폴더는 소유자가 누구든 상관없이 agent-common 그룹의 rwx 권한을 자동으로 상속
 


### 3. 환경 변수 및 애플리케이션 구동

```bash

AGENT_HOME=/home/agent-admin/agent-app
AGENT_PORT=15034
AGENT_UPLOAD_DIR=/home/agent-admin/agent-app/upload_files
AGENT_KEY_PATH=/home/agent-admin/agent-app/api_keys
AGENT_LOG_DIR=/var/log/agent-app

# 시크릿 키 생성 및 권한 부여
echo "agent_api_key_test" | sudo tee $AGENT_HOME/api_keys/secret.key > /dev/null
sudo chown agent-admin:agent-core $AGENT_HOME/api_keys/secret.key
sudo chmod 640 $AGENT_HOME/api_keys/secret.key


```
* tee 명령어 :입력받은 텍스트를 지정한 파일에 저장하고 화면에 출력 But `> /dev/null`로 리다이렉션해서 화면에 안나옴
(비밀키 출력X)
---

# 스크립트 구동 및 Cron 자동화 설정


### 1. 관제 스크립트 소유권 및 권한 설정

```
sudo chown agent-dev:agent-core /home/agent-admin/agent-app/bin/monitor.sh
sudo chmod 750 /home/agent-admin/agent-app/bin/monitor.sh

```

### 2. Cron 자동 실행 등록 (`agent-admin` 계정)

```
sudo -u agent-admin crontab -e

```

크론탭 내부 맨 아래에 다음 식 추가:

```
* * * * * . /etc/environment; /home/agent-admin/agent-app/bin/monitor.sh &gt; /dev/null 2&gt;&amp;1

```
* **사용 예시**: 

```bash
sudo tail -n 10 /var/log/agent-app/monitor.log

sudo tail -f /var/log/agent-app/monitor.log
```
---
# 보너스 과제 구현 내용

### 1 `report.sh` — 요약 리포트 자동 생성 및 시간 필터링

* **기능**: `/var/log/agent-app/monitor.log` 파일의 누적 기록을 분석하여 **CPU, Memory, Disk** 자원 사용량의 평균, 최대값(발생 시간 포함), 최소값(발생 시간 포함), 그리고 총 데이터 샘플 수를 계산해 요약 보고서로 출력합니다.

* **구간 필터링**: 시작 시간과 종료 시간(`"YYYY-MM-DD HH:MM:SS"`)을 인자로 전달받아 해당 범위 내의 로그만 추출하여 분석할 수 있습니다.

* **소유권 및 권한**: 소유자 `agent-dev`, 그룹 `agent-core`, 권한 `750` (`rwxr-x---`)

```bash
sudo chown agent-dev:agent-core /home/agent-admin/agent-app/bin/report.sh
sudo chmod 750 /home/agent-admin/agent-app/bin/report.sh
```

* **사용 예시**:  
``` bash
# 전체 로그 분석  
sudo -u agent-admin bash -l -c '/home/agent-admin/agent-app/bin/report.sh'  
# 특정 시간 구간 필터링 분석  
sudo -u agent-admin bash -l -c '/home/agent-admin/agent-app/bin/report.sh "2026-09-19 17:21:00" "2026-09-19 17:25:00"'
```
* -l: bash를 로그인 셸로 실행 =>agent-admin 사용자의 환경 변수나 경로설정 등을 온전하게 적용한 상태에서 스크립트를 실행
* -c: 뒤에 오는 문자열을 실행할 명령어로 인식 => ''

### 2. `archive_logs.sh` — 시간 기반 로그 보존 및 압축 정책

* **기능**:  
  1. `/var/log/agent-app/` 경로 내에서 **7일 이상 경과한 로그 파일**을 `.gz` 포맷으로 압축하여 `/var/log/monitor/agent-app/archive/` 경로로 이동 및 보존합니다.
  2. 아카이브 폴더 내에서 \*\*30일 이상 경과한 압축 파일 (`*.gz`)\*\*은 자동으로 탐색하여 삭제 조치합니다.
  3. 디렉토리 미존재, 권한 부족, 대상 파일 부재 등의 예외 상황에서도 안전하게 경고 메시지를 출력하고 정상 종료되도록 예외 처리가 통합되어 있습니다.
* **소유권 및 권한**: 소유자 `agent-dev`, 그룹 `agent-core`, 권한 `750` (`rwxr-x---`)
```bash
sudo chown agent-dev:agent-core /home/agent-admin/agent-app/bin/archive_logs.sh
sudo chmod 750 /home/agent-admin/agent-app/bin/archive_logs.sh
```

* **사용 예시**:  
``` bash
sudo -u agent-admin bash -l -c '/home/agent-admin/agent-app/bin/archive_logs.sh'
```

---

## 주요 트러블슈팅 경험 (Troubleshooting)

1. **`sudo -u` 실행 시 환경 변수 미인식 (`Key Path Mismatch`)**

  * **원인**: `sudo` 명령어 실행 시 기본 보안 정책에 의해 현재 셸 세션의 환경 변수가 초기화됨.
  * **해결**: 스크립트 및 `crontab` 실행 구문 앞에 `. /etc/environment`를 명시적으로 로드하여 전역 환경 변수 반영.

2. **프로세스 탐색명 불일치로 인한 Health Check 실패**

  * **원인**: `monitor.sh` 내 `pgrep` 탐색 패턴과 실제 구동 바이너리 파일명(`agent-app`) 간 오타/차이 발생.
  * **해결**: `PID=$(pgrep -f "agent-app" | head -n 1)`으로 탐색 키워드 정교화.

3. **아카이브 디렉토리 권한 부족 (`Permission Denied`)**

  * **원인**: 일반 서비스 계정(`agent-admin`)이 `/var/log` 하위에 디렉토리를 임의 생성할 권한이 없음.
  * **해결**: 관리자 권한(`sudo`)으로 `/var/log/monitor/agent-app/archive` 사전 생성 후 소유자(`agent-admin:agent-core`) 및 권한(`2770`) 지정.

#  트러블슈팅 보고서: 애플리케이션 부팅 검증 오류 해결

## 1. 환경 변수 경로 불일치 (`Key Path Mismatch`)

* **발생 상황**
* 앱 실행 시 `[2/5] Verifying Environment Variables [FAIL]`과 함께 `Key Path Mismatch. Expected: /home/agent-admin/agent-app/api_keys` 에러 발생


* **원인 분석**
* 과제 문서의 예시 내용과 달리, 실제 제공된 바이너리 앱 내부 검증 로직은 `AGENT_KEY_PATH` 환경 변수가 파일이 아닌 **디렉토리 경로**(`/home/agent-admin/agent-app/api_keys`)를 직접 가리키도록 요구함


* **해결 방안**
* 환경 변수 설정을 디렉토리 경로로 수정하여 반영


```bash
export AGENT_KEY_PATH=/home/agent-admin/agent-app/api_keys

```



---

## 2. 필수 키 파일 누락 및 파일명 불일치 (`Missing File: secret.key`)

* **발생 상황**
* 환경 변수 검증은 통과했으나 `[3/5] Checking Required Files [FAIL]` 및 `Missing File: secret.key` 에러 발생


* **원인 분석**
* 앱이 내부적으로 찾는 실제 키 파일명은 `secret.key`이나, 초기에 `t_secret.key`로 생성하여 파일을 찾지 못함


* **해결 방안**
* 키 파일명을 `secret.key`로 변경하고 소유권 및 권한(`640`) 재설정


```bash
sudo mv /home/agent-admin/agent-app/api_keys/t_secret.key /home/agent-admin/agent-app/api_keys/secret.key
sudo chown agent-admin:agent-core /home/agent-admin/agent-app/api_keys/secret.key
sudo chmod 640 /home/agent-admin/agent-app/api_keys/secret.key

```



---

## 3. `sudo -u` 실행 시 시스템 환경 변수 초기화 문제 및 해결

* **발생 상황**
* `/etc/environment`에 환경 변수를 영구 등록했음에도 불구하고, `sudo -u agent-admin` 명령어로 앱을 실행할 때마다 환경 변수가 누락되어 `Key Path Mismatch` 에러가 재발함


* **원인 분석**
* `sudo` 명령어는 보안 정책상 실행 시점의 환경 변수를 초기화하며, 로그인 셸(`bash -l`)을 사용하더라도 시스템 파일인 `/etc/environment`를 자동으로 읽어오지 못함


* **해결 방안**

* **방법 A (명시적 로드)**: 앱 실행 명령어 앞에 환경 변수 파일 소스(`[source]`) 명령을 함께 추가하여 실행
```bash
sudo -u agent-admin bash -l -c '. /etc/environment && cd /home/agent-admin/agent-app && ./agent-app'

```


* **방법 B (계정 직접 전환)**: `sudo su - agent-admin` 명령어로 서비스 계정에 직접 로그인한 뒤, `~/.bashrc`에 환경 변수를 등록하여 번거로움 방지
```bash
sudo su - agent-admin
cat << 'EOF' >> ~/.bashrc
export AGENT_HOME=/home/agent-admin/agent-app
export AGENT_PORT=15034
export AGENT_UPLOAD_DIR=$AGENT_HOME/upload_files
export AGENT_KEY_PATH=$AGENT_HOME/api_keys
export AGENT_LOG_DIR=/var/log/agent-app
EOF
source ~/.bashrc


cd /home/agent-admin/agent-app | ./agent-app
```