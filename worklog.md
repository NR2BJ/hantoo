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

## 2026-03-15 18:00 JST | Claude Code (Opus 4.6)

- 범위: Phase 2 - 시세, 차트, 관심종목 전체 구현 + 버그 수정
- 무엇을 했는지: KIS API 시세 조회, TradingView 차트, 관심종목 CRUD 전체 구현 및 디버깅
- 어떻게 수정했는지:
  - Backend: Redis 클라이언트, KIS 토큰 서비스, Rate Limiter, KIS HTTP 클라이언트, 캐시 헬퍼 생성
  - Backend: QuoteService (현재가/일봉/분봉/호가/체결/지수/검색)
  - Backend: KRX OTP 기반 CSV 다운로드로 종목 검색 (KIS search API 500 에러로 대체)
  - Backend: 지수 조회 에러 핸들링 (모의투자 서버 지수 미지원 → graceful skip)
  - Backend: INDEX_NAMES fallback dict 추가 (KIS가 지수명 빈값 반환 대응)
  - Frontend: TypeScript 타입, React Query 훅, TradingView 차트 컴포넌트
  - Frontend: 시장 정보 페이지, 종목 상세 페이지, 관심종목 페이지, 대시보드 지수 연동
- 수정 파일:
  - backend/app/services/redis_client.py (Create)
  - backend/app/services/kis_token_service.py (Create)
  - backend/app/services/rate_limiter.py (Create)
  - backend/app/services/kis_client.py (Create)
  - backend/app/services/cache.py (Create)
  - backend/app/services/quote_service.py (Create)
  - backend/app/services/stock_list.py (Create → Rewrite: JSON→OTP CSV)
  - backend/app/schemas/market.py (Create)
  - backend/app/schemas/watchlist.py (Create)
  - backend/app/routers/market.py (Create → Fix: indices error handling)
  - backend/app/routers/watchlists.py (Create)
  - backend/app/dependencies.py (Modify: ActiveAccount 추가)
  - backend/app/main.py (Modify: Redis lifecycle, 새 라우터 등록)
  - frontend/src/types/market.ts (Create)
  - frontend/src/hooks/use-market.ts (Create → Fix: search에서 account_id 제거)
  - frontend/src/hooks/use-watchlist.ts (Create)
  - frontend/src/components/charts/stock-chart.tsx (Create)
  - frontend/src/components/charts/mini-chart.tsx (Create)
  - frontend/src/app/(app)/market/page.tsx (Rewrite)
  - frontend/src/app/(app)/market/[symbol]/page.tsx (Create)
  - frontend/src/app/(app)/watchlist/page.tsx (Rewrite)
  - frontend/src/app/(app)/dashboard/page.tsx (Rewrite)
- 검증: 커밋 후 Portainer 재배포 필요
- 메모:
  - KIS search API (CTPF1604R) 500 에러 → KRX OTP CSV 로컬 검색으로 대체
  - KRX JSON API (getJsonData.cmd)도 HTML 반환 → OTP 방식 CSV 다운로드로 재작성
  - 모의투자 서버(openapivts)는 지수 조회 미지원 → asyncio.gather(return_exceptions=True)로 graceful 처리
  - 유저 요청: 지수 표시 커스터마이즈 (국장만이 아닌 글로벌 시장) → 추후 구현
  - 다음 단계: Phase 3 (매매 주문)

## 2026-03-15 20:00 JST | Claude Code (Opus 4.6)

- 범위: Phase 3 - 매매 주문 (매수/매도/정정/취소/조회)
- 무엇을 했는지: KIS API 주문 기능 전체 구현 (백엔드 서비스+라우터+프론트엔드 UI)
- 어떻게 수정했는지:
  - Backend: KIS 클라이언트에 hashkey 지원 추가 (POST 주문 요청용)
  - Backend: OrderService — place/modify/cancel/pending/filled/buyable 구현
  - Backend: 주문 스키마 (OrderCreate, OrderModify, PendingOrder, FilledOrder, BuyableAmount)
  - Backend: 주문 라우터 (POST/PUT/DELETE /api/orders, GET pending/filled/buyable)
  - Frontend: React Query 훅 (usePlaceOrder, useCancelOrder, usePendingOrders 등)
  - Frontend: 주문 폼 컴포넌트 (매수/매도 탭, 지정가/시장가, 확인 다이얼로그, 호가 연동)
  - Frontend: 거래 페이지 (차트+호가+주문폼 레이아웃), 주문내역 페이지 (미체결/체결 탭)
