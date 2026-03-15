# KIS Open API 전체 엔드포인트 체크리스트

> **목적**: Hantoo 프로젝트에서 KIS API를 빠짐없이 활용하기 위한 전체 엔드포인트 목록.
> KIS 공식 GitHub (`koreainvestment/open-trading-api` — `examples_llm/`) 기준 수집.
>
> **최종 업데이트**: 2026-03-16

## 범례
- ✅ 구현 완료
- 🔲 미구현 (구현 예정)
- ⬜ 제외 (NXT 별도 / 연금 / ELW)

---

## 1. 인증 (Auth)

| 상태 | 함수명 | 설명 | Hantoo 파일 |
|------|--------|------|-------------|
| ✅ | 접근토큰 발급 | OAuth access token 발급/갱신 | `kis_token_service.py` |
| ✅ | HashKey 발급 | POST 주문 요청 시 hashkey 생성 | `kis_client.py` |
| 🔲 | WebSocket 접속키 발급 | approval_key for WS 실시간 | — |

---

## 2. 국내주식 시세 (Domestic Stock — Quotes)

| 상태 | 함수명 | API Path | tr_id | 설명 | Hantoo 파일 |
|------|--------|----------|-------|------|-------------|
| ✅ | inquire_price | `/uapi/domestic-stock/v1/quotations/inquire-price` | `FHKST01010100` | 현재가 조회 | `quote_service.py` |
| 🔲 | inquire_price_2 | `/uapi/domestic-stock/v1/quotations/inquire-price-2` | `FHPST01010000` | 현재가 조회 (확장) | — |
| ✅ | inquire_asking_price_exp_ccn | `/uapi/domestic-stock/v1/quotations/inquire-asking-price-exp-ccn` | `FHKST01010200` | 호가/예상체결 | `quote_service.py` |
| ✅ | inquire_ccnl | `/uapi/domestic-stock/v1/quotations/inquire-ccnl` | `FHKST01010300` | 체결(틱) | `quote_service.py` |
| ✅ | inquire_daily_price | `/uapi/domestic-stock/v1/quotations/inquire-daily-price` | `FHKST01010400` | 일별시세 | `quote_service.py` |
| 🔲 | inquire_investor | `/uapi/domestic-stock/v1/quotations/inquire-investor` | `FHKST01010900` | 투자자별 매매동향 | — |
| ✅ | inquire_time_itemchartprice | `/uapi/domestic-stock/v1/quotations/inquire-time-itemchartprice` | `FHKST03010200` | 분봉 차트 | `quote_service.py` |
| 🔲 | inquire_daily_itemchartprice | `/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice` | `FHKST03010100` | 일봉 차트 (기간별) | — |
| ✅ | inquire_index_price | `/uapi/domestic-stock/v1/quotations/inquire-index-price` | `FHPUP02100000` | 지수 시세 | `quote_service.py` |
| 🔲 | inquire_index_category_price | — | — | 업종별 지수 시세 | — |
| 🔲 | inquire_index_daily_price | — | — | 지수 일별 시세 | — |
| 🔲 | inquire_index_tickprice | — | — | 지수 틱 시세 | — |
| 🔲 | inquire_index_timeprice | — | — | 지수 시간별 시세 | — |
| 🔲 | inquire_daily_indexchartprice | — | — | 지수 일봉 차트 | — |
| 🔲 | inquire_time_indexchartprice | — | — | 지수 시간 차트 | — |
| 🔲 | inquire_daily_trade_volume | `/uapi/domestic-stock/v1/quotations/inquire-daily-trade-volume` | `FHKST03010800` | 일별 거래량 상세 | — |
| 🔲 | search_info | `/uapi/domestic-stock/v1/quotations/search-info` | `CTPF1604R` | 종목 기본정보 조회 | — |
| 🔲 | search_stock_info | — | — | 종목 상세정보 검색 | — |
| 🔲 | inquire_overtime_price | `/uapi/domestic-stock/v1/quotations/inquire-overtime-price` | `FHPST02300000` | 시간외 현재가 | — |
| 🔲 | inquire_daily_overtimeprice | — | — | 시간외 일별 시세 | — |
| 🔲 | inquire_overtime_asking_price | — | — | 시간외 호가 | — |

### 호가/체결 (KRX/NXT/Total)

| 상태 | 함수명 | 설명 |
|------|--------|------|
| 🔲 | asking_price_krx | KRX 호가 |
| ⬜ | asking_price_nxt | NXT 호가 |
| 🔲 | asking_price_total | 통합 호가 |
| 🔲 | ccnl_krx | KRX 체결 |
| ⬜ | ccnl_nxt | NXT 체결 |
| 🔲 | ccnl_total | 통합 체결 |

### 예상체결/장전

