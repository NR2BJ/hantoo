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

## 2026-03-15 22:30 JST | Claude Code (Opus 4.6)

- 범위: KIS API 전체 엔드포인트 체크리스트 생성
- 무엇을 했는지: KIS 공식 GitHub(koreainvestment/open-trading-api)의 examples_llm/ 디렉토리에서 전체 API 함수 목록을 수집하여 체크리스트 MD 파일 생성
- 어떻게 수정했는지:
  - 8개 카테고리(국내주식, 해외주식, 채권, 국내선물옵션, 해외선물옵션, ETF/ETN, ELW, 인증) 전체 탐색
  - 국내주식 ~156개, 해외주식 ~50개, 채권 18개, 국내선물옵션 43개, 해외선물옵션 35개, ETF 6개, ELW 24개 함수 식별
  - 현재 구현 완료 17개 엔드포인트 ✅ 표시, 구현 예정 ~40개 🔲 표시, 나머지 ⬜ 보류
  - Phase별 구현 로드맵 포함 (Phase 5: 재무/뉴스, Phase 7: 랭킹/해외/WS)
- 수정 파일: `KIS_API_CHECKLIST.md` (신규 생성)
- 검증: 파일 생성 확인, 전체 ~333개 엔드포인트 포함
- 메모:
  - tr_id가 확인된 주요 엔드포인트: volume_rank(FHPST01710000), fluctuation(FHPST01700000), market_cap(FHPST01740000), top_interest_stock(FHPST01800000) 등
  - 채권/선물옵션/ELW는 가족용 플랫폼에서 우선순위 낮아 ⬜ 처리
  - KIS API 포털(apiportal.koreainvestment.com)에 더 상세한 스펙이 있으나, GitHub examples_llm 기준으로 충분히 포괄적

## 2026-03-15 23:30 JST | Claude Code (Opus 4.6)

- 범위: Phase 5 — 랭킹/시장정보 백엔드 구현
- 무엇을 했는지: KIS API 랭킹 엔드포인트 7개 구현 (거래량순위, 등락률, 시총, 인기종목, 신고가/저가, 투자자동향, 외국인/기관)
- 어떻게 수정했는지:
  - `ranking_service.py` 신규 생성: 7개 메서드, Redis 10초 캐시, KIS 응답 필드 파싱 (data_rank, mksc_shrn_iscd, hts_kor_isnm 등)
  - `ranking.py` 라우터 신규 생성: GET /api/ranking/{volume,fluctuation,market-cap,interest,highlow,investor,foreign}
  - `market.py` 스키마에 RankItem, InvestorItem 추가
  - `main.py`에 ranking 라우터 등록
  - 프론트엔드: RankItem/InvestorItem 타입 + use-ranking.ts 훅 7개 (30초 refetch)
  - UI 컴포넌트는 미포함 — Phase 7에서 대시보드/마켓에 배치 예정
- 수정 파일:
  - `backend/app/services/ranking_service.py` (신규)
  - `backend/app/routers/ranking.py` (신규)
  - `backend/app/schemas/market.py` (수정)
  - `backend/app/main.py` (수정)
  - `frontend/src/types/market.ts` (수정)
  - `frontend/src/hooks/use-ranking.ts` (신규)
  - `KIS_API_CHECKLIST.md` (7개 🔲→✅, Phase 로드맵 업데이트)
- 검증: `next build` 성공
- 메모:
  - Phase 순서 변경: AI(구 Phase 5,6)를 Phase 8로 이동, 해외주식을 Phase 6으로
  - 랭킹 API 파라미터: FID_COND_SCR_DIV_CODE가 각 API마다 다름 (20171, 20170, 20174, 20180, 20187 등)
  - KIS 응답 필드: 모든 랭킹 API가 동일 구조 (data_rank, mksc_shrn_iscd, hts_kor_isnm, stck_prpr 등)
  - 투자자 API(FHKST01010900): 응답 필드 구조가 다를 수 있어 실제 데이터 확인 필요

## 2026-03-15 17:00 JST | Claude Code (Opus 4.6)