- 수정 파일:
  - backend/app/services/kis_client.py (Modify: hashkey 메서드, use_hashkey 옵션)
  - backend/app/services/order_service.py (Create)
  - backend/app/schemas/order.py (Create)
  - backend/app/routers/orders.py (Create)
  - backend/app/main.py (Modify: orders 라우터 등록)
  - frontend/src/types/market.ts (Modify: 주문 타입 추가)
  - frontend/src/hooks/use-orders.ts (Create)
  - frontend/src/components/trading/order-form.tsx (Create)
  - frontend/src/app/(app)/trade/page.tsx (Rewrite)
  - frontend/src/app/(app)/orders/page.tsx (Rewrite)
- 검증: 커밋 후 Portainer 재배포 필요, 모의투자 계좌로 매수→미체결→취소 플로우 테스트
- 메모:
  - KIS 주문 tr_id: 매수 TTTC0802U, 매도 TTTC0801U, 정정/취소 TTTC0803U (모의: V접두사)
  - hashkey: POST 주문 시 body에 대한 해시키를 별도 API로 발급받아 헤더에 포함
  - Trade 모델은 Phase 1에서 이미 정의됨 → create_all로 자동 생성
  - 주문 확인 다이얼로그: 실수 매매 방지용 필수 UI
  - 다음 단계: Phase 4 (포트폴리오 & 실시간 WebSocket)

## 2026-03-15 22:00 JST | Claude Code (Opus 4.6)

- 범위: Phase 4 - 포트폴리오 & 실시간 (REST 폴링 기반)
- 무엇을 했는지: 계좌 잔고/보유종목 조회, 대시보드 실데이터 연동, 포트폴리오 페이지 구현
- 어떻게 수정했는지:
  - Backend: PortfolioService — KIS inquire-balance (TTTC8434R) 기반 잔고/보유종목 조회, 10초 캐시
  - Backend: 포트폴리오 스키마 (AccountBalance, Holding)
  - Backend: 포트폴리오 라우터 (GET /api/portfolio/balance, GET /api/portfolio/holdings)
  - Frontend: useBalance/useHoldings 훅 (React Query 10초 폴링)
  - Frontend: 대시보드 SummaryCard 실데이터 연동 (총자산, 총손익, 보유종목수, 예수금)
  - Frontend: 대시보드 보유종목 테이블 → useHoldings 연동 (클릭 → /market/{symbol})
  - Frontend: 포트폴리오 페이지 전면 재작성 (자산배분 바, 상세 테이블, 비중 시각화)
- 수정 파일:
  - backend/app/services/portfolio_service.py (Create)
  - backend/app/schemas/portfolio.py (Create)
  - backend/app/routers/portfolio.py (Create)
  - backend/app/main.py (Modify: portfolio 라우터 등록)
  - frontend/src/types/market.ts (Modify: AccountBalance, Holding 타입 추가)
  - frontend/src/hooks/use-portfolio.ts (Create)
  - frontend/src/app/(app)/dashboard/page.tsx (Rewrite: 실데이터 연동)
  - frontend/src/app/(app)/portfolio/page.tsx (Rewrite: 자산배분+종목상세+비중)
- 검증: `npx next build` 성공 (모든 라우트 정상 빌드)
- 메모:
  - WebSocket 실시간은 Phase 7로 이동 (KIS WS 복잡성: approval_key, 바이너리 파싱, 구독관리)
  - REST 10초 폴링으로 실용적 실시간성 확보 (React Query refetchInterval)
  - KIS 필드 정규화: evlu_pfls_amt→pnl, evlu_pfls_rt→pnl_rate, pchs_avg_pric→avg_price
  - PortfolioSnapshot (일별 스냅샷)은 Phase 7 성과 분석에서 활용 예정
  - 다음 단계: Phase 5 (AI 어시스턴트)

## 2026-03-15 23:00 JST | Claude Code (Opus 4.6)

- 범위: Phase 4 보완 - 외화 잔고 조회 + 금융상품 계좌 처리
- 무엇을 했는지: 해외주식 외화(USD 등) 잔고 조회 API 추가, 금융상품 계좌 에러 처리
- 어떻게 수정했는지:
  - Backend: KIS CTRP6504R (해외주식 체결기준 잔고) 호출 추가 → 외화예수금, 환율, 해외종목
  - Backend: portfolio_service에 get_overseas_holdings(), _get_overseas_foreign_balances() 추가
  - Backend: 위탁계좌(01) 외 계좌 접근 시 명확한 에러 메시지 반환
  - Backend: AccountBalance에 foreign_balances, overseas_total_krw 필드 추가
  - Backend: OverseasHolding 스키마 추가 (통화, 환율, 시장명 포함)
  - Frontend: 포트폴리오 페이지에 외화자산 카드 (통화별 예수금/주식평가/합계/환율)
  - Frontend: 해외 보유종목 테이블 (USD 표시, 환율 컬럼)
  - Frontend: 자산배분 바에 해외주식 구분 추가 (국내/해외/현금)
  - Frontend: 금융상품 계좌 선택 시 경고 메시지 표시
