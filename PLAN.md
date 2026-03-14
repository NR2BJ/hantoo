# Hantoo: 한투 API 웹 트레이딩 플랫폼

## Context
한국투자증권 Open API의 모든 기능을 웹 브라우저에서 사용할 수 있는 트레이딩 플랫폼.
개인 도커 서버에 Docker Compose로 배포. Portainer에서 Git 리포지토리 기반 스택으로 운영.
가족/지인이 공용 계좌 또는 개인 계좌로 거래 가능.
LLM(Claude + OpenAI) 연동으로 AI 매매 분석 및 자동매매 지원.

## Tech Stack
- **Frontend**: Next.js 15 (App Router) + TailwindCSS v4 + TradingView Lightweight Charts
- **Backend**: Python FastAPI + SQLAlchemy (async) + Alembic
- **DB**: PostgreSQL 16 + Redis 7
- **LLM**: Claude API + OpenAI API (멀티 프로바이더)
- **Reverse Proxy**: 외부 리버스 프록시 (Caddy, Nginx 등 - Docker 외부에서 운영)
- **Deploy**: Docker Compose → Portainer (Git 스택)

## 설정 관리 (Zero-Config 배포)
- **설정 파일 불필요** - `.env` 없음
- DB 비밀번호: docker-compose.yml에 하드코딩 (Docker 내부 네트워크, 외부 포트 없음)
- JWT secret, 암호화 키: **첫 실행 시 자동 생성** → DB 저장
- KIS API 키, LLM API 키, 관리자 계정: **웹 UI 셋업 위자드**에서 설정
- 모든 앱 설정: **관리자 설정 페이지**에서 변경 가능
- `app_settings` 테이블에 키-값으로 저장, 메모리 캐시
- 도메인/HTTPS: Caddyfile에서 `:80` → `your.domain.com`으로 변경하면 자동 HTTPS

## 프로젝트 구조

```
hantoo/
├── docker-compose.yml          # Postgres, Redis, Backend, Frontend (설정 파일 불필요)
├── PLAN.md                     # 이 파일
├── REVERSE-PROXY.md            # 리버스 프록시 설정 가이드 (Caddy, Nginx 등)
├── backend/
│   ├── Dockerfile
│   ├── app/
│   │   ├── main.py             # FastAPI 앱 팩토리 + 라이프사이클
│   │   ├── config.py           # 최소 인프라 설정 (DATABASE_URL, REDIS_URL)
│   │   ├── database.py         # SQLAlchemy async engine
│   │   ├── dependencies.py     # DI (현재 유저, 관리자, DB 세션)
│   │   ├── models/             # ORM 모델 12개 테이블
│   │   ├── schemas/            # Pydantic 요청/응답
│   │   ├── routers/            # API 라우터
│   │   │   ├── setup.py        # 셋업 위자드 + 설정 관리
│   │   │   ├── auth.py         # 로그인, 가입, 2FA
│   │   │   └── accounts.py     # KIS 계좌 CRUD
│   │   ├── services/
│   │   │   └── settings_service.py  # DB 기반 설정 (메모리 캐시)
│   │   ├── utils/
│   │   │   ├── security.py     # JWT, bcrypt
│   │   │   └── encryption.py   # Fernet AES-256
│   │   └── workers/            # 백그라운드 작업 (추후)
│   └── alembic/                # DB 마이그레이션
└── frontend/
    ├── Dockerfile
    └── src/
        ├── app/
        │   ├── (auth)/         # login, register, setup (셋업 위자드)
        │   └── (app)/          # 인증 필요 페이지 21개
        ├── components/layout/  # sidebar, header
        ├── stores/             # Zustand (auth, trading)
        └── lib/                # API 클라이언트, 유틸리티
```

## DB 테이블

| 테이블 | 용도 |
|--------|------|
| `app_settings` | 앱 설정 (JWT 키, 암호화 키, API 키 등) - 웹 UI로 관리 |
| `users` | 유저 (admin/member 역할, 초대 코드 기반 가입, TOTP 2FA) |
| `invite_codes` | 가입 초대 코드 |
| `kis_accounts` | KIS 계좌 (AppKey/Secret AES-256 암호화) |
| `kis_account_access` | 공용 계좌 권한 (view/trade) M:N |
| `trades` | 주문 이력 |
| `portfolio_snapshots` | 일별 포트폴리오 스냅샷 |
| `watchlists` / `watchlist_items` | 관심종목 |
| `alerts` | 가격 알림 |
| `ai_conversations` / `ai_messages` | AI 채팅 이력 |
| `ai_strategies` | AI 자동매매 전략 |

