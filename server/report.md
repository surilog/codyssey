# 시스템 관제 자동화 스크립트 개발 - 요구사항 수행 내역서

## 1. 수행 개요

* **미션 목표**: 다중 사용자 환경의 권한 관리, 네트워크 보안 설정, 애플리케이션 실행 환경 구성, 시스템 리소스 관제 및 로그 관리 자동화


* **대상 환경**: Ubuntu 22.04 LTS 이상


* **주요 구성 요소**:
* SSH 포트 변경 (`20022`) 및 Root 원격 접속 차단


* 방화벽 활성화 및 인바운드 포트 제한 (`20022/tcp`, `15034/tcp`)


* 사용자 계정 및 그룹 권한 체계 구축 (`agent-admin`, `agent-dev`, `agent-test`, `agent-common`, `agent-core`)


* 시스템 관제 스크립트(`monitor.sh`) 및 로그 로테이션 구현


* `crontab`을 통한 주기적 관제 자동화





---

## 2. 세부 수행 내역

### 2.1 SSH 보안 설정

* **수행 내용**:
* SSH 접속 포트를 기본 `22`에서 `20022`로 변경
* `PermitRootLogin no` 설정을 통해 Root 계정의 원격 로그인 차단




* **확인 명령어 및 결과**:
```bash
cat /etc/ssh/sshd_config | grep 20022
cat /etc/ssh/sshd_config | grep PermitRootLogin
ss -tulnp | grep sshd

```
![SSH포트 확인](/images/SSHsetting1.png)
![SSH포트 확인](/images/SSHsetting2.png)


### 2.2 방화벽(UFW) 설정

* **수행 내용**:
* UFW 방화벽 활성화


* 원격 관리를 위한 SSH 포트(`20022/tcp`)와 애플리케이션 포트(`15034/tcp`)만 허용


![방화벽 설정](/images/ufw_check.png)

### 2.3 계정 / 그룹 / 권한 체계 구성

* **계정 생성**:
* `agent-admin`: 운영/관리 및 `cron` 실행자


* `agent-dev`: 개발/운영 및 `monitor.sh` 작성자


* `agent-test`: QA/테스트 전용

![계정 / 그룹 / 권한 체계 구성](/images/create_account_check.png)


* **그룹 생성**:
* `agent-common`: `agent-admin`, `agent-dev`, `agent-test` 포함


* `agent-core`: `agent-admin`, `agent-dev` 포함

![계정 / 그룹 / 권한 체계 구성](/images/create_group_check.png)



### 2.4 디렉토리 구조 및 접근 권한 설정 (`$AGENT_HOME`)

* **디렉토리 경로 및 권한 정책**:
* `$AGENT_HOME` (`/home/agent-admin/agent-app`): 소유자 `agent-admin:agent-core`, 권한 `750`


![디렉토리 구조 및 접근 권한 설정](/images/2-3.png)

* `$AGENT_HOME/upload_files`: 소유자 `agent-admin:agent-common`, 권한 `2770` 및 ACL 설정 (공용 R/W)


* `$AGENT_HOME/api_keys` 및 `/var/log/agent-app`: 소유자 `agent-admin:agent-core`, 권한 `2770` 및 ACL 설정 (핵심 그룹만 R/W)


![디렉토리 구조 및 접근 권한 설정](/images/2-4.png)


### 2.5 애플리케이션 실행 및 검증

* **환경 변수 구성**: 
```bash
export AGENT_HOME=/home/agent-admin/agent-app
export AGENT_PORT=15034
export AGENT_UPLOAD_DIR=$AGENT_HOME/upload_files
export AGENT_KEY_PATH=$AGENT_HOME/api_keys
export AGENT_LOG_DIR=/var/log/agent-app
```

* **앱 실행 결과 (Boot Sequence 5단계)**:

![앱 실행 결과](/images/boot_s_check.png)



### 2.6 시스템 관제 스크립트 (`monitor.sh`) 구현 및 배치


* **파일 위치 및 권한**: `$AGENT_HOME/bin/monitor.sh` (소유자: `agent-dev`, 그룹: `agent-core`, 권한: `750`)


* **주요 기능**:
* **Health Check**: 프로세스(`agent-app`) 및 포트(`15034`) 점검 후 비정상 시 `exit 1`

* **방화벽 점검**: UFW 활성화 여부 확인 (비활성 시 `[WARNING]` 출력 및 계속 진행)


* **자원 수집 및 임계값 경고**: CPU(>20%), MEM(>10%), DISK(>80%) 초과 시 경고 출력


* **로그 로테이션**: `/var/log/agent-app/monitor.log` 파일 크기가 10MB를 초과할 경우 최대 10개의 파일로 순차적 로테이션 수행

```bash
ls -lt /var/log/agent-app/
```

![monitor.sh 파일 위치 및 권한](/images/4-1.png)
![monitor.sh 기능 확인 및 로그 확인](/images/4-2.png)
![로그 로테이션 확인](/images/log.png)

### 2.7 Cron 자동화 스크립트 등록

* **등록 계정**: `agent-admin`

* **등록 내용 (`crontab -e`)**:
```cron
* * * * * . /etc/environment; /home/agent-admin/agent-app/bin/monitor.sh > /dev/null 2>&1

```


* **확인 결과**: 1분 주기마다 정상적으로 로그 파일(`/var/log/agent-app/monitor.log`)에 데이터가 누적되는 것 검증 완료

![1분 주기 로그 누적 확인](/images/4-2.png)


## 3. 보너스 수행 내역

### 3-1.

![ 요약 리포트 자동 생성 및 시간 필터링 확인](/images/bonus1.png)


### 3-2.
![시간 기반 로그 보존 및 압축 정책인](/images/bouns2.png)