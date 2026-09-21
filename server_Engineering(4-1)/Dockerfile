# 베이스 이미지로 우분투 22.04 사용
FROM ubuntu:24.04

# 필수 패키지 설치 (sudo, ufw, iproute2, procps, acl 등)
RUN apt-get update && apt-get install -y \
    sudo \
    ufw \
    iproute2 \
    procps \
    acl \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /workspace

# 필요한 파일 복사
COPY . /workspace/

# 과제 요구사항 계정 및 그룹 생성
RUN groupadd -f agent-common && \
    groupadd -f agent-core && \
    useradd -m -s /bin/bash agent-admin && \
    useradd -m -s /bin/bash agent-dev && \
    useradd -m -s /bin/bash agent-test && \
    usermod -aG agent-common agent-admin && \
    usermod -aG agent-common agent-dev && \
    usermod -aG agent-common agent-test && \
    usermod -aG agent-core agent-admin && \
    usermod -aG agent-core agent-dev

# 앱 디렉토리 및 권한 설정
RUN AGENT_HOME=/home/agent-admin/agent-app && \
    mkdir -p $AGENT_HOME/upload_files && \
    mkdir -p $AGENT_HOME/api_keys && \
    mkdir -p $AGENT_HOME/bin && \
    mkdir -p /var/log/agent-app && \
    chown agent-admin:agent-core $AGENT_HOME && \
    chmod 750 $AGENT_HOME

# 포트 개방
EXPOSE 15034 20022