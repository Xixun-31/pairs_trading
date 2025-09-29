# pairs_trading
Pairs Trading Strategy Analysis
📌 專案簡介
這個專案使用 Python 與 CoinGecko API，對多組加密貨幣進行 Pairs Trading（配對交易）策略分析，包含以下交易對：
OP / ARB
OP / MATIC
ARB / MATIC
策略基於 日線價格回歸分析（OLS），計算 spread 與 z-score，並透過動態閾值決定開倉與平倉時機，考慮手續費與滑點後回測績效。
🛠️ 技術堆疊
Python 3.x
pandas, numpy, matplotlib, statsmodels
CoinGeckoAPI (抓取加密貨幣歷史價格)
🔢 策略流程
資料抓取
使用 CoinGecko API 抓取指定幣種的日線歷史價格。
可抓取固定天數或指定時間區間的資料。
資料整理
計算每日報酬率 (pct_change)
合併成 DataFrame，便於後續回歸與分析
OLS 回歸
用其中一個幣種價格對另一個幣種價格做線性回歸
計算 alpha、beta，並檢查統計顯著性（p-value）
Spread 與 Z-Score 計算
Spread = Y - (alpha + beta * X)
z-score = (spread - rolling_mean) / rolling_std
交易信號
開倉閾值 (z_open)
平倉閾值 (z_close)
建立倉位矩陣，Long/Short 根據 z-score 判斷
績效回測
扣除手續費 (commission) 與滑點 (slippage)
計算策略每日收益、累積收益
統計指標：
累積報酬率 (Cumulative Return)
夏普比率 (Sharpe Ratio)
最大回撤 (Maximum Drawdown)
交易次數與平均持倉天數
圖表分析
Spread & z-score 與交易信號
累積收益與回撤
z-score 閾值線
策略 P&L 分布
⚡ 使用方法
安裝必要套件：
pip install pandas numpy matplotlib statsmodels pycoingecko
執行各個交易對的策略腳本：
python op_arb_pairs.py   # OP / ARB
python op_matic_pairs.py # OP / MATIC
python arb_matic_pairs.py # ARB / MATIC
結果包含：
累積收益圖
z-score 與交易訊號圖
策略盈虧分布圖
文字化績效統計：
Final cumulative return
Total trades
Average holding days per trade
OLS alpha & beta
p-value
Annualized Sharpe Ratio
Maximum Drawdown
📊 策略結果概覽
Pair	Cumulative Return	Sharpe Ratio	Max Drawdown	Total Trades
OP / ARB	~1.10	0.64	~10.2%	46
OP / MATIC	~1.07	0.54	~13.1%	26
ARB / MATIC	~1.78	3.05	~6.9%	34
可以看到 ARB/MATIC 表現最佳，夏普比率高、回撤低，顯示風險調整後報酬優異。
🔧 可調整參數
rolling_window: 計算 spread 平均與標準差的窗口大小
z_open / z_close: 開倉和平倉的 z-score 閾值
commission / slippage: 手續費與滑點
start_days_ago / end_days_ago: 樣本內/樣本外資料範圍
💡 注意事項
本策略為 歷史回測，不保證未來收益。
樣本內優化過後，樣本外表現可能下降。
建議搭配 風險控管（資金分配、最大持倉比例）使用。
z-score 過低或過高可能造成過度交易或信號延遲，可調整滾動平均視窗。
