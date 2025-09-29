from pycoingecko import CoinGeckoAPI
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
import numpy as np

cg = CoinGeckoAPI()

def get_price_history(coin_id, vs_currency='usd', days=200):
    """
    抓取過去 days 天的歷史價格 (日線)
    """
    data = cg.get_coin_market_chart_by_id(id=coin_id, vs_currency=vs_currency, days=days)
    prices = data['prices']
    df = pd.DataFrame(prices, columns=['timestamp','price'])
    df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('date', inplace=True)
    df = df[['price']]
    return df

# 抓過去 200 天價格
op = get_price_history("optimism", days=200)
arb = get_price_history("arbitrum", days=200)

# 合併價格資料
data = pd.concat([op.rename(columns={'price':'OP-USD'}),
                  arb.rename(columns={'price':'ARB-USD'})], axis=1).dropna()

# 計算每日報酬率
daily_returns = data.pct_change().dropna()

# 整體日報酬相關性
overall_corr = daily_returns.corr().iloc[0,1]
print(f"Overall daily returns correlation (OP & ARB): {overall_corr:.4f}")

# 滾動相關性（30天視窗）
rolling_corr = daily_returns['OP-USD'].rolling(window=30).corr(daily_returns['ARB-USD'])

# 繪圖
import matplotlib.pyplot as plt

plt.figure(figsize=(12,6))
plt.plot(rolling_corr, label="30-day Rolling Correlation")
plt.axhline(overall_corr, color='red', linestyle='--', label=f"Overall Correlation: {overall_corr:.2f}")
plt.title("OP & ARB Rolling Correlation (30-day)")
plt.xlabel("Date")
plt.ylabel("Correlation")
plt.legend()
plt.grid(True)
plt.show()
