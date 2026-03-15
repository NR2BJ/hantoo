export interface StockQuote {
  symbol: string;
  name: string;
  current_price: number;
  change: number;
  change_rate: number;
  change_sign: string; // 1=상한, 2=상승, 3=보합, 4=하한, 5=하락
  open_price: number;
  high_price: number;
  low_price: number;
  volume: number;
  trade_amount: number;
  prev_close: number;
  market_cap: number;
  per: number | null;
  pbr: number | null;
  eps: number | null;
}

export interface Candle {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface OrderbookEntry {
  price: number;
  volume: number;
}

export interface Orderbook {
  symbol: string;
  ask: OrderbookEntry[];
  bid: OrderbookEntry[];
  total_ask_volume: number;
  total_bid_volume: number;
}

export interface TradeRecord {
  time: string;
  price: number;
  volume: number;
  change: number;
}

export interface IndexQuote {
  code: string;
  name: string;
  current: number;
  change: number;
  change_rate: number;
  change_sign: string;
}

export interface SearchResult {
  symbol: string;
  name: string;
  market: string;
}

export interface WatchlistItem {
  id: string;
  symbol: string;
  market: string;
  added_at: string;
  quote: StockQuote | null;
}

export interface Watchlist {
  id: string;
  name: string;
  created_at: string;
  items: WatchlistItem[];
}

// ── Order Types ──

export interface OrderCreate {
  symbol: string;
  side: "buy" | "sell";
  order_type: "limit" | "market";
  quantity: number;
  price?: number;
}

export interface OrderModify {
  quantity: number;
  price: number;
}

export interface OrderResponse {
  id: string;
  account_id: string;
  symbol: string;
  side: string;
  order_type: string;
  quantity: number;
  price: number | null;
  status: string;
  filled_quantity: number;
  filled_price: number | null;
  kis_order_id: string | null;
  submitted_at: string | null;
  created_at: string;
}

export interface PendingOrder {
  order_id: string;
  symbol: string;
  name: string;
  side: string;
  order_type: string;
  quantity: number;
  price: number;
  unfilled_qty: number;
  order_time: string;
}

export interface FilledOrder {
  order_id: string;
  symbol: string;
  name: string;
  side: string;
  quantity: number;
  price: number;
  total_amount: number;
  order_time: string;
  filled_time: string;
}

export interface BuyableAmount {
  orderable_cash: number;
  orderable_qty: number;
}

// ── Portfolio Types ──

export interface ForeignCurrencyBalance {
  currency: string;
  deposit: number;
  stock_value: number;
  total_value: number;
  exchange_rate: number;
}

export interface AccountBalance {
  total_value: number;
  cash: number;
  stock_value: number;
  total_pnl: number;
  total_pnl_rate: number;
  holding_count: number;
  foreign_balances: ForeignCurrencyBalance[];
  overseas_total_krw: number;
}

export interface Holding {
  symbol: string;
  name: string;
  quantity: number;
  avg_price: number;
  current_price: number;
  value: number;
  pnl: number;
  pnl_rate: number;
}

export interface OverseasHolding {
  symbol: string;
  name: string;
  market: string;
  currency: string;
  quantity: number;
  avg_price: number;
  current_price: number;
  value_foreign: number;
  pnl_foreign: number;
  pnl_rate: number;
  exchange_rate: number;
}

// ── Ranking Types ──

export interface RankItem {
  rank: number;
  symbol: string;
  name: string;
  current_price: number;
  change: number;
  change_rate: number;
  change_sign: string; // 1=상한 2=상승 3=보합 4=하한 5=하락
  volume: number;
  trade_amount: number;
}

export interface InvestorItem {
  investor: string;
  buy_volume: number;
  sell_volume: number;
  net_volume: number;
  buy_amount: number;
  sell_amount: number;
  net_amount: number;
}

// Color helpers for Korean market convention
export function getPriceColor(changeSign: string): string {
  // 1=상한, 2=상승 → red, 4=하한, 5=하락 → blue, 3=보합 → gray
  if (changeSign === "1" || changeSign === "2") return "text-red-500";
  if (changeSign === "4" || changeSign === "5") return "text-blue-500";
  return "text-gray-500";
}

export function getPriceSign(change: number): string {
  if (change > 0) return "+";
  return "";
}