- 범위: Phase 6 — 해외주식 (US Market: NASDAQ/NYSE/AMEX)
- 무엇을 했는지: 해외주식 시세/차트/검색/매매 백엔드 + 프론트엔드 전체 구현
- 어떻게 수정했는지:
  - 백엔드: 해외전용 스키마(schemas/overseas.py), 시세서비스(overseas_quote_service.py), 주문서비스(overseas_order_service.py), 라우터(routers/overseas.py) 신규 생성
  - /api/overseas/ prefix로 8개 엔드포인트: quote, candles, search, orders(CRUD), orders/filled, orders/buyable
  - 프론트엔드: OverseasQuote 등 11개 타입 추가, 해외시세/주문 훅 2개, 차트/주문폼 컴포넌트 2개, 거래 페이지 완성
  - KIS API 6개 tr_id 연동: HHDFS00000300(시세), FHKST03030100(차트), HHDFS76410000(검색), TTTT1002U/1006U(매매), TTTT1004U(정정취소), TTTS3035R(체결)
- 수정 파일:
  - `backend/app/schemas/overseas.py` (신규)
  - `backend/app/services/overseas_quote_service.py` (신규)
  - `backend/app/services/overseas_order_service.py` (신규)
  - `backend/app/routers/overseas.py` (신규)
  - `backend/app/main.py` (수정 — overseas 라우터 등록)
  - `frontend/src/types/market.ts` (수정 — 해외 타입 + formatUSD, getUSPriceColor 헬퍼)
  - `frontend/src/hooks/use-overseas-market.ts` (신규)
  - `frontend/src/hooks/use-overseas-orders.ts` (신규)
  - `frontend/src/components/charts/overseas-stock-chart.tsx` (신규)
  - `frontend/src/components/trading/overseas-order-form.tsx` (신규)
  - `frontend/src/app/(app)/trade/overseas/page.tsx` (수정 — 스켈레톤→완전 구현)
  - `KIS_API_CHECKLIST.md` (6개 🔲→✅)
- 검증: `next build` 성공
- 메모:
  - US 색상 컨벤션: 녹색=상승, 빨강=하락 (한국 반대)
  - 가격: float (USD 소수점 2자리) vs 국내 int (KRW)
  - Trade 모델의 market 필드에 "NAS"/"NYS"/"AMS" 저장 (기존 "KRX" 대비)
  - 매수가능금액: CTRP6504R output2의 USD 예수금 / 가격으로 계산
  - 검색: NAS/NYS/AMS 3개 거래소 asyncio.gather 병렬 조회
  - 해외 주문 Body: OVRS_ORD_UNPR (국내: ORD_UNPR), OVRS_EXCG_CD 추가 필요
  - 빈 페이지에 AAPL/TSLA/MSFT/AMZN/NVDA 퀵 선택 버튼 추가

## 2026-03-16 12:00 JST | Claude Code (Opus 4.6)

- 범위: 해외주식 종목 검색 버그 수정
- 무엇을 했는지: "pltr" 검색 시 무관한 종목이 알파벳순으로 나오는 문제 해결
- 어떻게 수정했는지:
  - 원인: HHDFS76410000(inquire-search)은 텍스트 검색 API가 아니라 조건 스크리너(가격대/시총/PER 등 숫자 필터). FND_COND에 "PLTR" 넣어도 무시되고 전체 종목이 반환됨
  - 해결: KIS 마스터 파일(.cod.zip) 다운로드 → 로컬 텍스트 검색으로 교체
  - `overseas_master.py` 신규 생성: NAS/NYS/AMS 3개 거래소 마스터 다운로드, cp949 파싱, Redis 24시간 캐시
  - `overseas_quote_service.py` 수정: search_stocks()에서 KIS API 호출 제거 → overseas_master.search_master() 호출로 교체
  - 관련성 정렬: exact match → prefix → symbol contains → name contains
- 수정 파일:
  - `backend/app/services/overseas_master.py` (신규)
  - `backend/app/services/overseas_quote_service.py` (수정)
- 검증: 커밋 후 Portainer 재배포 필요
- 메모:
  - KIS 마스터 파일 URL: https://new.real.download.dws.co.kr/common/master/{nas,nys,ams}mst.cod.zip
  - .cod 파일: 탭 구분, cp949 인코딩, 24개 컬럼 (심볼=4번째, 한글명=6번째, 영문명=7번째)
  - 첫 요청 시 다운로드 후 24시간 캐시 → 이후 검색은 Redis에서 즉시 응답
  - HHDFS76410000은 KIS_API_CHECKLIST에서 "조건검색"으로 용도 변경 표시 필요