| 상태 | 함수명 | 설명 |
|------|--------|------|
| 🔲 | exp_ccnl_krx | KRX 예상체결 |
| ⬜ | exp_ccnl_nxt | NXT 예상체결 |
| 🔲 | exp_ccnl_total | 통합 예상체결 |
| 🔲 | exp_closing_price | 예상 종가 |
| 🔲 | exp_index_trend | 예상 지수 추이 |
| 🔲 | exp_price_trend | 예상 가격 추이 |
| 🔲 | exp_total_index | 예상 종합 지수 |
| 🔲 | exp_trans_updown | 예상 등락 |
| 🔲 | index_exp_ccnl | 지수 예상 체결 |
| 🔲 | overtime_exp_ccnl_krx | 시간외 예상체결 |
| 🔲 | overtime_exp_trans_fluct | 시간외 등락 |

### 시장 상태/기타

| 상태 | 함수명 | 설명 |
|------|--------|------|
| 🔲 | market_status_krx | KRX 장 상태 |
| ⬜ | market_status_nxt | NXT 장 상태 |
| 🔲 | market_status_total | 통합 장 상태 |
| 🔲 | market_time | 장 시간 |
| 🔲 | chk_holiday (`CTCA0903R`) | 휴장일 확인 |
| 🔲 | market_value | 시가총액 (종목별) |
| 🔲 | mktfunds | 시장 자금 |
| 🔲 | intstock_grouplist | 관심종목 그룹 목록 |
| 🔲 | intstock_multprice | 관심종목 복수 시세 |
| 🔲 | intstock_stocklist_by_group | 그룹별 관심종목 |
| 🔲 | psearch_title | 조건검색 제목 |
| 🔲 | psearch_result | 조건검색 결과 |

---

## 3. 국내주식 주문/잔고 (Domestic Stock — Trading)

| 상태 | 함수명 | API Path | tr_id (실전/모의) | 설명 | Hantoo 파일 |
|------|--------|----------|-------------------|------|-------------|
| ✅ | order_cash (매수) | `/uapi/domestic-stock/v1/trading/order-cash` | `TTTC0802U` / `VTTC0802U` | 현금 매수 | `order_service.py` |
| ✅ | order_cash (매도) | `/uapi/domestic-stock/v1/trading/order-cash` | `TTTC0801U` / `VTTC0801U` | 현금 매도 | `order_service.py` |
| 🔲 | order_credit | `/uapi/domestic-stock/v1/trading/order-credit` | — | 신용 주문 | — |
| 🔲 | order_resv | — | — | 예약 주문 | — |
| 🔲 | order_resv_ccnl | — | — | 예약 주문 체결 조회 | — |
| 🔲 | order_resv_rvsecncl | — | — | 예약 주문 정정/취소 | — |
| ✅ | order_rvsecncl | `/uapi/domestic-stock/v1/trading/order-rvsecncl` | `TTTC0803U` / `VTTC0803U` | 정정/취소 | `order_service.py` |
| ✅ | inquire_psbl_order | `/uapi/domestic-stock/v1/trading/inquire-psbl-order` | `TTTC8908R` / `VTTC8908R` | 주문가능금액 | `order_service.py` |
| 🔲 | inquire_psbl_sell | — | — | 매도가능수량 | — |
| ✅ | inquire_psbl_rvsecncl | `/uapi/domestic-stock/v1/trading/inquire-psbl-rvsecncl` | `TTTC8036R` / `VTTC8036R` | 미체결 주문 | `order_service.py` |
| ✅ | inquire_daily_ccld | `/uapi/domestic-stock/v1/trading/inquire-daily-ccld` | `TTTC8001R` / `VTTC8001R` | 체결내역 | `order_service.py` |
| ✅ | inquire_balance | `/uapi/domestic-stock/v1/trading/inquire-balance` | `TTTC8434R` / `VTTC8434R` | 잔고(위탁) | `portfolio_service.py` |
| ✅ | inquire_account_balance | `/uapi/domestic-stock/v1/trading/inquire-account-balance` | `CTRP6548R` | 계좌자산현황(비위탁) | `portfolio_service.py` |
| 🔲 | inquire_balance_rlz_pl | `/uapi/domestic-stock/v1/trading/inquire-balance-rlz-pl` | `TTTC8494R` | 실현손익 조회 | — |
| 🔲 | after_hour_balance | — | — | 시간외 잔고 | — |
| 🔲 | credit_balance | — | — | 신용 잔고 | — |
| 🔲 | credit_by_company | — | — | 증권사별 신용 | — |
| 🔲 | daily_credit_balance | — | — | 일별 신용 잔고 | — |
| 🔲 | quote_balance | — | — | 시세 잔고 | — |
| 🔲 | intgr_margin | — | — | 통합 증거금 | — |
| 🔲 | inquire_credit_psamount | — | — | 신용 가능 금액 | — |
| 🔲 | inquire_period_profit | — | — | 기간별 수익률 | — |
| 🔲 | inquire_period_trade_profit | — | — | 기간별 매매 수익률 | — |

### 연금 계좌 ⬜ 제외

