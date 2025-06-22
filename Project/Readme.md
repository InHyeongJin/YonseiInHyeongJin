#  주제: 주가 예측 기반 자동매매 시뮬레이션 프로젝트

---

## 1. 모티베이션 (프로젝트를 하게 된 동기)

주식 시장에서는 예측 불가능한 가격 변동성과 인간 감정에 따른 의사결정으로 인해 수익을 내기 어려운 경우가 많다. 이러한 문제를 해결하고자, 과거 데이터를 기반으로 일정한 규칙성을 포착하여 주가를 예측하고, 이에 기반해 자동으로 매매 결정을 내리는 프로그램을 만들어 보고 싶었다. 특히, 반복 수열 구조를 이용한 예측 방식과 매매 전략을 결합하여 시뮬레이션 결과를 시각화하는 통합적인 시스템을 구현하는 것이 본 프로젝트의 핵심 목표였다.

---

## 2. 이론적 배경

* **선형 회귀**와 **이동 평균선 (Moving Average)**: 주가 데이터의 추세를 파악하는 기법으로 사용되며, 단기-장기 이동 평균선을 통해 매수/매도 시점을 파악할 수 있다.
* **선형 점화식 (Linear Recurrence Relation)**: 이전 항의 값으로 다음 항을 예측하는 수학적 모델로, 주가 예측 모델의 근간이 된다.
* **시뮬레이션 기반 자동매매 전략**: 일정한 규칙에 따라 매수/매도 조건을 판단하고 포지션을 취하는 전략으로, 인간의 개입 없이 자동으로 작동한다.

---

## 3. 코드 작성방법 및 설명

### 핵심 구성 요소: 총 4개의 클래스 기반 구조

### 1. `AdaptiveRecurrencePredictor`

> **역할**: 직전 두 시점의 가격을 기반으로 다음 시점 가격을 예측하는 단순 점화식 기반 선형 회귀 모델

* `__init__`: 예측 계수를 저장할 변수 `self.coefficients`를 초기화합니다. 처음에는 예측 계수가 없기 때문에 `None`으로 설정됩니다.

* `fit(prev2, prev1, current)`: 두 시점의 과거 가격(`prev2`, `prev1`)을 독립변수로, 현재 가격(`current`)을 종속변수로 하여 선형 회귀 계수를 계산합니다. `np.linalg.lstsq`를 사용해 최소제곱법으로 계수를 구하고, 이 값을 저장합니다.

* `predict_next(prev2, prev1)`: 저장된 계수를 이용하여 다음 가격을 예측합니다. 계수가 아직 없을 경우에는 이전 가격 중 하나를 그대로 반환합니다. 예측은 `prev2 * w1 + prev1 * w2` 형태로 계산됩니다.

```python
class AdaptiveRecurrencePredictor:
    def __init__(self):
        self.coefficients = None

    def fit(self, prev2, prev1, current):
        A = np.array([[prev2, prev1]])
        y = np.array([current])
        coeffs, _, _, _ = np.linalg.lstsq(A, y, rcond=None)
        self.coefficients = coeffs.flatten()
        return self.coefficients

    def predict_next(self, prev2, prev1):
        if self.coefficients is None or len(self.coefficients) == 0:
            return prev1
        return float(self.coefficients[0] * prev2 + self.coefficients[1] * prev1)
```

---

### 2. `MarketSimulator`

> **역할**: 시장의 가격 흐름을 랜덤한 요인으로 생성하여 투자 시뮬레이션의 환경을 제공합니다.

* `__init__(length)`: 시뮬레이션할 전체 기간(`length`)을 받아 내부적으로 가격을 생성합니다.

* `_generate_prices()`: 초기 가격 2개는 고정값 `[100, 102]`으로 시작합니다. 이후 라운드부터는 직전 가격에 `0.95~1.05` 범위의 추세 요인을 곱하고, 정규분포 기반의 무작위 노이즈를 더하여 다음 가격을 생성합니다. 이 방식은 무작위성과 약간의 추세성을 동시에 반영합니다.

```python
class MarketSimulator:
    def __init__(self, length):
        self.length = length
        self.prices = self._generate_prices()

    def _generate_prices(self):
        prices = [100, 102]
        for _ in range(self.length - 2):
            trend_factor = np.random.uniform(0.95, 1.05)
            shock = np.random.normal(0, 3)
            next_price = trend_factor * prices[-1] + shock
            prices.append(max(1, next_price))
        return prices
```

---

### 3. `Trader`

> **역할**: 예측된 가격과 실제 가격의 차이를 분석하여 매수, 매도, 보유 등의 결정을 내리고, 자산을 운용합니다.

* `__init__(name, cash)`: 초기 자산(cash), 주식 보유량, 거래 기록 등을 초기화합니다.

* `decide(current_price, predicted_price)`: 예측값과 실제값을 비교하여 다음과 같은 조건으로 행동을 결정합니다:

  * 예측값과 실제값의 차이가 작으면 관망(Hold)
  * 예측 상승폭이 2% 이상 → 자산의 75% 매수
  * 예측 상승폭이 1\~2% → 자산의 30% 매수
  * 예측 하락폭이 1% 이상 → 전량 매도
  * 현재가가 평균 매입가보다 5% 이상 하락 시 → 손절

* `net_worth(current_price)`: 현재 보유 현금과 주식의 시장 가치를 합산하여 자산 총액을 계산합니다.

* `print_history()`: 거래 기록을 표 형식으로 출력합니다.

* `get_net_worth_series(prices)`: 각 라운드마다의 순자산 변화를 리스트로 반환합니다.

