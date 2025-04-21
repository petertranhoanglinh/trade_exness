import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class BitcoinIchimokuMT5:
    def __init__(self, symbol='BTCUSDm', timeframe=mt5.TIMEFRAME_M5, lookback_period=200):
        self.symbol = symbol
        self.timeframe = timeframe
        self.lookback_period = lookback_period
        self.data = self.get_data()

    def get_data(self):
        if not mt5.initialize():
            raise Exception("❌ Không thể kết nối với MetaTrader 5")
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            mt5.shutdown()
            raise Exception(f"❌ Symbol '{self.symbol}' không tồn tại trong MT5. Hãy kiểm tra lại tên.")

        if not symbol_info.visible:
            mt5.symbol_select(self.symbol, True)
        rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, self.lookback_period)
        mt5.shutdown()
        if rates is None or len(rates) == 0:
            raise Exception("❌ Không lấy được dữ liệu từ MT5. Có thể server bị lỗi hoặc không có dữ liệu.")
        df = pd.DataFrame(rates)
        if 'time' not in df.columns:
            raise Exception(f"❌ Dữ liệu không chứa cột 'time'. Các cột có sẵn: {df.columns.tolist()}")

        df['time'] = pd.to_datetime(df['time'], unit='s')  
        df.set_index('time', inplace=True)
        df = df[['open', 'high', 'low', 'close']].astype(float)
        return df

    def calculate_ichimoku(self):
        df = self.data.copy()
        df['tenkan_sen'] = (df['high'].rolling(window=9).max() + df['low'].rolling(window=9).min()) / 2
        df['kijun_sen'] = (df['high'].rolling(window=26).max() + df['low'].rolling(window=26).min()) / 2
        df['senkou_span_a'] = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(26)
        df['senkou_span_b'] = (df['high'].rolling(window=52).max() + df['low'].rolling(window=52).min()) / 2
        df['senkou_span_b'] = df['senkou_span_b'].shift(26)
        df['chikou_span'] = df['close'].shift(-26)
        return df

    def check_trend(self):
        df = self.calculate_ichimoku()
        latest = df.iloc[-1]
        if latest['close'] > latest['senkou_span_a'] and latest['close'] > latest['senkou_span_b']:
            trend = "Bullish"
        elif latest['close'] < latest['senkou_span_a'] and latest['close'] < latest['senkou_span_b']:
            trend = "Bearish"
        else:
            trend = "Neutral"
        if latest['tenkan_sen'] > latest['kijun_sen']:
            trend_reversal = "Possible Bullish Reversal"
        elif latest['tenkan_sen'] < latest['kijun_sen']:
            trend_reversal = "Possible Bearish Reversal"
        else:
            trend_reversal = "No Reversal"

        return trend, trend_reversal

    def plot_ichimoku(self):
        df = self.calculate_ichimoku()

        plt.figure(figsize=(12, 6))
        plt.plot(df.index, df['close'], label='Close Price', color='black', linewidth=1)

        plt.fill_between(df.index, df['senkou_span_a'], df['senkou_span_b'],
                         where=(df['senkou_span_a'] > df['senkou_span_b']),
                         facecolor='green', alpha=0.5, label='Bullish Cloud')
        plt.fill_between(df.index, df['senkou_span_a'], df['senkou_span_b'],
                         where=(df['senkou_span_a'] < df['senkou_span_b']),
                         facecolor='red', alpha=0.5, label='Bearish Cloud')

        plt.plot(df.index, df['tenkan_sen'], label='Tenkan-sen (Conversion Line)', color='blue')
        plt.plot(df.index, df['kijun_sen'], label='Kijun-sen (Base Line)', color='orange')
        plt.plot(df.index, df['chikou_span'], label='Chikou Span (Lagging Span)', color='purple')

        plt.title(f'Ichimoku Cloud for {self.symbol}')
        plt.legend(loc='best')
        plt.grid(True)
        plt.tight_layout()
        plt.show()
if __name__ == "__main__":
    try:
        bitcoin = BitcoinIchimokuMT5()
        trend, trend_reversal = bitcoin.check_trend()
        print(f"📈 Current trend: {trend}")
        print(f"🔁 Trend reversal status: {trend_reversal}")
        bitcoin.plot_ichimoku()
    except Exception as e:
        print(f"🚨 Lỗi: {e}")
