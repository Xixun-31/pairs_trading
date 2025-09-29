# Pairs Trading Strategy Analysis

## 專案簡介
這個專案使用 Python 與 CoinGecko API，對多組加密貨幣進行 Pairs Trading（配對交易）策略分析，包含以下交易對：

- OP / ARB  
- OP / MATIC  
- ARB / MATIC  

策略基於日線價格回歸分析（OLS），計算 spread 與 z-score，並透過動態閾值決定開倉與平倉時機，考慮手續費與滑點後回測績效。

---

## 技術堆疊
- Python 3.x  
- pandas, numpy, matplotlib, statsmodels  
- CoinGeckoAPI (抓取加密貨幣歷史價格)  

---

## 策略流程

1. **資料抓取**  
   使用 CoinGecko API 抓取指定幣種的日線歷史價格。

2. **資料整理**  
   - 計算每日報酬率 (`pct_change()`)  
   - 合併成 DataFrame 便於後續回歸與分析

3. **OLS 回歸**  
   - 用其中一個幣種價格對另一個幣種價格做線性回歸  
   - 計算 alpha、beta，並檢查統計顯著性（p-value）

4. **Spread 與 Z-Score 計算**  
# Pairs Trading Strategy Analysis

## 專案簡介
這個專案使用 Python 與 CoinGecko API，對多組加密貨幣進行 Pairs Trading（配對交易）策略分析，包含以下交易對：

- OP / ARB  
- OP / MATIC  
- ARB / MATIC  

策略基於日線價格回歸分析（OLS），計算 spread 與 z-score，並透過動態閾值決定開倉與平倉時機，考慮手續費與滑點後回測績效。

---

## 技術堆疊
- Python 3.x  
- pandas, numpy, matplotlib, statsmodels  
- CoinGeckoAPI (抓取加密貨幣歷史價格)  

---

## 策略流程

1. **資料抓取**  
   使用 CoinGecko API 抓取指定幣種的日線歷史價格。

2. **資料整理**  
   - 計算每日報酬率 (`pct_change()`)  
   - 合併成 DataFrame 便於後續回歸與分析

3. **OLS 回歸**  
   - 用其中一個幣種價格對另一個幣種價格做線性回歸  
   - 計算 alpha、beta，並檢查統計顯著性（p-value）

4. **Spread 與 Z-Score 計算**  
Spread = Y - (alpha + beta * X)
z-score = (spread - rolling_mean) / rolling_std

5. **交易信號**  
- 開倉閾值 (`z_open`)  
- 平倉閾值 (`z_close`)  
- 建立倉位矩陣，Long/Short 根據 z-score 判斷

6. **績效回測**  
- 扣除手續費 (`commission`) 與滑點 (`slippage`)  
- 計算策略每日收益、累積收益  
- 統計指標：
  - 累積報酬率 (Cumulative Return)
  - 夏普比率 (Sharpe Ratio)
  - 最大回撤 (Maximum Drawdown)
  - 交易次數與平均持倉天數

---

## 使用方法

1. 安裝必要套件：
```bash
pip install pandas numpy matplotlib statsmodels pycoingecko

5. **交易信號**  
- 開倉閾值 (`z_open`)  
- 平倉閾值 (`z_close`)  
- 建立倉位矩陣，Long/Short 根據 z-score 判斷

6. **績效回測**  
- 扣除手續費 (`commission`) 與滑點 (`slippage`)  
- 計算策略每日收益、累積收益  
- 統計指標：
  - 累積報酬率 (Cumulative Return)
  - 夏普比率 (Sharpe Ratio)
  - 最大回撤 (Maximum Drawdown)
  - 交易次數與平均持倉天數

---

## 使用方法

1. 安裝必要套件：
```bash
pip install pandas numpy matplotlib statsmodels pycoingecko

2. 執行各個交易對的策略腳本：
python op_arb_pairs.py   # OP / ARB
python op_matic_pairs.py # OP / MATIC
python arb_matic_pairs.py # ARB / MATIC

3. 結果包含：
- 累積收益圖（需另行生成）
- z-score 與交易訊號圖（需另行生成）
- 策略 P&L 分布圖（需另行生成）
- 文字化績效統計：
  - Final cumulative return
  - Total trades
  - Average holding days per trade
  - OLS alpha & beta
  - p-value
  - Annualized Sharpe Ratio
  - Maximum Drawdown

---

## 策略結果概覽

### OP / ARB
- **Final cumulative return:** 1.1014  
- **Total trades:** 46  
- **Average holding days per trade:** 4.35  
- **OLS alpha:** 0.4743, **beta:** 0.5934  
- **p-value for alpha:** 4.65e-37  
- **p-value for beta:** 1.07e-13  
- **Annualized Sharpe Ratio:** 0.6368  
- **Maximum Drawdown:** -10.23%

### OP / MATIC
- **Final cumulative return:** 1.0697  
- **Total trades:** 26  
- **Average holding days per trade:** 6.35  
- **OLS alpha:** 0.2373, **beta:** 2.1829  
- **p-value for alpha:** 1.74e-08  
- **p-value for beta:** 6.87e-82  
- **Annualized Sharpe Ratio:** 0.5442  
- **Maximum Drawdown:** -13.14%

### ARB / MATIC
- **Final cumulative return:** 1.7780  
- **Total trades:** 34  
- **Average holding days per trade:** 4.85  
- **OLS alpha:** -0.0453, **beta:** 1.6936  
- **p-value for alpha:** 1.03e-07  
- **p-value for beta:** 1.40e-140  
- **Annualized Sharpe Ratio:** 3.0544  
- **Maximum Drawdown:** -6.92%

---

## 可調整參數

- `z_open`：開倉 z-score 閾值（預設 1.0~1.1）  
- `z_close`：平倉 z-score 閾值（預設 0.5~0.55）  
- `rolling_window`：計算 rolling mean & std 的視窗大小（預設 30 天）  
- `commission`：手續費比例（預設 0.001）  
- `slippage`：滑點比例（預設 0.0005）

---

## 注意事項

1. **樣本內 vs 樣本外**  
   - 調整參數過度適配樣本內資料可能導致樣本外表現下降  
   - 建議分區段測試（例如前 365 天到 200 天作樣本內，最近 200 天作樣本外）

2. **幣種相關性**  
   - 策略依賴高度相關的交易對，低相關可能導致 z-score 信號不穩定

3. **風險管理**  
   - 最大回撤與夏普比率是策略績效的核心指標  
   - 可額外設置止損或持倉上限以控制風險

4. **資料延遲與 API 限制**  
   - CoinGecko API 有請求限制，連續抓取大量資料需考慮 rate limit  
   - 若使用其他資料源，需調整時間戳或資料格式

---

## 結論

此專案提供完整的加密貨幣 Pairs Trading 分析流程，從資料抓取、回歸分析、z-score 計算到交易回測，並生成績效統計與圖表。可依據不同交易對與參數設計進行策略優化與風險評估。
