#!/usr/bin/env bash

set -euo pipefail

# 공통 환경 변수 설정
REGION="ap-northeast-2"
PROJECT_TAG="cloud-hw"
VPC_CIDR="10.0.0.0/16"
SUBNET_CIDR="10.0.1.0/24"
AZ="ap-northeast-2a"
INSTANCE_TYPE="t3.micro"
KEY_NAME="cloud-hw-key"

echo " [Phase 1] AWS CLI 인프라 자동 생성을 시작합니다... (Region: ${REGION})"

# 내 공인 IP 자동 감지 (SSH 22번 포트 접근 제한용)
MY_IP=$(curl -s https://checkip.amazonaws.com || curl -s https://ifconfig.me || echo "")
if [ -z "$MY_IP" ]; then
    echo " 내 공인 IP 감지 실패. 기본값 0.0.0.0/0 지정"
    SSH_CIDR="${SSH_CIDR:-0.0.0.0/0}"
else
    SSH_CIDR="${SSH_CIDR:-${MY_IP}/32}"
fi
echo " SSH 접근 허용 IP: ${SSH_CIDR}"

# VPC 생성 및 DNS 옵션 활성화
echo " [1/6] VPC 생성 중 (${VPC_CIDR})..."
VPC_ID=$(aws ec2 create-vpc \
    --cidr-block "${VPC_CIDR}" \
    --tag-specifications "ResourceType=vpc,Tags=[{Key=Name,Value=${PROJECT_TAG}-vpc},{Key=Project,Value=${PROJECT_TAG}}]" \
    --region "${REGION}" \
    --query 'Vpc.VpcId' --output text)

aws ec2 modify-vpc-attribute --vpc-id "${VPC_ID}" --enable-dns-hostnames --region "${REGION}"
aws ec2 modify-vpc-attribute --vpc-id "${VPC_ID}" --enable-dns-support --region "${REGION}"
echo "  VPC 생성 완료: ${VPC_ID}"

# 퍼블릭 서브넷 생성 및 퍼블릭 IP 자동 할당 활성화
echo " [2/6] 퍼블릭 서브넷 생성 중 (${SUBNET_CIDR}, AZ: ${AZ})..."
SUBNET_ID=$(aws ec2 create-subnet \
    --vpc-id "${VPC_ID}" \
    --cidr-block "${SUBNET_CIDR}" \
    --availability-zone "${AZ}" \
    --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=${PROJECT_TAG}-public-subnet},{Key=Project,Value=${PROJECT_TAG}}]" \
    --region "${REGION}" \
    --query 'Subnet.SubnetId' --output text)

aws ec2 modify-subnet-attribute --subnet-id "${SUBNET_ID}" --map-public-ip-on-launch --region "${REGION}"
echo "  서브넷 생성 완료: ${SUBNET_ID}"

# 인터넷 게이트웨이(IGW) 생성 및 VPC 바인딩
echo " [3/6] 인터넷 게이트웨이(IGW) 생성 및 VPC 연결 중..."
IGW_ID=$(aws ec2 create-internet-gateway \
    --tag-specifications "ResourceType=internet-gateway,Tags=[{Key=Name,Value=${PROJECT_TAG}-igw},{Key=Project,Value=${PROJECT_TAG}}]" \
    --region "${REGION}" \
    --query 'InternetGateway.InternetGatewayId' --output text)

aws ec2 attach-internet-gateway --vpc-id "${VPC_ID}" --internet-gateway-id "${IGW_ID}" --region "${REGION}"
echo "  IGW 생성 및 연결 완료: ${IGW_ID}"

# 라우팅 테이블 생성 및 0.0.0.0/0 -> IGW 경로 연결
echo " [4/6] 라우팅 테이블 설정 중..."
ROUTE_TABLE_ID=$(aws ec2 create-route-table \
    --vpc-id "${VPC_ID}" \
    --tag-specifications "ResourceType=route-table,Tags=[{Key=Name,Value=${PROJECT_TAG}-public-rt},{Key=Project,Value=${PROJECT_TAG}}]" \
    --region "${REGION}" \
    --query 'RouteTable.RouteTableId' --output text)