## 2026-03-16 19:30 JST | Claude Code

- 범위: Phase 7 — 종목 분석 (재무/기업/뉴스/ETF)
- 무엇을 했는지: KIS API 9개 엔드포인트 백엔드 구현 + 프론트 hooks/types
- 어떻게 수정했는지:
  - 스키마: `analysis.py` (IncomeStatement, BalanceSheet, FinancialRatio, Estimate, InvestOpinion, Dividend, News, StockInfo)
  - 서비스 3개: `finance_service.py` (재무제표3+실적추정+투자의견), `corporate_service.py` (배당+뉴스+종목정보), `etf_service.py` (스텁)
  - 라우터 2개: `/api/finance` (5 endpoints), `/api/corporate` (4 endpoints)
  - 프론트: `use-analysis.ts` (11 hooks), `market.ts` (8 interfaces 추가)
  - KIS_API_CHECKLIST.md Phase 로드맵 재편성 (7~14), ⬜→🔲 대량 전환 (NXT/연금/ELW만 제외)
- 수정 파일:
  - backend/app/schemas/analysis.py (신규)
  - backend/app/services/finance_service.py (신규)
  - backend/app/services/corporate_service.py (신규)
  - backend/app/services/etf_service.py (신규)
  - backend/app/routers/finance.py (신규)
  - backend/app/routers/corporate.py (신규)
  - backend/app/main.py (라우터 등록)
  - frontend/src/types/market.ts (Analysis types 추가)
  - frontend/src/hooks/use-analysis.ts (신규)
  - KIS_API_CHECKLIST.md (전면 업데이트)
- 검증: `next build` 성공
- 메모:
  - tr_id 확인된 9개만 풀 구현, 나머지(재무비율 확장5+KSD 12+ETF 6)는 스텁
  - 캐시 TTL: 재무3600s, 추정1800s, 뉴스60s, 종목정보86400s
  - KIS API 응답 필드명은 실제 호출 시 검증 필요 (stac_yymm, sale_account 등)

## 2026-03-16 21:00 JST | Claude Code

- 범위: 데이터 확인용 테스트 UI 추가
- 무엇을 했는지: Phase 7 분석 데이터 + Phase 5 랭킹 데이터를 확인할 수 있는 최소 UI 생성
- 어떻게 수정했는지:
  - 종목 상세 페이지(/market/[symbol]): 7개 탭 추가 (차트/호가, 재무제표, 배당, 뉴스, 투자의견, 투자자동향, 종목정보)
  - 재무제표 탭: 연간/분기 토글, 손익계산서/재무상태표/재무비율/실적추정 4개 테이블
  - 시장정보 페이지(/market): 7개 랭킹 탭 추가 (거래량, 등락률, 시총, 관심종목, 52주신고저, 외인기관, 배당률)
  - 코스피/코스닥 마켓 전환 버튼, 상승/하락 정렬 버튼
  - 랭킹 종목 클릭 시 상세페이지로 이동
  - DataSection 컴포넌트: 로딩/에러/데이터 상태 표시
  - 금액 포매터: 억/만 단위 자동 변환
- 수정 파일:
  - frontend/src/app/(app)/market/[symbol]/page.tsx (전면 재작성)
  - frontend/src/app/(app)/market/page.tsx (전면 재작성)
- 검증: `next build` 성공
- 메모:
  - 디자인은 최소한 — Phase 13(UI 폴리시)에서 개선 예정
  - 사이드바 변경 불필요 — 시장정보 → 종목검색 → 종목클릭으로 자연스러운 동선
  - 모든 데이터 섹션에 로딩/에러 상태 표시로 API 디버깅 용이

## 2026-03-16 22:00 JST | Claude Code

- 범위: Phase 7 KIS API 파라미터/필드 매핑 버그 수정 (6건)
- 무엇을 했는지: 실제 배포 후 확인된 API 오류 전부 수정
- 어떻게 수정했는지:
  - finance_service: FID_DIV_CLS_CODE 반전, EPS 제거, 투자의견 필수파라미터 추가, 목표가 필드 수정
  - corporate_service: 배당 params 전면 교체, 뉴스 필수파라미터 추가, 종목정보 fallback 추가
  - ranking_service: 투자자 동향을 날짜별 시계열→개인/외인/기관 3행 pivot으로 변경