## 보안
- 리버스 프록시 자동 HTTPS + 보안 헤더 (HSTS, X-Frame-Options 등)
- JWT HttpOnly 쿠키 (XSS 방지)
- TOTP 2FA (Google Authenticator)
- 초대 코드 기반 가입 (공개 가입 차단)
- KIS 자격증명 AES-256 암호화 저장
- AI 자동매매: 코드 레벨 리스크 제한 (LLM 의존 X)
- 모든 주문에 이중 확인 (프론트 다이얼로그 + 백엔드 검증)

## 구현 Phase

### Phase 1: Foundation ✅
- Docker Compose + Caddy
- FastAPI + DB 모델 12개 테이블 + Alembic
- 인증 (JWT, 초대코드, 2FA)
- KIS 계좌 CRUD (암호화)
- 웹 UI 설정 관리 (셋업 위자드 + 관리자 설정 페이지)
- Next.js 스켈레톤 + 21개 라우트

### Phase 2: Market Data & Charts ✅
- KIS 시세 서비스 (REST 조회, Redis 캐시)
- Rate limiter (계좌별 초당 20건)
- TradingView 차트 (캔들, 거래량, 기술적 지표)
- 시장 개요 / 종목 상세 페이지
- 관심종목 CRUD + 실시간 시세

### Phase 3: Trading
- 주문 서비스 (매수/매도/정정/취소) - 국내/해외
- 주문 내역 DB 기록
- 트레이딩 페이지 (차트 + 주문폼 + 호가 + 체결내역)

### Phase 4: Portfolio & Real-Time
- 포트폴리오 서비스 + 일별 스냅샷 워커
- KIS WebSocket → 백엔드 WS 프록시 → 프론트 실시간 데이터
- 대시보드 (계좌 요약, 지수, 보유종목)
- 가격 알림

### Phase 5: AI Integration
- LLM 프로바이더 추상화 (Claude + OpenAI)
- AI 채팅 + Tool Use (시세 조회, 포트폴리오, 주문 제안)
- 스트리밍 응답 (SSE)

### Phase 6: AI Auto-Trading
- AI 전략 CRUD + APScheduler
- Risk Manager (코드 레벨 제한: 최대 포지션, 손절, 일일 거래 수)
- 자동매매 워커
- 전략 성과 대시보드

### Phase 7: Polish
- 해외주식/ETF/선물/채권 전용 UI
- 모바일 반응형
- KIS API 전체 기능 커버 (순위, 업종, 투자자 동향, IPO, 배당 등)

## 변경 이력

### 2026-03-15
- Phase 1 완성
- Nginx → Caddy 변경 (자동 HTTPS, 외부망 대비)
- Zero-Config 배포: .env 파일 완전 제거
  - DB 비밀번호: docker-compose.yml 하드코딩 (내부 네트워크 전용)
  - JWT secret, encryption key: 첫 실행 시 자동 생성
  - 모든 앱 설정: 웹 UI로 관리 (셋업 위자드 + 관리자 설정 페이지)
- nginx/ 디렉토리 제거 (caddy로 완전 대체)
- Postgres/Redis 외부 포트 제거 (Docker 내부 네트워크만)
- `app_settings` 테이블 추가

### 2026-03-15 (2)
- Caddy를 Docker Compose에서 제거 → 외부 리버스 프록시 사용
  - 백엔드 8000, 프론트엔드 3000 포트 노출
  - caddy/ 디렉토리 삭제, caddy 볼륨 제거
- REVERSE-PROXY.md 추가: Caddy, Nginx 설정 예시 가이드

### 2026-03-15 (3)
- Phase 2 구현 완료
  - 백엔드: Redis 클라이언트, KIS 토큰 서비스, Rate Limiter (20 req/s), KIS API 클라이언트, 캐시 헬퍼, QuoteService (현재가/일봉/분봉/호가/체결/지수/검색)
  - 백엔드: ActiveAccount 의존성, /api/market/* 라우터, /api/watchlists/* CRUD 라우터
  - 프론트엔드: React Query 훅 (useQuote, useCandles, useOrderbook, useTrades, useIndices, useSearch, useWatchlist*)
  - 프론트엔드: TradingView Lightweight Charts (캔들스틱 + 볼륨, 빨간=상승/파란=하락)
  - 프론트엔드: 시장 정보 (지수 + 종목 검색), 종목 상세 (차트 + 호가 + 체결), 관심종목 (CRUD + 실시간 시세), 대시보드 지수 연동
