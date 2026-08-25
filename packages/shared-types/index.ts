/**
 * Market AI — Shared TypeScript Domain Types
 */

export type Exchange = 'NSE' | 'BSE' | 'MCX';

export type InstrumentType = 'EQUITY' | 'INDEX' | 'FUTURES' | 'OPTIONS';

export type MarketSessionStatus = 
  | 'CLOSED' 
  | 'PRE_OPEN' 
  | 'OPEN' 
  | 'SPECIAL_SESSION' 
  | 'POST_CLOSE' 
  | 'HOLIDAY' 
  | 'WEEKEND';

export type MarketRegime = 
  | 'BULL' 
  | 'BEAR' 
  | 'RANGE' 
  | 'HIGH_VOLATILITY' 
  | 'LOW_VOLATILITY' 
  | 'RISK_ON' 
  | 'RISK_OFF' 
  | 'TRANSITION';

export interface SymbolInfo {
  exchange: Exchange;
  symbol: string;
  isin?: string;
  company_name: string;
  instrument_type: InstrumentType;
  series: string;
  sector?: string;
  industry?: string;
  lot_size: number;
  tick_size: number;
  active: boolean;
}

export interface Candle {
  timestamp: string; // ISO 8601
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  open_interest?: number;
  turnover?: number;
}

export interface Quote {
  symbol: string;
  exchange: Exchange;
  company_name?: string;
  last_price: number;
  change: number;
  percent_change: number;
  open: number;
  high: number;
  low: number;
  previous_close: number;
  volume: number;
  value?: number;
  vwap?: number;
  high_52w?: number;
  low_52w?: number;
  timestamp: string;
  provider: string;
}

export interface IndexQuote {
  symbol: string;
  name: string;
  current_value: number;
  change: number;
  percent_change: number;
  open: number;
  high: number;
  low: number;
  previous_close: number;
  advances?: number;
  declines?: number;
  timestamp: string;
}

export interface MarketBreadth {
  advances: number;
  declines: number;
  unchanged: number;
  advance_decline_ratio: number;
  highs_52w: number;
  lows_52w: number;
  upper_circuits: number;
  lower_circuits: number;
  total_traded_stocks: number;
  timestamp: string;
}

export interface FiiDiiActivity {
  date: string;
  fii_buy_gross: number; // in INR Crores
  fii_sell_gross: number;
  fii_net: number;
  dii_buy_gross: number;
  dii_sell_gross: number;
  dii_net: number;
  total_institutional_net: number;
  timestamp: string;
}

export interface SectorPerformance {
  sector_name: string;
  symbol: string;
  current_value: number;
  percent_change: number;
  change: number;
  top_contributor?: string;
  weight_pct?: number;
}

export interface MarketRegimeState {
  regime: MarketRegime;
  probability: number;
  confidence: number;
  drivers: string[];
  risks: string[];
  updated_at: string;
}

export interface MarketStatusResponse {
  status: MarketSessionStatus;
  is_open: boolean;
  ist_time: string;
  session_name: string;
  current_date: string;
  next_open?: string;
  next_close?: string;
  holiday_name?: string;
  trading_day: boolean;
}

export interface LiveTickerMessage {
  event_type: 'TICK' | 'HEARTBEAT' | 'STATUS_CHANGE';
  symbol: string;
  price: number;
  change: number;
  percent_change: number;
  volume: number;
  timestamp: string;
}
