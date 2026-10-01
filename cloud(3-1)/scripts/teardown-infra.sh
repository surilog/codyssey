#!/usr/bin/env bash


set -euo pipefail

REGION="ap-northeast-2"
PROJECT_TAG="cloud-hw"

echo "[Phase 1] '${PROJECT_TAG}' 프로젝트 인프라 자원 삭제를 시작합니다..."

# 1. EC2 인스턴스 조회 및 종료
INSTANCE_IDS=$(aws ec2 describe-instances \
    --filters "Name=tag:Project,Values=${PROJECT_TAG}" "Name=instance-state-name,Values=pending,running,stopping,stopped" \
    --region "${REGION}" \
    --query 'Reservations[].Instances[].InstanceId' --output text)

if [ -n "${INSTANCE_IDS}" ] && [ "${INSTANCE_IDS}" != "None" ]; then
    echo " EC2 인스턴스 종료 중: ${INSTANCE_IDS}"
    aws ec2 terminate-instances --instance-ids ${INSTANCE_IDS} --region "${REGION}" > /dev/null
    echo "  인스턴스가 완전히 종료(Terminated)될 때까지 대기 중..."
    aws ec2 wait instance-terminated --instance-ids ${INSTANCE_IDS} --region "${REGION}"
    echo "  EC2 인스턴스 종료 완료!"
else
    echo " 종료할 EC2 인스턴스가 없습니다."
fi

# 2. 보안 그룹 삭제
SG_IDS=$(aws ec2 describe-security-groups \
    --filters "Name=tag:Project,Values=${PROJECT_TAG}" \
    --region "${REGION}" \
    --query 'SecurityGroups[].GroupId' --output text)

if [ -n "${SG_IDS}" ] && [ "${SG_IDS}" != "None" ]; then
    for sg in ${SG_IDS}; do
        echo " 보안 그룹 삭제 중: ${sg}"
        aws ec2 delete-security-group --group-id "${sg}" --region "${REGION}" || true
    done
fi

# 3. VPC 및 하위 리소스(라우팅 테이블, IGW, 서브넷) 일괄 삭제
VPC_IDS=$(aws ec2 describe-vpcs \
    --filters "Name=tag:Project,Values=${PROJECT_TAG}" \
    --region "${REGION}" \
    --query 'Vpcs[].VpcId' --output text)

if [ -n "${VPC_IDS}" ] && [ "${VPC_IDS}" != "None" ]; then
    for vpc in ${VPC_IDS}; do
        # 라우팅 테이블 삭제
        RT_IDS=$(aws ec2 describe-route-tables \
            --filters "Name=vpc-id,Values=${vpc}" "Name=tag:Project,Values=${PROJECT_TAG}" \
            --region "${REGION}" \
            --query 'RouteTables[].RouteTableId' --output text)
        for rt in ${RT_IDS}; do
            echo " 라우팅 테이블 삭제 중: ${rt}"
            aws ec2 delete-route-table --route-table-id "${rt}" --region "${REGION}" || true
        done

        # 인터넷 게이트웨이 분리 및 삭제
        IGW_IDS=$(aws ec2 describe-internet-gateways \
            --filters "Name=attachment.vpc-id,Values=${vpc}" \
            --region "${REGION}" \
            --query 'InternetGateways[].InternetGatewayId' --output text)
        for igw in ${IGW_IDS}; do
            echo " 인터넷 게이트웨이 분리 및 삭제 중: ${igw}"
            aws ec2 detach-internet-gateway --internet-gateway-id "${igw}" --vpc-id "${vpc}" --region "${REGION}" || true
            aws ec2 delete-internet-gateway --internet-gateway-id "${igw}" --region "${REGION}" || true
        done

        # 서브넷 삭제
        SUBNET_IDS=$(aws ec2 describe-subnets \
            --filters "Name=vpc-id,Values=${vpc}" \
            --region "${REGION}" \
            --query 'Subnets[].SubnetId' --output text)
        for sub in ${SUBNET_IDS}; do
            echo "📐 서브넷 삭제 중: ${sub}"
            aws ec2 delete-subnet --subnet-id "${sub}" --region "${REGION}" || true
        done

        # VPC 삭제
        echo " VPC 삭제 중: ${vpc}"
        aws ec2 delete-vpc --vpc-id "${vpc}" --region "${REGION}"
        echo "  VPC 삭제 완료!"
    done
fi

echo " [Phase 1] 모든 인프라 자원 삭제 스크립트 실행 완료!"