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

> **역할**: 과거 데이터를 기반으로 한 점화식 예측 모델 구현

* `__init__`: 예측할 과거 주기 길이(`window_size`) 설정
* `fit`: 과거 가격 데이터를 저장함
* `predict_next`: 최근 `window_size` 만큼의 데이터를 이용해 다음 값을 단순 선형 회귀를 통해 예측

```python
def predict_next(self):
    if len(self.data) < self.window_size:
        return self.data[-1]
    X = np.arange(self.window_size).reshape(-1, 1)
    y = np.array(self.data[-self.window_size:])
    model = LinearRegression().fit(X, y)
    return model.predict([[self.window_size]])[0]
```

---

### 2. `MarketSimulator`

> **역할**: 시뮬레이션용 시장 데이터 생성 (랜덤 워크 + 노이즈)

* `generate_data`: 초기 가격을 기준으로 확률적 주가 변동 시뮬레이션
* `get_data`: n일 간의 가격 데이터 출력

```python
def generate_data(self, steps=100):
    price = self.initial_price
    self.data = []
    for _ in range(steps):
        change_percent = random.uniform(-self.volatility, self.volatility)
        price *= (1 + change_percent)
        self.data.append(price)
    return self.data
```

---

### 3. `Trader`

> **역할**: 예측값과 실제 이동 평균선을 기준으로 매수/매도 판단 후 포지션 변화

* `decide`: 다음날 가격을 예측하고, 현재가와 비교 후 행동 결정
* `trade`: `cash`, `stock`, `asset_history` 업데이트
* `finalize`: 시뮬레이션 종료 후 잔여 주식을 모두 매도하여 현금화

```python
def trade(self, action, current_price):
    if action == 'buy':
        amount = self.cash / current_price
        self.stock += amount
        self.cash = 0
    elif action == 'sell':
        self.cash += self.stock * current_price
        self.stock = 0
```

---

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