- 수정 파일:
  - backend/app/schemas/portfolio.py (Modify: ForeignCurrencyBalance, OverseasHolding 추가)
  - backend/app/services/portfolio_service.py (Modify: 해외잔고 조회, 계좌타입 체크)
  - backend/app/routers/portfolio.py (Modify: overseas-holdings 엔드포인트 추가)
  - frontend/src/types/market.ts (Modify: ForeignCurrencyBalance, OverseasHolding 타입)
  - frontend/src/hooks/use-portfolio.ts (Modify: useOverseasHoldings 훅 추가)
  - frontend/src/app/(app)/portfolio/page.tsx (Rewrite: 외화+해외종목 표시)
- 검증: `npx next build` 성공
- 메모:
  - CTRP6504R: output1=해외종목별, output2=통화별요약(외화예수금), output3=원화환산총계
  - 금융상품 계좌(product_code≠01)는 KIS 국내주식 잔고조회 API 미지원
  - 환율은 당일 최초고시환율 기준 (실제 환전 시 다를 수 있음)
  - 모의투자 계좌에서는 해외주식 잔고 output1/2가 비어있을 수 있음

## 2026-03-15 23:30 JST | Claude Code (Opus 4.6)

- 범위: 금융상품 계좌 잔고 조회 지원 (CTRP6548R 폴백)
- 무엇을 했는지: 위탁계좌(01) 외 금융상품 계좌도 잔고/보유종목 조회 가능하도록 개선
- 어떻게 수정했는지:
  - Backend: get_balance()에서 product_code별 분기 — 01이면 TTTC8434R, 그 외는 CTRP6548R
  - Backend: _get_balance_account_overview() 신규 — CTRP6548R (투자계좌 자산현황, HTS 0891)
  - Backend: _get_holdings_account_overview() 신규 — CTRP6548R output1에서 보유종목 파싱
  - Backend: 기존 에러 던지기 제거 → CTRP6548R 시도 후 실패 시에만 에러
  - Frontend: 에러 메시지를 KIS 응답 포함하여 구체적으로 표시
- 수정 파일:
  - backend/app/services/portfolio_service.py (Modify: CTRP6548R 폴백 추가)
  - frontend/src/app/(app)/portfolio/page.tsx (Modify: 에러 메시지 개선)
- 검증: `npx next build` 성공
- 메모:
  - CTRP6548R: 범용 계좌 자산현황 API, product_code 01/19/21 등 다양하게 지원
  - 파라미터: CANO, ACNT_PRDT_CD, INQR_DVSN_1, BSPR_BF_DT_APLY_YN
  - output1=보유종목, output2=요약 (필드명이 TTTC8434R과 다를 수 있음)
  - 실제 금융상품 계좌로 테스트 필요 — 필드명 매핑이 정확한지 확인 필요

## 2026-03-16 00:00 JST | Claude Code (Opus 4.6)

- 범위: 포트폴리오 자산배분 바 버그 수정 + 외화잔고 필터링
- 무엇을 했는지: 자산배분 비율이 100%를 초과하거나 잘못 표시되던 문제 수정
- 어떻게 수정했는지:
  - Backend: 외화잔고에서 deposit+stock_value가 0인 통화 필터링 (모의투자에서 빈 통화 제거)
  - Backend: overseas_total_krw를 실제 외화잔고가 있을 때만 계산 (빈 계좌에서 KIS가 반환하는 의미없는 값 무시)
  - Frontend: 자산배분 바 비율 계산을 IIFE로 변경, 합계 100% 보장
  - Frontend: 현금 비율 = total - domestic - overseas로 역산 (독립 계산 → 차감 계산)
  - Frontend: 범례에 퍼센트 표시 추가, 바 내 텍스트는 8% 미만이면 숨김
- 수정 파일:
  - backend/app/services/portfolio_service.py (Modify: 외화잔고 0원 필터링, overseas_total_krw 조건부)
  - frontend/src/app/(app)/portfolio/page.tsx (Modify: 자산배분 바 비율 계산 수정)
- 검증: `npx next build` 성공
- 메모:
  - 모의투자 CTRP6504R: output2에 CNY/HKD/JPY/USD/VND 모두 반환하나 잔액 0, output3의 tot_asst_amt는 의미없는 값
  - ISA 계좌: overseas_total_krw가 실제 잔액과 무관하게 반환되어 비율 깨짐 → 필터링으로 해결
  - 금융상품 계좌: CTRP6548R으로 현금 잔액은 정상 조회 확인