- 수정 파일:
  - backend/app/services/finance_service.py
  - backend/app/services/corporate_service.py
  - backend/app/services/ranking_service.py
- 검증: `next build` 성공, 커밋 cce2caa
- 메모:
  - FHKST01010900(투자자): 한 행=한 날짜, prsn/frgn/orgn 접두사로 구분
  - 뉴스/배당: output1 키 사용 (output 아님)
  - 모의투자 서버에서 일부 API 미지원 가능

## 2026-03-16 23:30 JST | Claude Code

- 범위: Phase 7 Round 2 — KIS API 버그 전면 수정 (8건)
- 무엇을 했는지: 로컬 KIS API 레퍼런스(docs/kis-api-reference/examples_llm/) 기반으로 모든 파라미터/응답 필드 재검증 및 수정
- 어떻게 수정했는지:
  1. **Python falsy 버그**: `_safe_int(val) or None` → `_opt_int(val)` 도입 (0이 None 되는 문제 해결)
     - finance_service.py: income/balance/ratio/estimate 전부 _opt_int/_opt_float 적용
     - corporate_service.py: dividend/stock_info 동일 적용
  2. **등락률 순위(fluctuation)**: uppercase→lowercase 파라미터, fid_input_cnt_1/fid_prc_cls_code/fid_rsfl_rate1/2 추가
  3. **52주 신고저(near_new_highlow)**: FID_RANK_SORT_CLS_CODE→fid_prc_cls_code(0=신고,1=신저), fid_aply_rang_vol/prc/cnt 추가
  4. **배당수익률 랭킹(dividend_rate)**: FID_* 파라미터 전면 교체 → CTS_AREA/GB1/UPJONG/GB2/GB3/F_DT/T_DT/GB4, output1 사용
  5. **외국인/기관(foreign_institution)**: FID_COND_MRKT_DIV_CODE "J"→"V", 코스닥 시 FID_INPUT_ISCD "1001"
  6. **투자의견(invest_opinion)**: uppercase→lowercase 파라미터, invt_opnn_cls_code→한글 매핑(매수/중립/매도), 변동=현재vs직전 비교
  7. **실적추정(estimate_perform)**: FID_INPUT_ISCD→SHT_CD, output→output1
  8. **지수 깜빡임**: useIndices/useQuote에 placeholderData: keepPreviousData 추가
- 수정 파일:
  - backend/app/services/finance_service.py — _opt_int/_opt_float 추가, 전 서비스 적용, estimate SHT_CD, opinion lowercase+코드매핑
  - backend/app/services/corporate_service.py — _opt_int/_opt_float 추가, dividend_rate 파라미터 전면교체, stock_info 로깅 추가
  - backend/app/services/ranking_service.py — fluctuation/near_highlow/foreign_institution 파라미터 전면 수정, investor 로깅 추가
  - frontend/src/hooks/use-market.ts — keepPreviousData import, useIndices/useQuote에 placeholderData 적용
- 검증: `next build` 성공, Python syntax check 통과
- 메모:
  - KIS API 파라미터 대소문자가 API마다 다름: fluctuation=lowercase, volume-rank=uppercase, dividend-rate=특수(CTS_AREA etc.)
  - docs/kis-api-reference/examples_llm/에 333개 API 스펙 파일 있으므로 향후 새 API 추가 시 반드시 참조
  - 투자자 데이터: 장 종료 후에만 당일 데이터 제공됨 → 장중에는 0이 정상

## 2026-03-17 00:30 JST | Claude Code (Opus 4.6)

- 범위: Phase 7 API 버그 Round 3 — 필드명 검증 및 디버그 로깅 강화
- 무엇을 했는지:
  1. **finance_service.py 전면 개선**:
     - estimate_perform: 듀얼 포맷 파싱 (Format A: 네임드 필드 sale_account 등 / Format B: data1-data5 제네릭)
     - financial_ratio: per/pbr/roa_val은 이 API에 없음 확인 → None 폴백 + 주석 추가
     - 모든 API 응답에 debug logger.info 추가 (response keys, first row keys, sample data)
  2. **corporate_service.py 전면 개선**:
     - stock_info: CTPF1604R(12필드) → CTPF1002R(91+필드) 전환, CTPF1604R을 폴백으로 유지
     - 마켓코드: mket_id_cd(STK→KOSPI, KSQ→KOSDAQ) + rprs_mrkt_kor_name 폴백
     - 섹터: idx_bztp_mcls_cd_name → idx_bztp_lcls_cd_name → std_idst_clsf_cd_name 순 폴백
     - 상장일: scts_mket_lstg_dt → kosdaq_mket_lstg_dt → lstg_dt → frst_erlm_dt → sale_strt_dt 순 폴백
     - dividend_rate_ranking: 종목명 다중 필드 시도 (hts_kor_isnm, isin_name, prdt_abrv_name), 없으면 심볼 폴백
     - 모든 API 응답에 debug logger.info 추가