```python
class Trader:
    def __init__(self, name, cash):
        self.name = name
        self.cash = cash
        self.shares = 0
        self.history = []
        self.avg_buy_price = None

    def decide(self, current_price, predicted_price):
        error_threshold = 2.0
        if abs(predicted_price - current_price) < error_threshold:
            action = "Hold"
        else:
            gain_ratio = (predicted_price - current_price) / current_price
            if self.avg_buy_price and current_price < 0.95 * self.avg_buy_price:
                self.cash += self.shares * current_price
                action = f"Stop-loss: Sell {self.shares}"
                self.shares = 0
                self.avg_buy_price = None
            elif gain_ratio > 0.02:
                to_buy = int(0.75 * self.cash / current_price)
                self.shares += to_buy
                self.cash -= to_buy * current_price
                if to_buy > 0:
                    self.avg_buy_price = current_price
                action = f"Buy {to_buy}"
            elif gain_ratio > 0.01:
                to_buy = int(0.3 * self.cash / current_price)
                self.shares += to_buy
                self.cash -= to_buy * current_price
                if to_buy > 0:
                    self.avg_buy_price = current_price
                action = f"Buy {to_buy}"
            elif gain_ratio < -0.01:
                self.cash += self.shares * current_price
                action = f"Sell {self.shares}"
                self.shares = 0
                self.avg_buy_price = None
            else:
                action = "Hold"

        self.history.append((current_price, predicted_price, self.cash, self.shares, action))
```

---

### 4. `Simulator`

> **역할**: 전체 시뮬레이션 실행, 가격 예측과 투자 전략 수행, 시각화 포함

* `__init__`: 시뮬레이터는 시장(MarketSimulator), 예측기(AdaptiveRecurrencePredictor), 투자자(Trader)를 초기화합니다.

* `run()`: 전체 라운드 동안 다음 순서로 반복:

  * 직전 두 가격으로 예측
  * 실제 가격과 비교해 투자자 결정 → 거래 실행
  * 예측기 업데이트 (학습)
  * 마지막에 순자산 출력 및 그래프 시각화

* `_plot(prices)`: 실제 가격, 예측 가격, 이동 평균(5일)을 그래프로 출력합니다.

* `_plot_net_worth(prices)`: 순자산의 변화 추이를 그래프로 시각화합니다.

```python
class Simulator:
    def __init__(self, length=30):
        self.market = MarketSimulator(length)
        self.predictor = AdaptiveRecurrencePredictor()
        self.trader = Trader("Player", 10000)

    def run(self):
        prices = self.market.prices
        for i in range(2, len(prices)):
            prev2, prev1 = prices[i-2], prices[i-1]
            predicted = self.predictor.predict_next(prev2, prev1)
            actual = prices[i]
            self.trader.decide(actual, predicted)
            self.predictor.fit(prev2, prev1, actual)

        self.trader.print_history()
        final_price = prices[-1]
        print(f"\n최종 자산 가치: {round(self.trader.net_worth(final_price), 2)}원")
        self._plot(prices)
        self._plot_net_worth(prices)
```


### 4. `Simulator`

> **역할**: 전체 시뮬레이션 실행 및 결과 시각화

* `run`: 예측-매매 루프 실행, 각 시점의 순자산 기록
* `plot_results`: 실제 가격, 예측값, 자산 변화, 이동평균선 등 시각화

```python
def run(self):
    for day in range(self.predictor.window_size, len(self.data)):
        current_price = self.data[day]
        ma = np.mean(self.data[day - self.predictor.window_size:day])
        self.predictor.fit(self.data[day - self.predictor.window_size:day])
        predicted_price = self.predictor.predict_next()
        action = self.trader.decide(predicted_price, current_price, ma)
        self.trader.trade(action, current_price)
        asset = self.trader.cash + self.trader.stock * current_price
        self.trader.asset_history.append(asset)
    self.trader.finalize(self.data[-1])
```

---

## 4.  프로젝트의 한계

* 매우 단순한 **선형 회귀**만으로 예측하므로, 실제 주가처럼 비선형적이고 외부 변수가 많은 데이터에는 약할 수 있음
* 현재 전략은 단일 이동 평균과 비교해 예측가가 높으면 매수, 낮으면 매도하는 구조로, **리스크 관리**가 부족함
* 실제 시장의 **수수료**, **슬리피지**, **심리적 요소**, **변동성 급등** 등은 반영되지 않음

---

## 5. 결론 및 개선점

###  성과

* 반복 수열 기반의 간단한 머신 예측 모델과 자동 매매 전략을 연계하여 시뮬레이션 수행
* 시각화를 통해 자산 추이와 예측 오차 시각적으로 확인 가능

###  개선 아이디어

* 예측 모델을 **LSTM**, **ARIMA**, **Transformer 기반 시계열 모델** 등으로 고도화
* **다중 이동 평균선 전략 (예: 골든크로스, 데드크로스)** 도입
* 변동성 지표 (예: RSI, MACD) 등 다양한 보조지표 활용 가능
* 포트폴리오 개념으로 **다중 종목** 매매 시뮬레이션 가능성 탐색

---

## 🛠 사용 라이브러리

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import random
```

---

## 실행 방법 (예시)

```python
market = MarketSimulator(initial_price=100)
data = market.generate_data(steps=100)

predictor = AdaptiveRecurrencePredictor(window_size=5)
trader = Trader(cash=10000)
simulator = Simulator(data, predictor, trader)
simulator.run()
simulator.plot_results()
```
