from pycoingecko import CoinGeckoAPI
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
import numpy as np

cg = CoinGeckoAPI()

def get_price_history(coin_id, vs_currency='usd', days=200):
    data = cg.get_coin_market_chart_by_id(id=coin_id, vs_currency=vs_currency, days=days)
    prices = data['prices']
    df = pd.DataFrame(prices, columns=['timestamp','price'])
    df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('date', inplace=True)
    df = df[['price']]
    return df

# 取得過去 200 天價格
op = get_price_history("optimism", days=200)
matic = get_price_history("matic-network", days=200)

# 合併價格
data = pd.concat([
    op.rename(columns={'price':'OP-USD'}),
    matic.rename(columns={'price':'MATIC-USD'})
], axis=1).dropna()

# 每日報酬
daily_returns = data.pct_change().dropna()

# 計算相關性
overall_corr = daily_returns.corr().iloc[0,1]
print(f"Overall daily returns correlation (OP & MATIC): {overall_corr:.4f}")

# OLS 回歸
Y = data["OP-USD"]
X = sm.add_constant(data["MATIC-USD"])
model = sm.OLS(Y, X).fit()
alpha, beta = model.params.const, model.params["MATIC-USD"]

# 計算 spread 與 z-score
spread = Y - (alpha + beta * data["MATIC-USD"])
rolling_window = 30
spread_mean = spread.rolling(window=rolling_window).mean()
spread_std = spread.rolling(window=rolling_window).std()
zscore = (spread - spread_mean) / spread_std

# 設定交易閾值
z_open = 1.0
z_close = 0.5

# 建立倉位
positions = pd.DataFrame(index=data.index, columns=data.columns).fillna(0)
positions.loc[zscore < -z_open, "OP-USD"] = 1
positions.loc[zscore < -z_open, "MATIC-USD"] = -1
positions.loc[zscore > z_open, "OP-USD"] = -1
positions.loc[zscore > z_open, "MATIC-USD"] = 1
positions.loc[abs(zscore) < z_close, :] = 0

# 手續費與滑點
commission = 0.001
slippage = 0.0005
trade_size = positions.diff().abs()
cost = (trade_size * data).sum(axis=1) * (commission + slippage)

# 計算策略收益
strategy_returns = (positions.shift(1) * daily_returns).sum(axis=1) - cost
cum_ret = (1 + strategy_returns).cumprod()

# 計算夏普比率
sharpe_ratio = strategy_returns.mean() / strategy_returns.std() * np.sqrt(252)

# 計算最大回撤
rolling_max = cum_ret.cummax()
drawdown = (cum_ret - rolling_max) / rolling_max
max_drawdown = drawdown.min()

# 統計交易
total_trades = ((positions.diff().abs()).sum(axis=1) > 0).sum()
avg_holding_days = len(data)/total_trades if total_trades>0 else 0

print("\n=== 📊 OP/MATIC Pairs Trading Performance ===")
print(f"Final cumulative return: {cum_ret.iloc[-1]:.4f}")
print(f"Total trades: {total_trades}")
print(f"Average holding days per trade: {avg_holding_days:.2f}")
print(f"OLS alpha: {alpha:.4f}, beta: {beta:.4f}")
print(f"p-value alpha: {model.pvalues['const']:.2e}")
print(f"p-value beta: {model.pvalues['MATIC-USD']:.2e}")
print(f"Annualized Sharpe Ratio: {sharpe_ratio:.4f}")
print(f"Maximum Drawdown: {max_drawdown:.2%}")

# 繪製累積收益與 z-score
plt.figure(figsize=(12,6))
plt.plot(cum_ret, label="Cumulative Return")
plt.title("OP/MATIC Pairs Trading Cumulative Return")
plt.xlabel("Date")
plt.ylabel("Cumulative Return")
plt.legend()
plt.grid(True)
plt.show()

plt.figure(figsize=(12,6))
plt.plot(zscore, label="Z-Score of Spread")
plt.axhline(z_open, color='red', linestyle='--', label="Open Threshold")
plt.axhline(-z_open, color='red', linestyle='--')
plt.axhline(z_close, color='green', linestyle='--', label="Close Threshold")
plt.axhline(-z_close, color='green', linestyle='--')
plt.title("Z-Score of OP/MATIC Spread")
plt.xlabel("Date")
plt.ylabel("Z-Score")
plt.legend()
plt.grid(True)
plt.show()