- 어떻게 수정했는지: KIS API 로컬 레퍼런스(examples_llm) 기반 필드명 교차 검증 + 실 API 확인 불가로 디버그 로깅 추가
- 수정 파일:
  - backend/app/services/finance_service.py — estimate 듀얼포맷, ratio 필드 정리, 전체 디버그 로깅
  - backend/app/services/corporate_service.py — CTPF1002R 전환, 다중필드 폴백, 전체 디버그 로깅
- 검증: commit e150e47, git push 완료
- 메모:
  - 보안: 내부망 외부 노출 대신 Docker 컨테이너 로그(Portainer)로 실 API 응답 확인하는 전략
  - 배포 후 Portainer에서 `[dividend]`, `[stock_info]`, `[estimate]`, `[income]` 등으로 로그 검색하면 실제 필드명/값 확인 가능
  - estimate_perform의 data1-5가 실제로 매출/영업이익/순이익/EPS 순서인지는 로그로 확인 필요
  - financial_ratio에서 PER/PBR은 주가 정보 API(quote)에서 가져와야 할 수 있음

## 2026-03-17 01:15 JST | Claude Code (Opus 4.6)

- 범위: Phase 7 API 버그 Round 4 — 로깅 설정 + VTS 500 에러 graceful 처리
- 무엇을 했는지:
  1. **로깅 레벨 수정**: Python 기본 root logger가 WARNING이라 `logger.info()` 디버그 로그가 안 보였음 → `logging.basicConfig(level=INFO)` 추가
  2. **VTS 500 에러 graceful 처리**:
     - finance_service: balance-sheet/financial-ratio에 try/except 추가, 실패 시 빈 리스트 반환
     - corporate_service: CTPF1002R+CTPF1604R 둘 다 실패 시 최소 StockInfoDetail 반환 (symbol만)
     - 모든 라우터(ranking/finance/corporate): `raise HTTPException(500)` → `return []` 변경
     - 프론트엔드가 에러 상태 대신 빈 데이터를 표시하도록 개선
- 수정 파일:
  - backend/app/main.py — logging.basicConfig(level=INFO)
  - backend/app/services/finance_service.py — balance-sheet, financial-ratio try/except
  - backend/app/services/corporate_service.py — stock_info 이중 폴백 후 최소 데이터 반환
  - backend/app/routers/ranking.py — 7개 엔드포인트 500→빈리스트
  - backend/app/routers/finance.py — 5개 엔드포인트 500→빈리스트
  - backend/app/routers/corporate.py — 4개 엔드포인트 500→빈데이터
- 검증: Python syntax check 통과, commit 4b2c10b, push 완료
- 메모:
  - **결정사항**: 모의투자/실전투자 메인 탭 분리 예정 (UI는 추후, 계획만 기록)
  - 사용자가 정보 조회는 앞으로 실전 계좌로 하겠다고 함
  - 실전 계좌 전환 후 디버그 로그(INFO 레벨)로 실제 응답 구조 확인 가능
  - VTS 서버: search-stock-info, balance-sheet, financial-ratio 등 많은 API가 500 또는 간헐적 실패

## 2026-03-17 01:50 JST | Claude Code (Opus 4.6)

