#EC2 서버 설정 및 배포 스크립트

set -euo pipefail


sudo apt-get update -y
sudo apt-get install -y docker.io nginx curl
# 도커 서비스 활성화 + 권한 설정
sudo systemctl enable --now docker
sudo usermod -aG docker ubuntu || true

echo "도커 이미지 빌드 및 컨테이너 실행 중 "
sudo docker stop cloud-web-app 2>/dev/null || true
sudo docker rm cloud-web-app 2>/dev/null || true

sudo docker build -t cloud-hw-image .
sudo docker run -d \
    --name cloud-web-app \
    --restart always \
    -p 127.0.0.1:8080:80 \
    cloud-hw-image

echo "Nginx 리버스 프록시 설정 적용 중"
sudo cp nginx/site.conf /etc/nginx/sites-available/default
sudo nginx -t
sudo systemctl reload nginx

echo "  Docker Container: 127.0.0.1:8080 에서 실행 중"
echo "  Nginx Reverse Proxy: 80 포트 ➔ 8080 포트로 전달 완료"