| 상태 | 함수명 | 설명 |
|------|--------|------|
| ⬜ | pension_inquire_balance | 연금 잔고 |
| ⬜ | pension_inquire_present_balance | 연금 현재 잔고 |
| ⬜ | pension_inquire_daily_ccld | 연금 체결내역 |
| ⬜ | pension_inquire_deposit | 연금 예수금 |
| ⬜ | pension_inquire_psbl_order | 연금 주문가능액 |

---

## 4. 국내주식 순위/랭킹 (Domestic Stock — Rankings)

| 상태 | 함수명 | API Path | tr_id | 설명 |
|------|--------|----------|-------|------|
| ✅ | volume_rank | `/uapi/domestic-stock/v1/quotations/volume-rank` | `FHPST01710000` | 거래량 순위 | `ranking_service.py` |
| ✅ | fluctuation | `/uapi/domestic-stock/v1/ranking/fluctuation` | `FHPST01700000` | 등락률 순위 | `ranking_service.py` |
| ✅ | market_cap | `/uapi/domestic-stock/v1/ranking/market-cap` | `FHPST01740000` | 시가총액 순위 | `ranking_service.py` |
| ✅ | top_interest_stock | `/uapi/domestic-stock/v1/ranking/top-interest-stock` | `FHPST01800000` | 인기종목 (관심도) | `ranking_service.py` |
| ✅ | near_new_highlow | `/uapi/domestic-stock/v1/ranking/near-new-highlow` | `FHPST01870000` | 신고가/신저가 근접 | `ranking_service.py` |
| 🔲 | capture_uplowprice | `/uapi/domestic-stock/v1/quotations/capture-uplowprice` | `FHKST130000C0` | 상한가/하한가 포착 |
| 🔲 | inquire_vi_status | `/uapi/domestic-stock/v1/quotations/inquire-vi-status` | `FHPST01390000` | VI 발동 현황 |
| 🔲 | disparity | — | — | 이격도 |
| 🔲 | volume_power | — | — | 체결강도 |
| 🔲 | overtime_fluctuation | — | — | 시간외 등락 |
| 🔲 | overtime_volume | — | — | 시간외 거래량 |
| 🔲 | pbar_tratio | — | — | 매수비율 |
| 🔲 | prefer_disparate_ratio | — | — | 우선주 괴리율 |
| 🔲 | profit_asset_index | — | — | 수익자산지표 |
| 🔲 | hts_top_view | — | — | HTS 인기 화면 |
| 🔲 | tradprt_byamt | — | — | 거래대금별 |
| 🔲 | bulk_trans_num | — | — | 대량체결건수 |
| 🔲 | comp_interest | — | — | 관심종목 비교 |

---

## 5. 국내주식 재무/기업정보 (Domestic Stock — Financials)

| 상태 | 함수명 | API Path | tr_id | 설명 |
|------|--------|----------|-------|------|
| 🔲 | finance_income_statement | `/uapi/domestic-stock/v1/finance/income-statement` | `FHKST66430200` | 손익계산서 |
| 🔲 | finance_balance_sheet | `/uapi/domestic-stock/v1/finance/balance-sheet` | `FHKST66430100` | 재무상태표 |
| 🔲 | finance_financial_ratio | `/uapi/domestic-stock/v1/finance/financial-ratio` | `FHKST66430300` | 재무비율 |
| 🔲 | finance_growth_ratio | — | — | 성장비율 |
| 🔲 | finance_profit_ratio | — | — | 수익비율 |
| 🔲 | finance_stability_ratio | — | — | 안정성비율 |
| 🔲 | finance_other_major_ratios | — | — | 기타 주요 비율 |
| 🔲 | finance_ratio | — | — | 재무비율 (종합) |
| 🔲 | estimate_perform | `/uapi/domestic-stock/v1/quotations/estimate-perform` | `HHKST668300C0` | 실적추정치 |
| 🔲 | invest_opinion | `/uapi/domestic-stock/v1/quotations/invest-opinion` | `FHKST663300C0` | 투자의견/컨센서스 |

---

## 6. 국내주식 투자자/프로그램매매 (Domestic Stock — Investor/Program)

### 투자자 매매동향

| 상태 | 함수명 | API Path | tr_id | 설명 |
|------|--------|----------|-------|------|
| ✅ | inquire_investor | `/uapi/domestic-stock/v1/quotations/inquire-investor` | `FHKST01010900` | 종목별 투자자 매매동향 | `ranking_service.py` |
| ✅ | foreign_institution_total | `/uapi/domestic-stock/v1/quotations/foreign-institution-total` | `FHPTJ04400000` | 외국인/기관 합산 | `ranking_service.py` |
| 🔲 | inquire_investor_daily_by_market | — | — | 시장별 일별 투자자 |
| 🔲 | inquire_investor_time_by_market | — | — | 시장별 시간별 투자자 |
| 🔲 | investor_trade_by_stock_daily | — | — | 종목별 일별 투자자 매매 |
| 🔲 | investor_trend_estimate | — | — | 투자자 동향 추정 |
| 🔲 | frgnmem_pchs_trend | — | — | 외국인 매수 추이 |
| 🔲 | frgnmem_trade_estimate | — | — | 외국인 거래 추정 |
| 🔲 | frgnmem_trade_trend | — | — | 외국인 거래 추이 |
| 🔲 | invest_opbysec | — | — | 증권사별 투자의견 |

