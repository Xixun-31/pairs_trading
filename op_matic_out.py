# 修改重點：把 ARB-USD -> MATIC-USD
from pycoingecko import CoinGeckoAPI
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

cg = CoinGeckoAPI()

def get_price_history_range(coin_id, start_days_ago, end_days_ago, vs_currency='usd'):
    end_date = datetime.today() - timedelta(days=end_days_ago)
    start_date = datetime.today() - timedelta(days=start_days_ago)
    data = cg.get_coin_market_chart_range_by_id(
        id=coin_id, 
        vs_currency=vs_currency, 
        from_timestamp=int(start_date.timestamp()), 
        to_timestamp=int(end_date.timestamp())
    )
    prices = data['prices']
    df = pd.DataFrame(prices, columns=['timestamp','price'])
    df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('date', inplace=True)
    df = df[['price']]
    return df

# 取得樣本內資料：前 365 天到前 200 天
op_train = get_price_history_range("optimism", start_days_ago=365, end_days_ago=200)
matic_train = get_price_history_range("matic-network", start_days_ago=365, end_days_ago=200)

# 合併成樣本內 DataFrame
data = pd.concat([
    op_train.rename(columns={'price':'OP-USD'}),
    matic_train.rename(columns={'price':'MATIC-USD'})
], axis=1).dropna()

# 計算每日報酬
daily_returns = data.pct_change().dropna()

# 計算日報酬相關性
correlation = daily_returns.corr().iloc[0,1]
print(f"OP & MATIC daily returns correlation: {correlation:.4f}")

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

# 動態調整 z-score 閾值
z_open = 1.1
z_close = 0.55

# 交易策略
positions = pd.DataFrame(index=data.index, columns=data.columns).fillna(0)
long_cond  = zscore < -z_open
short_cond = zscore > z_open
close_cond = abs(zscore) < z_close

positions.loc[long_cond, "OP-USD"]  =  1
positions.loc[long_cond, "MATIC-USD"] = -1
positions.loc[short_cond, "OP-USD"]  = -1
positions.loc[short_cond, "MATIC-USD"] =  1
positions.loc[close_cond, :] = 0

# 手續費與滑點
commission = 0.001
slippage = 0.0005
trade_size = positions.diff().abs()
cost = (trade_size * data).sum(axis=1) * (commission + slippage)

# 回測策略收益
strategy_returns = (positions.shift(1) * daily_returns).sum(axis=1) - cost
cum_ret = (1 + strategy_returns).cumprod()

# 夏普比率
sharpe_ratio = strategy_returns.mean() / strategy_returns.std() * np.sqrt(252)

# 最大回撤
rolling_max = cum_ret.cummax()
drawdown = (cum_ret - rolling_max) / rolling_max
max_drawdown = drawdown.min()

# 交易統計
total_trades = ((positions.diff().abs()).sum(axis=1) > 0).sum()
avg_holding_days = len(data)/total_trades if total_trades>0 else 0

print("\n=== 📊 OP/MATIC Pairs Trading Performance ===")
print(f"Final cumulative return: {cum_ret.iloc[-1]:.4f}")
print(f"Total trades: {total_trades}")
print(f"Average holding days per trade: {avg_holding_days:.2f}")
print(f"OLS alpha: {alpha:.4f}, beta: {beta:.4f}")
print(f"p-value for alpha: {model.pvalues['const']:.2e}")
print(f"p-value for beta : {model.pvalues['MATIC-USD']:.2e}")
print(f"Annualized Sharpe Ratio: {sharpe_ratio:.4f}")
print(f"Maximum Drawdown: {max_drawdown:.2%}")

# 繪圖累積收益與 z-score
plt.figure(figsize=(12,6))
plt.plot(cum_ret, label="Pairs Trading Strategy")
plt.title("OP/MATIC Pairs Trading Strategy Cumulative Return")
plt.xlabel("Date")
plt.ylabel("Cumulative Return")
plt.legend()
plt.grid(True)
plt.show()

plt.figure(figsize=(10,5))
plt.plot(zscore, label='z-score')
plt.axhline(z_open, color='red', linestyle='--', label='Upper Threshold')
plt.axhline(-z_open, color='green', linestyle='--', label='Lower Threshold')
plt.axhline(z_close, color='orange', linestyle=':', label='Close Threshold')
plt.axhline(-z_close, color='orange', linestyle=':', label='_nolegend_')
plt.scatter(zscore.index[long_cond], zscore[long_cond], marker='^', color='green', s=80)
plt.scatter(zscore.index[short_cond], zscore[short_cond], marker='v', color='red', s=80)
plt.scatter(zscore.index[close_cond], zscore[close_cond], marker='o', color='black', s=50)
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
