set -euo pipefail

DOMAIN="${1:-cloud-hw-yang.duckdns.org}"
EMAIL="${2:-jamgyang@gmail.com}"

echo " Let's Encrypt SSL/TLS 인증서 발급 시작(Domain: ${DOMAIN})"

sudo apt-get update -y
sudo apt-get install -y certbot python3-certbot-nginx

sudo certbot --nginx \
    -d "${DOMAIN}" \
    --non-interactive \
    --agree-tos \
    -m "${EMAIL}" \
    --redirect

sudo systemctl status certbot.timer --no-pager || true

echo "HTTPS SSL/TLS 보안 설정 완료!"
echo " Domain: https://${DOMAIN}"