### 프로그램 매매

| 상태 | 함수명 | 설명 |
|------|--------|------|
| 🔲 | program_trade_krx | KRX 프로그램 매매 |
| ⬜ | program_trade_nxt | NXT 프로그램 매매 |
| 🔲 | program_trade_total | 통합 프로그램 매매 |
| 🔲 | program_trade_by_stock | 종목별 프로그램 매매 |
| 🔲 | program_trade_by_stock_daily | 종목별 일별 프로그램 매매 |
| 🔲 | comp_program_trade_daily | 일별 프로그램 매매 비교 |
| 🔲 | comp_program_trade_today | 당일 프로그램 매매 비교 |
| 🔲 | investor_program_trade_today | 투자자별 당일 프로그램 |
| 🔲 | index_program_trade | 지수 프로그램 매매 |

### 회원사/대차/공매도

| 상태 | 함수명 | 설명 |
|------|--------|------|
| 🔲 | inquire_member | 회원사 매매동향 |
| 🔲 | inquire_member_daily | 회원사 일별 매매 |
| 🔲 | short_sale | 공매도 현황 |
| 🔲 | daily_short_sale | 일별 공매도 |
| 🔲 | daily_loan_trans | 일별 대차거래 |
| 🔲 | lendable_by_company | 증권사별 대여가능 |
| 🔲 | traded_by_company | 증권사별 거래현황 |

---

## 7. 국내주식 기업정보/KSD (Domestic Stock — Corporate)

| 상태 | 함수명 | API Path | tr_id | 설명 |
|------|--------|----------|-------|------|
| 🔲 | ksdinfo_dividend | `/uapi/domestic-stock/v1/ksdinfo/dividend` | `HHKDB669102C0` | 배당정보 |
| 🔲 | dividend_rate | `/uapi/domestic-stock/v1/ranking/dividend-rate` | `HHKDB13470100` | 배당수익률 |
| 🔲 | ksdinfo_bonus_issue | — | — | 무상증자 |
| 🔲 | ksdinfo_cap_dcrs | — | — | 감자 |
| 🔲 | ksdinfo_forfeit | — | — | 실권 |
| 🔲 | ksdinfo_list_info | — | — | 상장정보 |
| 🔲 | ksdinfo_mand_deposit | — | — | 의무예탁 |
| 🔲 | ksdinfo_merger_split | — | — | 합병/분할 |
| 🔲 | ksdinfo_paidin_capin | — | — | 유상증자 |
| 🔲 | ksdinfo_pub_offer | — | — | 공모 |
| 🔲 | ksdinfo_purreq | — | — | 주식매수청구 |
| 🔲 | ksdinfo_rev_split | — | — | 액면분할/병합 |
| 🔲 | ksdinfo_sharehld_meet | — | — | 주주총회 |
| 🔲 | period_rights | — | — | 기간별 권리정보 |
| 🔲 | news_title | `/uapi/domestic-stock/v1/quotations/news-title` | `FHKST01011800` | 뉴스 제목 목록 |

---

## 8. 해외주식 시세 (Overseas Stock — Quotes)

| 상태 | 함수명 | API Path | tr_id | 설명 |
|------|--------|----------|-------|------|
| ✅ | price | `/uapi/overseas-price/v1/quotations/price` | `HHDFS00000300` | 현재가 |
| 🔲 | dailyprice | `/uapi/overseas-price/v1/quotations/dailyprice` | `HHDFS76240000` | 일별 시세 |
| 🔲 | asking_price | — | — | 호가 |
| 🔲 | inquire_asking_price | — | — | 호가 상세 |
| 🔲 | inquire_ccnl | — | — | 체결 내역 |
| ✅ | inquire_daily_chartprice | `/uapi/overseas-price/v1/quotations/inquire-daily-chartprice` | `FHKST03030100` | 일봉 차트 |
| 🔲 | inquire_time_itemchartprice | — | — | 분봉 차트 |
| 🔲 | inquire_time_indexchartprice | — | — | 해외지수 차트 |
| ✅ | inquire_search | `/uapi/overseas-price/v1/quotations/inquire-search` | `HHDFS76410000` | 종목 검색 |
| 🔲 | price_detail | — | — | 종목 상세 |
| 🔲 | price_fluct | — | — | 등락률 |
| 🔲 | delayed_asking_price_asia | — | — | 아시아 지연 호가 |
| 🔲 | delayed_ccnl | — | — | 지연 체결 |
| 🔲 | quot_inquire_ccnl | — | — | 체결 조회 |
| 🔲 | industry_price | — | — | 업종별 시세 |
| 🔲 | industry_theme | — | — | 테마별 시세 |
| 🔲 | brknews_title | — | — | 해외 뉴스 |
| 🔲 | market_cap | — | — | 시가총액 |
| 🔲 | countries_holiday | — | — | 해외 휴장일 |
| 🔲 | new_highlow | — | — | 신고가/신저가 |
| 🔲 | news_title | — | — | 해외 뉴스 제목 |
| 🔲 | search_info | — | — | 해외종목 정보 |

