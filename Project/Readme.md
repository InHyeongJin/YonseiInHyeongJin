#  주제: 주가 예측 기반 자동매매 시뮬레이션 프로젝트
 
#### 수학과프로그래밍 / 인형진 (2021131028)

---

## 1. 모티베이션 (프로젝트를 하게 된 동기)

저는 약 3년간 해외 주식 투자를 경험하면서 주가의 변동성과 예측의 어려움을 직접 체감해 왔습니다. 이번 학기 ‘수학과 프로그래밍’ 수업에서 배운 파이썬의 데이터 시각화 기법(Matplotlib)이 특히 흥미로웠고, 이는 제가 직접 주가 그래프를 구현해 보고 싶다는 생각으로 이어졌습니다. 또한, 반복되는 수열 구조를 분석하는 점화식 개념 역시 매우 인상 깊었습니다. 이러한 요소들을 실제 투자 시뮬레이션에 접목시켜 보고자, 점화식을 활용한 단순한 주가 예측 모델을 설계하고 이를 기반으로 자동 매매 전략을 구현한 뒤, 시각화까지 포함한 통합적인 프로젝트를 진행하게 되었습니다.


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
---

## 4.  프로젝트의 한계

* 매우 단순한 **선형 회귀**만으로 예측하므로, 실제 주가처럼 비선형적이고 외부 변수가 많은 데이터에는 약할 수 있음
* 현재 전략은 단일 이동 평균과 비교해 예측가가 높으면 매수, 낮으면 매도하는 구조로, **리스크 관리**가 부족함
* 실제 시장의 **수수료**, **슬리피지**, **심리적 요소**, **변동성 급등** 등은 반영되지 않음

---
## 5. 실행 예시
| Round | Price  | Predicted |   Cash   | Shares |       Action       |
|-------|--------|-----------|----------|--------|--------------------|
| 1     | 101.06 | 102.00    | 10000.00 | 0      | Hold               |
| 2     | 96.52  | 101.58    | 2567.62  | 77     | Buy 77             |
| 3     | 93.69  | 93.93     | 2567.62  | 77     | Hold               |
| 4     | 92.93  | 90.18     | 9723.00  | 0      | Sell 77            |
| 5     | 99.77  | 91.15     | 9723.00  | 0      | Sell 0             |
| 6     | 102.88 | 103.01    | 9723.00  | 0      | Hold               |
| 7     | 106.10 | 108.12    | 6858.19  | 27     | Buy 27             |
| 8     | 109.56 | 109.42    | 6858.19  | 27     | Hold               |
| 9     | 108.56 | 113.07    | 1755.96  | 74     | Buy 47             |
| 10    | 105.23 | 109.76    | 493.21   | 86     | Buy 12             |
| 11    | 112.62 | 103.14    | 10178.43 | 0      | Sell 86            |
| 12    | 121.39 | 114.67    | 10178.43 | 0      | Sell 0             |
| 13    | 116.65 | 130.41    | 2596.35  | 65     | Buy 65             |
| 14    | 109.80 | 118.40    | 9733.29  | 0      | Stop-loss: Sell 65 |
| 15    | 105.90 | 104.48    | 9733.29  | 0      | Hold               |
| 16    | 100.94 | 100.83    | 9733.29  | 0      | Hold               |
| 17    | 103.33 | 96.81     | 9733.29  | 0      | Sell 0             |
| 18    | 96.79  | 101.96    | 2474.28  | 75     | Buy 75             |
| 19    | 103.82 | 94.77     | 10260.69 | 0      | Sell 75            |
| 20    | 100.53 | 103.84    | 2620.42  | 76     | Buy 76             |
| 21    | 96.30  | 102.22    | 694.42   | 96     | Buy 20             |
| 22    | 94.11  | 92.76     | 694.42   | 96     | Hold               |
| 23    | 93.17  | 91.02     | 9638.99  | 0      | Sell 96            |
| 24    | 88.55  | 91.64     | 2466.79  | 81     | Buy 81             |
| 25    | 88.17  | 85.92     | 9608.55  | 0      | Sell 81            |
| 26    | 91.92  | 85.69     | 9608.55  | 0      | Sell 0             |
| 27    | 91.94  | 93.67     | 9608.55  | 0      | Hold               |
| 28    | 91.04  | 93.82     | 2416.28  | 79     | Buy 79             |

**최종 자산 가치: 9608.55원**
![image](https://github.com/user-attachments/assets/7ab9f4ec-4931-42d6-9302-70e9af58bebc)
![image](https://github.com/user-attachments/assets/036dc120-8c57-4da6-8405-453407ef689c)


---

## 6. 결론 및 개선점

이번 프로젝트를 통해 반복 수열 구조를 활용한 간단한 예측 모델과 자동 매매 전략을 결합하여 주가 변동을 시뮬레이션하고, 그 결과를 시각적으로 확인할 수 있는 시스템을 구현해보았습니다. 예측과 거래 결과를 시간 흐름에 따라 시각화하면서 자산의 변화와 전략의 효용을 직관적으로 파악할 수 있었고, 점화식을 실전 데이터에 적용해보는 과정을 통해 이론과 실습을 자연스럽게 연결해볼 수 있었습니다.

다만, 사용된 예측 모델이 매우 단순한 선형 점화식 기반이기 때문에 실제 시장의 복잡한 움직임이나 외부 요인들을 반영하는 데에는 한계가 있었습니다. 또한 매매 전략 역시 정적인 규칙 기반으로 설계되어 있어 급격한 변동이나 비정상적인 상황에서는 대응력이 떨어지는 점도 확인할 수 있었습니다. 

향후에는 다음과 같은 방향으로 개선해볼 수 있을 것입니다:

- 예측 모델을 LSTM, ARIMA, Transformer 기반의 시계열 예측 기법으로 고도화하여 보다 정밀한 예측이 가능하도록 개선

- 골든크로스나 데드크로스와 같은 다중 이동 평균선 전략을 도입해 더욱 정교한 매매 시점 판단

- RSI, MACD 등 다양한 기술적 지표를 활용하여 시장의 강도와 변동성을 반영한 전략 설계

- 단일 종목이 아닌 다중 종목을 동시에 시뮬레이션하여 포트폴리오 기반의 자동 매매로 확장

이러한 개선점을 반영한다면 보다 현실적인 시장 시뮬레이션과 실용적인 자동매매 전략 구축으로 발전시켜 나갈 수 있을 것 같습니다. 개인적으로 다음 학기에 열리는 '기계학습과응용'수업을 들어 더 나은 프로젝트를 시도해보고 싶습니다.


---

## 사용 라이브러리

```python
import numpy as np
import matplotlib.pyplot as plt
from prettytable import PrettyTable
import random
```