- 범위: Phase 7 API 버그 Round 5 — estimate 전치 구조 파싱 + 캐시 키 환경 분리
- 무엇을 했는지:
  1. **estimate_perform 완전 재작성**:
     - 실전 서버 로그에서 확인: output1=메타 dict, output2=지표별 행×연도별 열 (전치 구조), output4=연도 레이블
     - 기존: output1을 리스트로 순회 → 데이터 못 읽음
     - 수정: output4에서 날짜 추출, output2 행(매출=0,영업이익=1,당기순이익=3,EPS=4)에서 열별 피벗
     - 삼성전자 기준: data1=2589355.0 (2023매출 259조, 억원 단위) 확인
  2. **캐시 키에 환경(prod/paper) 추가**:
     - 기존: `kis:finance:income:{symbol}:{period}` → VTS에서 캐시된 빈 데이터가 실전에서도 반환
     - 수정: `kis:{environment}:finance:income:{symbol}:{period}` → 환경별 캐시 분리
     - finance_service 5개, corporate_service 4개, ranking_service 7개 키 모두 수정
- 수정 파일:
  - backend/app/services/finance_service.py — estimate 전치 파싱 + 캐시 키 5개
  - backend/app/services/corporate_service.py — 캐시 키 4개
  - backend/app/services/ranking_service.py — 캐시 키 7개
- 검증: Python syntax check 통과, commit 164d889, push 완료
- 메모:
  - estimate output2 행 순서: 매출액(0), 영업이익(1), 세전이익(2), 당기순이익(3), EPS(4), BPS(5) — 추정
  - estimate output3: 비율 지표 8행 (영업이익률, ROE, PER 등) — 현재 미사용
  - 배포 후 Redis에 기존 VTS 캐시가 남아있을 수 있음 → 새 키 형식이므로 자연히 새로 조회됨
  - income/balance/ratio의 실전 서버 응답 구조는 다음 조회 시 로그로 확인 가능

## 2026-03-17 02:30 JST | Claude Code (Opus 4.6)

- 범위: Phase 7 API 버그 Round 6 — float 문자열 파싱 근본 수정
- 무엇을 했는지:
  - **근본 원인**: KIS API가 숫자를 float 문자열로 반환 (`sale_account: '3336059.00'`, `eps: '6564.00'`, `data1: '2589355.0'`), 하지만 `int("3336059.00")`은 Python에서 ValueError 발생 → `_opt_int`/`_safe_int`가 전부 None/0 반환
  - **수정**: `int(val)` → `int(float(val))`로 변경 — 3개 서비스 파일의 모든 `_safe_int`, `_opt_int` 함수
- 수정 파일:
  - backend/app/services/finance_service.py — `_safe_int`, `_opt_int`
  - backend/app/services/corporate_service.py — `_safe_int`, `_opt_int`
  - backend/app/services/ranking_service.py — `_safe_int`
- 검증: 커밋 후 배포 필요
- 메모:
  - Python `int("3336059.00")` → ValueError, `int(float("3336059.00"))` → 3336059 ✓
  - 이 버그가 Round 4~5에서 "API는 200 OK인데 UI가 비어있는" 현상의 근본 원인
  - `_safe_float`은 `float(val)`로 이미 정상 동작하므로 변경 불필요

## 2026-03-17 03:00 JST | Claude Code (Opus 4.6)

- 범위: 캐시 플러시 + 수동 새로고침 버튼 추가
- 무엇을 했는지:
  1. **백엔드 캐시 플러시 엔드포인트 개선**: `POST /api/cache/flush?symbol=005930` 또는 `?scope=ranking` 으로 선택적 캐시 삭제 가능
  2. **종목 상세 페이지 새로고침 버튼**: 클릭 시 해당 종목 Redis 캐시 삭제 + React Query 캐시 무효화 → KIS API에서 새로 가져옴
  3. **시장 정보 페이지 새로고침 버튼**: 클릭 시 ranking 스코프 Redis 캐시 삭제 + 순위/지수 React Query 캐시 무효화
- 수정 파일:
  - backend/app/main.py — cache/flush 엔드포인트에 symbol, scope 파라미터 추가
  - frontend/src/app/(app)/market/[symbol]/page.tsx — 새로고침 버튼 (symbol 기준 캐시 플러시)
  - frontend/src/app/(app)/market/page.tsx — 새로고침 버튼 (ranking 스코프 캐시 플러시)
- 메모:
  - 순위 데이터: 백엔드 10초 캐시 + 프론트 30초 폴링 — KIS 초당 1회 제한 보호용으로 필요
  - 재무/종목정보: 분기~연 단위 변경이므로 긴 캐시 유지, 수동 새로고침으로 강제 갱신 가능
  - **중요**: Round 6 배포 후 반드시 `POST /api/cache/flush` 호출하여 기존 깨진 캐시 제거 필요