### 해외주식 랭킹

| 상태 | 함수명 | 설명 |
|------|--------|------|
| 🔲 | volume_rank | 해외 거래량 순위 |
| 🔲 | volume_surge | 거래량 급증 |
| 🔲 | volume_power | 체결강도 |
| 🔲 | updown_rate | 등락률 |
| 🔲 | trade_growth | 거래량 증가 |
| 🔲 | trade_pbmn | 거래대금별 |
| 🔲 | trade_turnover | 회전율 |

---

## 9. 해외주식 주문/잔고 (Overseas Stock — Trading)

| 상태 | 함수명 | API Path | tr_id (실전/모의) | 설명 |
|------|--------|----------|-------------------|------|
| ✅ | order (US buy) | `/uapi/overseas-stock/v1/trading/order` | `TTTT1002U` / `VTTT1002U` | 미국 매수 |
| ✅ | order (US sell) | 〃 | `TTTT1006U` / `VTTT1006U` | 미국 매도 |
| 🔲 | order (HK buy) | 〃 | `TTTS1002U` / `VTTS1002U` | 홍콩 매수 |
| 🔲 | order (HK sell) | 〃 | `TTTS1001U` / `VTTS1001U` | 홍콩 매도 |
| 🔲 | order (JP buy) | 〃 | `TTTS0308U` / `VTTS0308U` | 일본 매수 |
| 🔲 | order (JP sell) | 〃 | `TTTS0307U` / `VTTS0307U` | 일본 매도 |
| 🔲 | order (CN-SH buy) | 〃 | `TTTS0202U` / `VTTS0202U` | 중국상해 매수 |
| 🔲 | order (CN-SH sell) | 〃 | `TTTS1005U` / `VTTS1005U` | 중국상해 매도 |
| 🔲 | order (CN-SZ buy) | 〃 | `TTTS0305U` / `VTTS0305U` | 중국심천 매수 |
| 🔲 | order (CN-SZ sell) | 〃 | `TTTS0304U` / `VTTS0304U` | 중국심천 매도 |
| 🔲 | order (VN buy) | 〃 | `TTTS0311U` / `VTTS0311U` | 베트남 매수 |
| 🔲 | order (VN sell) | 〃 | `TTTS0310U` / `VTTS0310U` | 베트남 매도 |
| ✅ | order_rvsecncl | `/uapi/overseas-stock/v1/trading/order-rvsecncl` | `TTTT1004U` / `VTTT1004U` | 해외 주문 정정/취소 |
| 🔲 | daytime_order | — | — | 주간거래 주문 |
| 🔲 | daytime_order_rvsecncl | — | — | 주간거래 정정/취소 |
| 🔲 | order_resv | — | — | 해외 예약 주문 |
| 🔲 | order_resv_ccnl | — | — | 예약 주문 체결 |
| 🔲 | order_resv_list | — | — | 예약 주문 목록 |
| 🔲 | inquire_balance | `/uapi/overseas-stock/v1/trading/inquire-balance` | `TTTS3012R` / `VTTS3012R` | 해외 보유잔고 |
| ✅ | inquire_present_balance | `/uapi/overseas-stock/v1/trading/inquire-present-balance` | `CTRP6504R` | 해외 현재잔고 |
| ✅ | inquire_ccnl | `/uapi/overseas-stock/v1/trading/inquire-ccnl` | `TTTS3035R` / `VTTS3035R` | 해외 체결내역 |
| 🔲 | inquire_nccs | — | — | 해외 미체결 |
| 🔲 | inquire_period_profit | — | — | 해외 기간 수익률 |
| 🔲 | inquire_period_trans | — | — | 해외 기간 거래내역 |
| 🔲 | inquire_paymt_stdr_balance | — | — | 결제기준 잔고 |
| 🔲 | inquire_psamount | — | — | 해외 주문가능금액 |
| 🔲 | ccnl_notice | — | — | 체결 통보 |
| 🔲 | algo_ordno | — | — | 알고리즘 주문번호 |
| 🔲 | inquire_algo_ccnl | — | — | 알고리즘 체결 |
| 🔲 | foreign_margin | — | — | 외화 증거금 |
| 🔲 | colable_by_company | — | — | 대용가능금액 |
| 🔲 | rights_by_ice | — | — | 권리정보 |
| 🔲 | period_rights | — | — | 기간 권리정보 |

---

## 10. 국내채권 (Domestic Bonds)