aws ec2 create-route \
    --route-table-id "${ROUTE_TABLE_ID}" \
    --destination-cidr-block "0.0.0.0/0" \
    --gateway-id "${IGW_ID}" \
    --region "${REGION}" > /dev/null

aws ec2 associate-route-table \
    --subnet-id "${SUBNET_ID}" \
    --route-table-id "${ROUTE_TABLE_ID}" \
    --region "${REGION}" > /dev/null
echo "  라우팅 테이블 설정 완료: ${ROUTE_TABLE_ID}"

# 보안 그룹 생성 및 인바운드 포트(22, 80, 443) 허용
echo " [5/6] 보안 그룹 생성 및 규칙 설정 중..."
SG_ID=$(aws ec2 create-security-group \
    --group-name "${PROJECT_TAG}-web-sg" \
    --description "Security group for ${PROJECT_TAG} web server" \
    --vpc-id "${VPC_ID}" \
    --tag-specifications "ResourceType=security-group,Tags=[{Key=Name,Value=${PROJECT_TAG}-web-sg},{Key=Project,Value=${PROJECT_TAG}}]" \
    --region "${REGION}" \
    --query 'GroupId' --output text)

# SSH(22): 내 IP만 허용
aws ec2 authorize-security-group-ingress --group-id "${SG_ID}" --protocol tcp --port 22 --cidr "${SSH_CIDR}" --region "${REGION}"
# HTTP(80): 전체 허용
aws ec2 authorize-security-group-ingress --group-id "${SG_ID}" --protocol tcp --port 80 --cidr "0.0.0.0/0" --region "${REGION}"
# HTTPS(443): 전체 허용
aws ec2 authorize-security-group-ingress --group-id "${SG_ID}" --protocol tcp --port 443 --cidr "0.0.0.0/0" --region "${REGION}"
echo "  보안 그룹 생성 완료: ${SG_ID}"

# 최신 Ubuntu 24.04 LTS AMI ID 자동 조회
echo " 최신 Ubuntu 24.04 LTS AMI ID 조회 중..."
AMI_ID=$(aws ec2 describe-images \
    --owners "099720109477" \
    --filters "Name=name,Values=ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*" "Name=state,Values=available" \
    --query 'sort_by(Images, &CreationDate)[-1].ImageId' \
    --region "${REGION}" \
    --output text)
echo " ✅ AMI ID: ${AMI_ID}"

# EC2 인스턴스 시작
echo " [6/6] EC2 인스턴스 배포 중 (${INSTANCE_TYPE})..."
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id "${AMI_ID}" \
    --count 1 \
    --instance-type "${INSTANCE_TYPE}" \
    --key-name "${KEY_NAME}" \
    --security-group-ids "${SG_ID}" \
    --subnet-id "${SUBNET_ID}" \
    --block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":8,"VolumeType":"gp3","DeleteOnTermination":true}}]' \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=${PROJECT_TAG}-web-server},{Key=Project,Value=${PROJECT_TAG}}]" \
    --region "${REGION}" \
    --query 'Instances[0].InstanceId' --output text)

echo "  인스턴스가 Running 상태가 될 때까지 대기 중... (${INSTANCE_ID})"
aws ec2 wait instance-running --instance-ids "${INSTANCE_ID}" --region "${REGION}"

PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids "${INSTANCE_ID}" \
    --region "${REGION}" \
    --query 'Reservations.Instances.PublicIpAddress' --output text)

echo ""
echo "=========================================================================="
echo " [Phase 1] AWS CLI 인프라 자동 생성 완료!"
echo "=========================================================================="
echo " 생성된 리소스 정보 요약:"
echo " • VPC ID: ${VPC_ID}"
echo " • Subnet ID: ${SUBNET_ID}"
echo " • IGW ID: ${IGW_ID}"
echo " • RouteTable ID: ${ROUTE_TABLE_ID}"
echo " • SecurityGroup: ${SG_ID}"
echo " • Instance ID: ${INSTANCE_ID}"
echo " • Public IP: ${PUBLIC_IP}"
echo ""
echo " 접속 테스트 명령어:"
echo " ssh -i \"${KEY_NAME}.pem\" ubuntu@${PUBLIC_IP}"
echo "=========================================================================="