## 2026-03-17 04:00 JST | Claude Code (Opus 4.6)

- 범위: Phase 7 API 버그 Round 7 — KISApiError 400 응답 수정 + 백그라운드 폴링 중지
- 무엇을 했는지:
  1. **KISApiError → 빈 데이터 반환**: 코스닥(Q) 요청 시 KIS API가 rt_cd≠"0" 반환 → `KISApiError` → 라우터가 `HTTPException(400)` 재발생 → 프론트에 에러 표시됨. 모든 16개 엔드포인트에서 `KISApiError`를 잡아서 빈 리스트/기본 객체 반환하도록 수정
  2. **백그라운드 폴링 중지**: 탭 비활성 시 불필요한 API 호출 방지 — `refetchIntervalInBackground: false` 추가
- 어떻게 수정했는지:
  - `except KISApiError as e: raise HTTPException(400, ...)` → `except KISApiError as e: logger.info(...); return []`
  - stock-info 엔드포인트는 빈 리스트 대신 최소 `StockInfoDetail(symbol=symbol, name=symbol, ...)` 반환
- 수정 파일:
  - backend/app/routers/ranking.py — 7개 엔드포인트 KISApiError 핸들링
  - backend/app/routers/finance.py — 5개 엔드포인트 KISApiError 핸들링
  - backend/app/routers/corporate.py — 4개 엔드포인트 KISApiError 핸들링
  - frontend/src/hooks/use-ranking.ts — 7개 훅에 refetchIntervalInBackground: false
  - frontend/src/hooks/use-analysis.ts — useNews 훅에 refetchIntervalInBackground: false
- 검증: 커밋 완료 (220fa83, 6a4742c). 배포 후 새로고침 버튼으로 캐시 플러시 필요
- 메모:
  - KIS API는 HTTP 200 반환하지만 `rt_cd != "0"`인 경우 논리적 에러 — 코스닥 쿼리에서 자주 발생
  - `invalidateQueries`는 마운트된 쿼리만 리페치 — 탭 미선택 시 데이터 안 불러옴 (정상 동작, lazy loading)

## 2026-03-17 05:00 JST | Claude Code (Opus 4.6)

- 범위: Phase 7 버그 Round 8 — KOSDAQ 제거, quote 파싱 수정, 에러 핸들링 추가
- 무엇을 했는지:
  1. **KOSDAQ 버튼 제거**: KIS 순위 API 대부분 코스닥(Q) 미지원 (거래량/등락률/시총/관심/신고저 전부 J만 지원). 서비스에서 미지원 마켓코드면 API 호출 없이 빈 배열 반환
  2. **quote_service.py `_safe_int` 수정**: Round 6에서 finance/corporate/ranking은 수정했지만 quote_service는 빠뜨림 — `int(val)` → `int(float(val))`
  3. **종목명 표시 수정**: `quote?.name ?? symbol` → `quote?.name || symbol` (빈 문자열은 nullish coalescing에 안 걸림)
  4. **market.py 에러 핸들링**: quote/orderbook/candles/trades 라우터에 KISApiError+Exception 처리 추가 — 에러 시 빈 데이터 반환
  5. **오도하는 UI 메시지 수정**: "KIS 계좌를 선택하세요" → "로딩 중..." / "체결 데이터 없음"
- 수정 파일:
  - backend/app/services/quote_service.py — `_safe_int` 수정
  - backend/app/services/ranking_service.py — 미지원 마켓코드 조기 반환
  - backend/app/routers/market.py — KISApiError 핸들링 추가
  - frontend/src/app/(app)/market/page.tsx — KOSDAQ 버튼 제거, 코스닥 미지원 메시지
  - frontend/src/app/(app)/market/[symbol]/page.tsx — 종목명 표시 수정, 폴백 메시지 수정
- 검증: 커밋 완료 (d7c50e2, 31a946a). 배포 후 `POST /api/cache/flush` 호출 필요
- 메모:
  - 장 마감 시(17시 이후) 시가/고가/저가/거래량=0은 정상 — KIS API가 당일 세션 데이터를 반환하므로 장 미개장 시 0
  - 코스닥 지원되는 API: 외인/기관(V코드), 배당률(GB1=3)만 해당
  - KIS API 문서 vs 실제: fluctuation은 Q 지원한다고 문서에 있지만 실제로는 에러 반환