| 상태 | 함수명 | 설명 |
|------|--------|------|
| 🔲 | inquire_price | 채권 현재가 |
| 🔲 | inquire_daily_price | 채권 일별 시세 |
| 🔲 | inquire_asking_price | 채권 호가 |
| 🔲 | inquire_ccnl | 채권 체결 |
| 🔲 | bond_asking_price | 채권 호가 (상세) |
| 🔲 | bond_ccnl | 채권 체결 (상세) |
| 🔲 | bond_index_ccnl | 채권지수 체결 |
| 🔲 | inquire_daily_itemchartprice | 채권 일봉 차트 |
| 🔲 | search_bond_info | 채권 종목 검색 |
| 🔲 | issue_info | 발행 정보 |
| 🔲 | avg_unit | 평균단가 |
| 🔲 | buy | 채권 매수 |
| 🔲 | sell | 채권 매도 |
| 🔲 | order_rvsecncl | 채권 정정/취소 |
| 🔲 | inquire_balance | 채권 잔고 |
| 🔲 | inquire_daily_ccld | 채권 체결내역 |
| 🔲 | inquire_psbl_order | 채권 주문가능액 |
| 🔲 | inquire_psbl_rvsecncl | 채권 미체결 |

---

## 11. 국내 선물/옵션 (Domestic Futures & Options)

| 상태 | 함수명 | 설명 |
|------|--------|------|
| 🔲 | inquire_price | 선물/옵션 현재가 |
| 🔲 | inquire_asking_price | 선물/옵션 호가 |
| 🔲 | inquire_daily_fuopchartprice | 일봉 차트 |
| 🔲 | inquire_time_fuopchartprice | 시간별 차트 |
| 🔲 | exp_price_trend | 예상가격 추이 |
| 🔲 | order | 선물/옵션 주문 |
| 🔲 | order_rvsecncl | 정정/취소 |
| 🔲 | inquire_psbl_order | 주문가능액 |
| 🔲 | inquire_psbl_ngt_order | 야간 주문가능 |
| 🔲 | inquire_balance | 잔고 |
| 🔲 | inquire_balance_settlement_pl | 결제손익 |
| 🔲 | inquire_balance_valuation_pl | 평가손익 |
| 🔲 | inquire_deposit | 예수금 |
| 🔲 | inquire_ngt_balance | 야간 잔고 |
| 🔲 | inquire_ccnl | 체결 조회 |
| 🔲 | inquire_ccnl_bstime | 시간별 체결 |
| 🔲 | inquire_ngt_ccnl | 야간 체결 |
| 🔲 | futures_exp_ccnl | 선물 예상 체결 |
| 🔲 | option_exp_ccnl | 옵션 예상 체결 |
| 🔲 | fuopt_ccnl_notice | 체결 통보 |
| 🔲 | inquire_daily_amount_fee | 일별 수수료 |
| 🔲 | ngt_margin_detail | 야간 증거금 |
| 🔲 | display_board_top | 종합 전광판 |
| 🔲 | display_board_futures | 선물 전광판 |
| 🔲 | display_board_callput | 콜/풋 전광판 |
| 🔲 | display_board_option_list | 옵션 목록 전광판 |

### 실시간 시세 (선물/옵션)

| 상태 | 함수명 | 설명 |
|------|--------|------|
| 🔲 | commodity_futures_realtime_quote | 상품선물 실시간 호가 |
| 🔲 | commodity_futures_realtime_conclusion | 상품선물 실시간 체결 |
| 🔲 | index_futures_realtime_quote | 지수선물 실시간 호가 |
| 🔲 | index_futures_realtime_conclusion | 지수선물 실시간 체결 |
| 🔲 | index_option_realtime_quote | 지수옵션 실시간 호가 |
| 🔲 | index_option_realtime_conclusion | 지수옵션 실시간 체결 |
| 🔲 | stock_futures_realtime_quote | 개별주식선물 실시간 호가 |
| 🔲 | stock_futures_realtime_conclusion | 개별주식선물 실시간 체결 |

### KRX 야간 거래

| 상태 | 함수명 | 설명 |
|------|--------|------|
| 🔲 | krx_ngt_futures_asking_price | 야간 선물 호가 |
| 🔲 | krx_ngt_futures_ccnl | 야간 선물 체결 |
| 🔲 | krx_ngt_futures_ccnl_notice | 야간 선물 체결 통보 |
| 🔲 | krx_ngt_option_asking_price | 야간 옵션 호가 |
| 🔲 | krx_ngt_option_ccnl | 야간 옵션 체결 |
| 🔲 | krx_ngt_option_exp_ccnl | 야간 옵션 예상 체결 |
| 🔲 | krx_ngt_option_notice | 야간 옵션 통보 |

---

## 12. 해외 선물/옵션 (Overseas Futures & Options)

