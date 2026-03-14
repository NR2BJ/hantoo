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
