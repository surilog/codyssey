# 베이스 이미지로 우분투 24.04 사용
FROM ubuntu:24.04

# 필수 패키지 설치 (sudo, ufw, iproute2, procps, acl 등)
RUN apt-get update && apt-get install -y \
    sudo \
    ufw \
    iproute2 \
    procps \
    acl \
    && rm -rf /var/lib/apt/lists/*

# 환경 변수 설정
ENV AGENT_HOME=/home/agent-admin/agent-app
ENV AGENT_PORT=15034

# 1. 과제 요구사항 계정 및 그룹 생성
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

# 2. 디렉토리 구조 및 권한/ACL 설정
RUN mkdir -p $AGENT_HOME/upload_files && \
    mkdir -p $AGENT_HOME/api_keys && \
    mkdir -p $AGENT_HOME/bin && \
    mkdir -p /var/log/agent-app && \
    chown -R agent-admin:agent-core $AGENT_HOME && \
    chmod 750 $AGENT_HOME && \
    chown -R agent-admin:agent-common $AGENT_HOME/upload_files && \
    chmod 2770 $AGENT_HOME/upload_files && \
    chown -R agent-admin:agent-core $AGENT_HOME/api_keys && \
    chmod 2770 $AGENT_HOME/api_keys && \
    chown -R agent-admin:agent-core /var/log/agent-app && \
    chmod 2770 /var/log/agent-app

# 3. 실행 파일 복사 및 권한 부여 (맥 빌드 디렉토리에 있는 agent-app을 복사)
COPY agent-app $AGENT_HOME/agent-app
RUN chown agent-admin:agent-core $AGENT_HOME/agent-app && \
    chmod 750 $AGENT_HOME/agent-app

# 4. API 키 파일 생성 및 권한 설정
RUN echo "agent_api_key_test" > $AGENT_HOME/api_keys/t_secret.key && \
    chown agent-admin:agent-core $AGENT_HOME/api_keys/t_secret.key && \
    chmod 640 $AGENT_HOME/api_keys/t_secret.key

# 5. /etc/environment 환경 변수 영구 등록
RUN echo "AGENT_HOME=$AGENT_HOME" >> /etc/environment && \
    echo "AGENT_PORT=15034" >> /etc/environment && \
    echo "AGENT_UPLOAD_DIR=$AGENT_HOME/upload_files" >> /etc/environment && \
    echo "AGENT_KEY_PATH=$AGENT_HOME/api_keys/t_secret.key" >> /etc/environment && \
    echo "AGENT_LOG_DIR=/var/log/agent-app" >> /etc/environment

# 작업 디렉토리 설정
WORKDIR $AGENT_HOME

# 포트 개방
EXPOSE 15034 20022

# 컨테이너 유지
CMD ["tail", "-f", "/dev/null"]