| 상태 | 함수명 | 설명 |
|------|--------|------|
| 🔲 | asking_price | 해외선물 호가 |
| 🔲 | opt_asking_price | 해외옵션 호가 |
| 🔲 | inquire_price | 해외선물 현재가 |
| 🔲 | opt_price | 해외옵션 현재가 |
| 🔲 | inquire_time_futurechartprice | 선물 시간 차트 |
| 🔲 | inquire_time_optchartprice | 옵션 시간 차트 |
| 🔲 | search_contract_detail | 계약 상세 |
| 🔲 | search_opt_detail | 옵션 상세 |
| 🔲 | opt_detail | 옵션 정보 |
| 🔲 | stock_detail | 종목 정보 |
| 🔲 | market_time | 시장 시간 |
| 🔲 | ccnl / daily_ccnl / weekly_ccnl / monthly_ccnl / tick_ccnl | 체결 (기간별) |
| 🔲 | opt_daily_ccnl / opt_weekly_ccnl / opt_monthly_ccnl / opt_tick_ccnl | 옵션 체결 (기간별) |
| 🔲 | ccnl_notice | 체결 통보 |
| 🔲 | order | 해외선물 주문 |
| 🔲 | order_notice | 주문 통보 |
| 🔲 | order_rvsecncl | 정정/취소 |
| 🔲 | inquire_ccld / inquire_daily_ccld / inquire_period_ccld | 체결 내역 |
| 🔲 | inquire_unpd | 미체결 |
| 🔲 | inquire_deposit | 예수금 |
| 🔲 | inquire_psamount | 주문가능액 |
| 🔲 | margin_detail | 증거금 상세 |
| 🔲 | investor_unpd_trend | 투자자 미결제 추이 |
| 🔲 | inquire_daily_order | 일별 주문 |
| 🔲 | inquire_period_trans | 기간별 거래 |

---

## 13. ETF/ETN

| 상태 | 함수명 | 설명 |
|------|--------|------|
| 🔲 | inquire_price | ETF/ETN 현재가 |
| 🔲 | inquire_component_stock_price | 구성종목 시세 |
| 🔲 | etf_nav_trend | NAV 추이 |
| 🔲 | nav_comparison_trend | NAV 비교 추이 |
| 🔲 | nav_comparison_daily_trend | NAV 비교 일별 추이 |
| 🔲 | nav_comparison_time_trend | NAV 비교 시간 추이 |

---

## 14. ELW ⬜ 제외

| 상태 | 함수명 | 설명 |
|------|--------|------|
| ⬜ | compare_stocks | 종목 비교 |
| ⬜ | cond_search | 조건 검색 |
| ⬜ | elw_asking_price | ELW 호가 |
| ⬜ | elw_ccnl | ELW 체결 |
| ⬜ | elw_exp_ccnl | ELW 예상 체결 |
| ⬜ | expiration_stocks | 만기 종목 |
| ⬜ | indicator | 지표 |
| ⬜ | indicator_trend_ccnl / daily / minute | 지표 추이 |
| ⬜ | lp_trade_trend | LP 거래 추이 |
| ⬜ | newly_listed | 신규 상장 |
| ⬜ | quick_change | 급변 |
| ⬜ | sensitivity / sensitivity_trend_* | 민감도 / 추이 |
| ⬜ | udrl_asset_list / udrl_asset_price | 기초자산 목록/시세 |
| ⬜ | updown_rate | 등락률 |
| ⬜ | volatility_trend_ccnl / daily / minute / tick | 변동성 추이 |
| ⬜ | volume_rank | 거래량 순위 |

---

## 15. WebSocket 실시간

| 상태 | 함수명 | 설명 |
|------|--------|------|
| 🔲 | 국내주식 실시간 체결 | H0STCNT0 — 실시간 체결가 |
| 🔲 | 국내주식 실시간 호가 | H0STASP0 — 실시간 호가 |
| 🔲 | 국내주식 실시간 체결통보 | H0STCNI0 / H0STCNI9 — 주문 체결 통보 |
| 🔲 | 해외주식 실시간 체결 | HDFSCNT0 — 해외 실시간 체결 |
| 🔲 | 해외주식 실시간 호가 | HDFSASP0 — 해외 실시간 호가 |
| 🔲 | 해외주식 실시간 체결통보 | H0GSCNI0 — 해외 체결 통보 |

---

## 구현 현황 요약

| 카테고리 | ✅ 완료 | 🔲 예정 | ⬜ 제외 | 합계 |
|----------|---------|---------|---------|------|
| 인증 | 2 | 1 | 0 | 3 |
| 국내주식 시세 | 6 | ~35 | ~4 (NXT) | ~45 |
| 국내주식 주문/잔고 | 8 | ~13 | 5 (연금) | ~26 |
| 국내주식 랭킹 | 5 | 13 | 0 | 18 |
| 국내주식 재무 | 0 | 10 | 0 | 10 |
| 국내주식 투자자/프로그램 | 2 | ~23 | ~2 (NXT) | ~27 |
| 국내주식 기업/KSD | 0 | 15 | 0 | 15 |
| 해외주식 시세 | 3 | ~26 | 0 | ~29 |
| 해외주식 주문/잔고 | 5 | ~27 | 0 | ~32 |
| 국내채권 | 0 | 18 | 0 | 18 |
| 국내선물옵션 | 0 | 43 | 0 | 43 |
| 해외선물옵션 | 0 | 35 | 0 | 35 |
| ETF/ETN | 0 | 6 | 0 | 6 |
| ELW | 0 | 0 | 24 | 24 |
| WebSocket | 0 | 6 | 0 | 6 |
| **합계** | **31** | **~271** | **~35** | **~337** |

