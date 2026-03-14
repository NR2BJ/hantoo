# Reverse Proxy 설정 가이드

Hantoo는 리버스 프록시를 Docker 외부에서 운영하는 것을 권장합니다.
Docker Compose는 백엔드(`:7655`)와 프론트엔드(`:7656`) 포트만 노출합니다.

## 라우팅 규칙

| 경로 | 대상 | 설명 |
|------|------|------|
| `/api/*` | `http://<DOCKER_HOST>:7655` | REST API |
| `/ws/*` | `http://<DOCKER_HOST>:7655` | WebSocket (Upgrade 필요) |
| 나머지 전부 | `http://<DOCKER_HOST>:7656` | Next.js 프론트엔드 |

`<DOCKER_HOST>`는 Docker가 돌아가는 서버의 IP 또는 호스트명입니다.

---

## Caddy

가장 간단합니다. 자동 HTTPS (Let's Encrypt) 포함.

```caddyfile
your.domain.com {
    # API
    handle /api/* {
        reverse_proxy <DOCKER_HOST>:7655
    }

    # WebSocket
    handle /ws/* {
        reverse_proxy <DOCKER_HOST>:7655
    }

    # Frontend
    handle {
        reverse_proxy <DOCKER_HOST>:7656
    }

    # 보안 헤더
    header {
        X-Content-Type-Options nosniff
        X-Frame-Options DENY
        X-XSS-Protection "1; mode=block"
        Referrer-Policy strict-origin-when-cross-origin
        Strict-Transport-Security "max-age=31536000; includeSubDomains"
    }
}
```

HTTP only (개발용):
```caddyfile
:80 {
    handle /api/* {
        reverse_proxy <DOCKER_HOST>:7655
    }
    handle /ws/* {
        reverse_proxy <DOCKER_HOST>:7655
    }
    handle {
        reverse_proxy <DOCKER_HOST>:7656
    }
}
```

---

## Nginx

```nginx
server {
    listen 80;
    server_name your.domain.com;

    # HTTPS 리다이렉트 (certbot 사용 시)
    # return 301 https://$host$request_uri;

    # API
    location /api/ {
        proxy_pass http://<DOCKER_HOST>:7655;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket
    location /ws/ {
        proxy_pass http://<DOCKER_HOST>:7655;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 86400;
    }

    # Frontend
    location / {
        proxy_pass http://<DOCKER_HOST>:7656;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 보안 헤더
    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options DENY always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy strict-origin-when-cross-origin always;
}
```

HTTPS (certbot):
```bash
sudo certbot --nginx -d your.domain.com
```

---

## Traefik

Docker labels 방식 대신, 파일 프로바이더 예시:

```yaml
# traefik-dynamic.yml
http:
  routers:
    hantoo-api:
      rule: "Host(`your.domain.com`) && PathPrefix(`/api`)"
      service: hantoo-backend
      tls:
        certResolver: letsencrypt
    hantoo-ws:
      rule: "Host(`your.domain.com`) && PathPrefix(`/ws`)"
      service: hantoo-backend
      tls:
        certResolver: letsencrypt
    hantoo-frontend:
      rule: "Host(`your.domain.com`)"
      service: hantoo-frontend
      tls:
        certResolver: letsencrypt
      priority: 1

  services:
    hantoo-backend:
      loadBalancer:
        servers:
          - url: "http://<DOCKER_HOST>:7655"
    hantoo-frontend:
      loadBalancer:
        servers:
          - url: "http://<DOCKER_HOST>:7656"
```

---

## 공통 주의사항

1. **WebSocket**: `/ws/*` 경로는 반드시 WebSocket upgrade를 지원해야 합니다. Caddy는 자동, Nginx는 `proxy_set_header Upgrade` 설정 필요.
2. **HTTPS 권장**: 금융 거래 데이터를 다루므로 외부 접속 시 반드시 HTTPS를 사용하세요.
3. **쿠키**: JWT가 HttpOnly 쿠키로 전달됩니다. 리버스 프록시가 `Host` 헤더를 올바르게 전달해야 합니다.
4. **타임아웃**: WebSocket 연결은 장시간 유지됩니다. Nginx의 경우 `proxy_read_timeout`을 충분히 높게 설정하세요.
