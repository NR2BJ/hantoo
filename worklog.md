# worklog

Purpose: Claude Code와 Codex가 동시에 작업할 때, 누가 언제 무엇을 어떻게 어디에 수정했는지 한 파일에서 바로 확인하기 위한 기록 파일.

## 기록 규칙

앞으로는 아래 형식으로 계속 누적:

```md
## YYYY-MM-DD HH:MM JST | 작성자

- 범위:
- 무엇을 했는지:
- 어떻게 수정했는지:
- 수정 파일:
- 검증:
- 메모:
```

주의:
- 이력은 요약이 아니라 실제 수정 의도를 남긴다.
- 가능한 한 `무엇`, `방법`, `파일`, `검증`을 같이 적는다.
- 다른 에이전트가 이어받을 수 있도록 상태 전이/런타임 가정도 메모에 남긴다.

---

## 2026-03-15 12:00 JST | Claude Code (Opus 4.6)

- 범위: 프로젝트 초기 리서치
- 무엇을 했는지: 한국투자증권(KIS) Open Trading API에 대한 종합 리서치 수행
- 어떻게 수정했는지: 웹 검색을 통해 API 기능, 인증 방식, 엔드포인트, 오픈소스 라이브러리, 제한 사항 등 조사
- 수정 파일: worklog.md (신규 생성)
- 검증: 공식 KIS Developers 포탈, GitHub 리포지토리, 커뮤니티 문서 등 다수 소스 교차 확인
- 메모: 리서치 결과는 채팅으로 전달. 프로젝트명 "hantoo"는 한국투자증권(한투) 관련 프로젝트로 추정.

## 2026-03-15 13:00 JST | Claude Code (Opus 4.6)

- 범위: 프론트엔드 페이지 플레이스홀더 생성
- 무엇을 했는지: Next.js App Router 기반 16개 placeholder 페이지 컴포넌트 생성
- 어떻게 수정했는지: "use client" React 컴포넌트로 각 페이지를 생성. 제목과 설명 텍스트를 포함한 기본 레이아웃 적용.
- 수정 파일:
  - frontend/src/app/(app)/trade/page.tsx (국내주식 거래)
  - frontend/src/app/(app)/trade/overseas/page.tsx (해외주식 거래)
  - frontend/src/app/(app)/trade/etf/page.tsx (ETF 거래)
  - frontend/src/app/(app)/trade/futures/page.tsx (선물/옵션 거래)
  - frontend/src/app/(app)/trade/bonds/page.tsx (채권 거래)
  - frontend/src/app/(app)/portfolio/page.tsx (포트폴리오)
  - frontend/src/app/(app)/market/page.tsx (시장 정보)
  - frontend/src/app/(app)/watchlist/page.tsx (관심 종목)
  - frontend/src/app/(app)/orders/page.tsx (주문 내역)
  - frontend/src/app/(app)/ai/page.tsx (AI 어시스턴트)
  - frontend/src/app/(app)/ai/strategies/page.tsx (AI 매매 전략)
  - frontend/src/app/(app)/ai/analysis/page.tsx (AI 시장 분석)
  - frontend/src/app/(app)/admin/users/page.tsx (유저 관리)
  - frontend/src/app/(app)/admin/shared-account/page.tsx (공용 계좌 관리)
  - frontend/src/app/(app)/settings/page.tsx (설정)
  - frontend/src/app/(app)/settings/accounts/page.tsx (KIS 계좌 관리)
- 검증: 모든 16개 파일 정상 생성 확인
- 메모: 모든 페이지는 CSS 변수(--card, --border, --muted-foreground) 기반 스타일링 사용. (app) route group 내에 배치.

## 2026-03-15 14:00 JST | Claude Code (Opus 4.6)

- 범위: Phase 1 전체 - 프로젝트 스캐폴딩
- 무엇을 했는지: Hantoo 트레이딩 플랫폼 Phase 1 완성 (Foundation)
- 어떻게 수정했는지:
  - Docker Compose (postgres, redis, backend, frontend, caddy) 설정
  - Caddy 리버스 프록시 (자동 HTTPS, 보안 헤더)
  - Backend: FastAPI + SQLAlchemy async 모델 10개 테이블 + Alembic
  - Backend: 인증 (JWT HttpOnly 쿠키, 초대코드 가입, TOTP 2FA)
  - Backend: KIS 계좌 CRUD (AppKey/Secret AES-256 암호화)
  - Backend: 공용 계좌 접근 권한 관리 (view/trade)
  - Frontend: Next.js 15 + React 19 + TanStack Query + Zustand
  - Frontend: 로그인/가입 페이지, 앱 레이아웃 (사이드바, 헤더)
  - Frontend: 20개 라우트 페이지 (대시보드, 거래 5종, 포트폴리오, 시장, AI 3종, 관리 등)
- 수정 파일: (주요)
  - docker-compose.yml, caddy/Caddyfile, .env.example, .gitignore
  - backend/: main.py, config.py, database.py, dependencies.py
  - backend/models/: user.py, kis_account.py, trade.py, portfolio.py, watchlist.py, alert.py, ai.py
  - backend/schemas/: auth.py, account.py
  - backend/routers/: auth.py, accounts.py
  - backend/utils/: security.py, encryption.py
  - backend/alembic/: env.py, script.py.mako
  - frontend/: package.json, next.config.ts, tsconfig.json
  - frontend/src/: app/layout.tsx, providers.tsx, globals.css
  - frontend/src/components/layout/: sidebar.tsx, header.tsx
  - frontend/src/stores/: auth-store.ts, trading-store.ts
  - frontend/src/lib/: api-client.ts, utils.ts
  - frontend/src/app/(auth)/: login/page.tsx, register/page.tsx
  - frontend/src/app/(app)/: 16개 페이지
- 검증: `npx next build` 성공 (20개 라우트 모두 정상 빌드)
- 메모:
  - Node.js는 fnm으로 설치됨 (v24.13.0), `source ~/.zshrc` 필요
  - 유저 요청: 모의투자(paper trading) 지원 → environment 필드로 이미 반영됨
  - 유저 요청: Caddy로 외부망 노출 → nginx 대신 caddy로 변경, 보안 헤더 추가
  - 유저 요청: 2FA → TOTP(pyotp) 구현 완료
  - 다음 단계: Phase 2 (시세 서비스, 차트, 관심종목)