---

## Phase별 구현 로드맵

### Phase 1~4 ✅ 완료
- 인증, 국내 시세/차트, 포트폴리오, 국내 매매, 잔고

### Phase 5 (랭킹/시장정보) ✅ 완료
- 국내 랭킹 (거래량/등락률/시총/인기/신고가신저가)
- 투자자 매매동향 (종목별/외국인기관)

### Phase 6 (해외주식) ✅ 거의 완료
- 해외 종목 검색 (마스터 파일 기반)
- 해외 시세/차트/주문 (미국 NASDAQ/NYSE/AMEX)
- 해외 체결내역, 정정/취소

### Phase 7 (종목 분석 — 재무/기업/뉴스)
- 재무제표 (손익/재무상태표/재무비율/성장/수익/안정성)
- 실적추정치, 투자의견/컨센서스
- 배당정보, 배당수익률
- 뉴스 (국내+해외)
- 기업정보 KSD (증자/감자/합병/분할/주총/공모/실권/액면분할)
- 종목 기본정보, 상세정보 검색
- ETF/ETN 전용 (NAV, 구성종목, 비교추이)

### Phase 8 (시장 분석 — 투자자/프로그램/공매도/랭킹 확장)
- 투자자 매매동향 상세 (시장별 일별/시간별, 종목별 일별)
- 외국인 매수추이/거래추정/거래추이
- 증권사별 투자의견
- 프로그램 매매 (KRX/통합/종목별/일별/당일/지수)
- 회원사 매매동향 (당일/일별)
- 공매도 (현황/일별), 대차거래, 증권사별 대여/거래
- 국내 랭킹 확장 (이격도/체결강도/시간외/매수비율/우선주괴리/수익자산/거래대금/대량체결)
- 해외 랭킹 (거래량/급증/체결강도/등락률/증가/거래대금/회전율)
- 해외 시세 확장 (상세/등락률/업종/테마/시총/신고가신저가/뉴스)
- 예상체결/장전 시세 (KRX/통합/예상종가/지수추이/가격추이/등락)
- 관심종목 그룹/복수시세
- 조건검색 (제목/결과)
- 지수 상세 (업종별/일별/틱/시간별/일봉차트/시간차트)

### Phase 9 (거래 확장 — 신용/예약/해외 다국가)
- 국내 신용 주문/잔고/증권사별/일별/가능금액
- 국내 예약 주문/체결/정정취소
- 해외 주문 다국가 (홍콩/일본/중국상해/중국심천/베트남)
- 해외 주간거래 주문/정정취소
- 해외 예약 주문/체결/목록
- 해외 추가 잔고 (보유/결제기준/주문가능금액/외화증거금/대용가능/권리정보)
- 해외 미체결, 기간 거래내역
- 해외 알고리즘 주문/체결
- 국내 추가 잔고 (시간외/시세/통합증거금/실현손익/기간별수익률)
- 국내 매도가능수량

### Phase 10 (채권 거래)
- 채권 시세/호가/체결/차트
- 채권 검색/발행정보/평균단가
- 채권 매수/매도/정정취소
- 채권 잔고/체결내역/주문가능액/미체결
- 채권지수 체결

### Phase 11 (국내 선물/옵션)
- 선물/옵션 시세/호가/차트
- 주문/정정취소/주문가능액
- 잔고/결제손익/평가손익/예수금
- 체결 (일반/시간별/야간)
- 예상체결 (선물/옵션)
- 전광판 (종합/선물/콜풋/옵션목록)
- 야간 거래 (호가/체결/통보 — 선물+옵션)
- 실시간 시세 WebSocket (상품선물/지수선물/지수옵션/개별주식선물)
- 야간 주문가능/잔고/증거금
- 일별 수수료

### Phase 12 (해외 선물/옵션)
- 해외선물/옵션 시세/호가/차트
- 종목검색/계약상세/옵션상세
- 주문/정정취소/통보
- 체결 (일/주/월/틱)
- 잔고/미체결/예수금/주문가능액/증거금
- 투자자 미결제 추이
- 일별 주문/기간별 거래
- 시장 시간

### Phase 13 (UI 다듬기 + WebSocket 실시간)
- 대시보드 랭킹 카드 UI
- 호가창 개선, 보조지표 (이평선/RSI/MACD)
- WebSocket 실시간 체결/호가 (국내+해외 6종)
- 장 상태/시간, 휴장일 (국내+해외)
- 시간외 시세 (현재가/일별/호가)
- 모바일 반응형

### Phase 14 (AI) — 최후반
- AI 어시스턴트 (Claude/OpenAI)
- AI 자동매매

### ⬜ 제외 (구현 안 함)
- NXT 별도 API (asking_price_nxt, ccnl_nxt, exp_ccnl_nxt, market_status_nxt, program_trade_nxt) — 통합 API로 충분
- 연금 계좌 (pension_*) — 별도 계좌 체계
- ELW 전체 — 거래량 극소
