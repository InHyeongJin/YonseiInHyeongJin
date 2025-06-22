# 주식 시뮬레이션 프로젝트: Adaptive Trading Simulator

## 📌 프로젝트 개요

Adaptive Trading Simulator는 시장 가격의 움직임을 단순한 수학 모델로 시뮬레이션하고, 그에 따라 예측과 투자 전략을 수행해보는 **투자 전략 실험 플랫폼**입니다. 실제 주식 시장처럼 가격이 랜덤하게 변동하며, 예측기를 통해 미래 가격을 예측하고, 예측값을 바탕으로 매매 전략을 실행합니다.

---

## 🎯 프로젝트 목적 및 동기

* **직접 시계열 데이터를 생성하고, 예측기를 활용하여 매매 전략을 테스트해보고 싶다**는 동기에서 출발
* 예전 프로젝트들(카드 게임, 수열 시각화)처럼 단순한 구조 안에 논리적/수학적 설계가 포함되도록 구성
* 실제 시장처럼 동적으로 변하는 데이터를 다뤄보고, 예측 기반 의사결정 시뮬레이션을 수행함으로써 **금융·AI 융합**의 학습 기회를 얻고자 함

---

## 💻 코드 구성 및 설명

### 1. MarketSimulator 클래스

시장 가격을 생성하는 클래스입니다.

```python
class MarketSimulator:
    def __init__(self):
        self.prices = [100, 102]  # 초기 두 가격

    def simulate(self, rounds):
        for _ in range(rounds - 2):
            prev2, prev1 = self.prices[-2], self.prices[-1]
            trend_factor = np.random.uniform(0.95, 1.05)
            shock = np.random.normal(0, 3)
            next_price = trend_factor * prev1 + shock
            self.prices.append(max(1, next_price))
        return self.prices
```

* `trend_factor`와 `shock`을 조합하여 **현실적인 가격 등락**을 생성
* 가격이 1보다 작아지지 않도록 안정화

### 2. AdaptiveRecurrencePredictor 클래스

간단한 선형 계수 기반 예측기입니다.

```python
class AdaptiveRecurrencePredictor:
    def __init__(self):
        self.w1, self.w2 = 0.5, 0.5

    def predict_next(self, prev2, prev1):
        return self.w1 * prev2 + self.w2 * prev1

    def fit(self, prev2, prev1, actual):
        lr = 0.001
        pred = self.predict_next(prev2, prev1)
        error = actual - pred
        self.w1 += lr * error * prev2
        self.w2 += lr * error * prev1
```

* `predict_next`: 두 시점 이전 가격과 이전 가격의 선형 결합으로 다음 가격을 예측
* `fit`: 오차 기반으로 학습률 `lr`을 적용해 가중치를 업데이트

### 3. Trader 클래스

예측에 따라 실제 매수/매도 결정을 내리는 클래스입니다.

```python
class Trader:
    def __init__(self, initial_cash):
        self.cash = initial_cash
        self.shares = 0
        self.history = []
        self.avg_buy_price = None
```

#### 주요 메서드:

```python
    def decide(self, current_price, predicted):
        action = "Hold"
        gain_ratio = (predicted - current_price) / current_price
        if self.avg_buy_price and current_price < 0.95 * self.avg_buy_price:
            self.cash += self.shares * current_price
            action = f"Stop-loss: Sell {self.shares}"
            self.shares = 0
            self.avg_buy_price = None
        elif abs(predicted - current_price) < 2:
            action = "Hold"
        elif gain_ratio > 0.02:
            to_buy = int(0.75 * self.cash / current_price)
            if to_buy > 0:
                self.cash -= to_buy * current_price
                self.avg_buy_price = current_price
                self.shares += to_buy
                action = f"Buy {to_buy}"
        elif gain_ratio > 0.01:
            to_buy = int(0.3 * self.cash / current_price)
            if to_buy > 0:
                self.cash -= to_buy * current_price
                self.avg_buy_price = current_price
                self.shares += to_buy
                action = f"Buy {to_buy}"
        elif gain_ratio < -0.01 and self.shares > 0:
            self.cash += self.shares * current_price
            action = f"Sell {self.shares}"
            self.shares = 0
            self.avg_buy_price = None
        self.history.append((current_price, predicted, self.cash, self.shares, action))
```

* 예측 상승률(gain\_ratio)에 따라 **보수적 또는 공격적 매수**
* 예측 하락 시 **전량 매도**
* 손실폭이 -5% 초과 시 **Stop-loss 발동**

### 4. TradingSimulator 클래스

전체 시뮬레이션 실행을 담당합니다.

```python
class TradingSimulator:
    def __init__(self, rounds=30):
        self.rounds = rounds
        self.market = MarketSimulator()
        self.predictor = AdaptiveRecurrencePredictor()
        self.trader = Trader(initial_cash=10000)
```

```python
    def run(self):
        prices = self.market.simulate(self.rounds)
        for i in range(2, self.rounds):
            prev2, prev1 = prices[i - 2], prices[i - 1]
            predicted = self.predictor.predict_next(prev2, prev1)
            actual = prices[i]
            self.trader.decide(actual, predicted)
            self.predictor.fit(prev2, prev1, actual)
        return prices, self.trader.history
```

### 5. 시각화 함수

* `matplotlib.pyplot`을 이용해 실제 가격, 예측 가격, 이동 평균선(5일), 순자산 그래프 출력
* `PrettyTable`로 거래 로그 테이블 출력

---

## ⚠ 프로젝트 한계점

* **예측 모델의 단순함**: 선형 회귀만 사용하여 복잡한 패턴 예측은 어려움
* **시장 요인의 생략**: 수수료, 세금, 체결 조건 등이 생략됨
* **전략 정적성**: 전략이 유연하지 않고 상황별 커스터마이징이 부족함

---

## ✅ 결론 및 개선 방향

이번 프로젝트를 통해:

* 수학 기반 예측의 한계와 가능성을 확인
* 전략 설계의 중요성과 리스크 관리의 핵심성 인식
* 실제 자산 변화 시각화를 통한 직관적 학습 가능성 체험

### 향후 개선 아이디어

* 머신러닝 예측기(LSTM, Prophet 등) 도입
* 다양한 전략 조합 실험 (모멘텀, 이동평균 크로스 등)
* 리스크 관리 강화 (베타, 샤프 비율 적용)
* 사용자 UI, 매개변수 조절 기능 추가

---

> 본 프로젝트는 Python 3 환경에서 개발되었으며, 사용된 주요 라이브러리는 `numpy`, `matplotlib`, `prettytable` 입니다.
> 본 문서는 `README.md`로 변환되어 GitHub 저장소에 포함됩니다.
