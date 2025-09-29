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

# 合併成一個 DataFrame
data = pd.concat([op.rename(columns={'price':'OP-USD'}),
                  arb.rename(columns={'price':'ARB-USD'})], axis=1).dropna()

# 計算每日報酬
daily_returns = data.pct_change().dropna()

# 計算日報酬相關性
correlation = daily_returns.corr().iloc[0,1]
print(f"OP & ARB daily returns correlation: {correlation:.4f}")

# OLS 回歸
Y = data["OP-USD"]
X = sm.add_constant(data["ARB-USD"])
model = sm.OLS(Y, X).fit()
alpha, beta = model.params.const, model.params["ARB-USD"]

# 計算 spread 與 z-score
spread = Y - (alpha + beta * data["ARB-USD"])
rolling_window = 30
spread_mean = spread.rolling(window=rolling_window).mean()
spread_std = spread.rolling(window=rolling_window).std()
zscore = (spread - spread_mean) / spread_std

# 動態調整 z-score 閾值（根據標準差波動）
z_open = 1.1  # 開倉閾值
z_close = 0.55  # 平倉閾值

# 交易策略
positions = pd.DataFrame(index=data.index, columns=data.columns).fillna(0)
long_cond  = zscore < -z_open
short_cond = zscore > z_open
close_cond = abs(zscore) < z_close

positions.loc[long_cond, "OP-USD"]  =  1
positions.loc[long_cond, "ARB-USD"] = -1
positions.loc[short_cond, "OP-USD"]  = -1
positions.loc[short_cond, "ARB-USD"] =  1
positions.loc[close_cond, :] = 0

# 設定止損閾值，例如 spread 超過 ±5% 的價格就止損
stop_loss_threshold = 0.15  # 可自行調整

# 計算止損條件
stop_loss_cond = (spread / Y).abs() > stop_loss_threshold

# 將止損條件平倉
positions.loc[stop_loss_cond, :] = 0


# 設定手續費與滑點
commission = 0.001  # 0.1%
slippage = 0.0005   # 0.05%

# 計算每日交易量變化（開平倉才計算手續費）
trade_size = positions.diff().abs()  

# 計算每日手續費+滑點成本
cost = (trade_size * data).sum(axis=1) * (commission + slippage)

# 回測策略收益（扣掉手續費與滑點）
strategy_returns = (positions.shift(1) * daily_returns).sum(axis=1) - cost

# 累積收益
cum_ret = (1 + strategy_returns).cumprod()

# 計算夏普比率
sharpe_ratio = strategy_returns.mean() / strategy_returns.std() * np.sqrt(252)

# 計算策略統計數據
total_trades = ((positions.diff().abs()).sum(axis=1) > 0).sum()
avg_holding_days = len(data)/total_trades if total_trades > 0 else 0

# 計算最大回撤
rolling_max = cum_ret.cummax()  # 累積收益的歷史最高點
drawdown = (cum_ret - rolling_max) / rolling_max  # 回撤
max_drawdown = drawdown.min()  # 最大回撤（最負值）

print("\n=== 📊 Pairs Trading Performance ===")
print(f"Final cumulative return: {cum_ret.iloc[-1]:.4f}")
print(f"Total trades: {total_trades}")
print(f"Average holding days per trade: {avg_holding_days:.2f}")
print(f"OLS alpha: {alpha:.4f}, beta: {beta:.4f}")
print(f"p-value for alpha: {model.pvalues['const']:.2e}")
print(f"p-value for beta : {model.pvalues['ARB-USD']:.2e}")
print(f"Annualized Sharpe Ratio: {sharpe_ratio:.4f}")
print(f"Maximum Drawdown: {max_drawdown:.2%}")

# 繪圖
plt.figure(figsize=(12,6))
plt.plot(cum_ret, label="Pairs Trading Strategy")
plt.title("Pairs Trading Strategy Cumulative Return")
plt.xlabel("Date")
plt.ylabel("Cumulative Return")
plt.legend()
plt.grid(True)
plt.show()

# 找出進場和平倉點
long_entries  = zscore < -z_open
short_entries = zscore > z_open
exits = abs(zscore) < z_close

plt.figure(figsize=(14,8))

# 1️⃣ 繪 spread 與 z-score
plt.subplot(2,1,1)
plt.plot(spread, label='Spread', color='blue')
plt.plot(spread_mean, label='Rolling Mean', color='orange')
plt.fill_between(spread.index, spread_mean + spread_std, spread_mean - spread_std, color='gray', alpha=0.2, label='±1 Std')
plt.scatter(spread.index[long_entries], spread[long_entries], marker='^', color='green', label='Long Entry', s=80)
plt.scatter(spread.index[short_entries], spread[short_entries], marker='v', color='red', label='Short Entry', s=80)
plt.scatter(spread.index[exits], spread[exits], marker='o', color='black', label='Exit', s=50)
plt.title("Spread & z-score with Trade Signals")
plt.xlabel("Date")
plt.ylabel("Spread")
plt.legend()
plt.grid(True)

# 2️⃣ 繪累積收益
plt.subplot(2,1,2)
plt.plot(cum_ret, label="Cumulative Return", color='purple')
plt.fill_between(drawdown.index, cum_ret, cum_ret.cummax(), color='red', alpha=0.2, label="Drawdown")
plt.title("Pairs Trading Strategy Cumulative Return & Drawdown")
plt.xlabel("Date")
plt.ylabel("Cumulative Return")
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()

plt.figure(figsize=(14,5))

# 繪 z-score
plt.plot(zscore, label='z-score', color='blue')
plt.axhline(z_open, color='red', linestyle='--', label='Upper Threshold')
plt.axhline(-z_open, color='green', linestyle='--', label='Lower Threshold')
plt.axhline(z_close, color='orange', linestyle=':', label='Close Threshold')
plt.axhline(-z_close, color='orange', linestyle=':', label='_nolegend_')

# 標記交易訊號
plt.scatter(zscore.index[long_entries], zscore[long_entries], marker='^', color='green', label='Long Entry', s=80)
plt.scatter(zscore.index[short_entries], zscore[short_entries], marker='v', color='red', label='Short Entry', s=80)
plt.scatter(zscore.index[exits], zscore[exits], marker='o', color='black', label='Exit', s=50)

plt.title("z-score with Trading Signals")
plt.xlabel("Date")
plt.ylabel("z-score")
plt.legend()
plt.grid(True)
plt.show()

plt.figure(figsize=(10,5))
plt.hist(strategy_returns, bins=30, edgecolor='k', alpha=0.6)
plt.title("Strategy P&L Distribution")
plt.xlabel("Daily Return")
plt.ylabel("Frequency")
plt.grid(True)
plt.show()
