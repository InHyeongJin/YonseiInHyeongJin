import numpy as np
import matplotlib.pyplot as plt
from prettytable import PrettyTable

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

    def net_worth(self, current_price):
        return self.cash + self.shares * current_price

    def print_history(self):
        table = PrettyTable()
        table.field_names = ["Round", "Price", "Predicted", "Cash", "Shares", "Action"]
        for i, (p, pred, c, s, act) in enumerate(self.history):
            table.add_row([i+1, round(p, 2), round(pred, 2), round(c, 2), s, act])
        print(table)

    def get_net_worth_series(self, prices):
        worth_series = []
        for i, (p, _, c, s, _) in enumerate(self.history):
            worth_series.append(c + s * prices[i+2])
        return worth_series

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

    def _plot(self, prices):
        rounds = list(range(1, len(prices) + 1))
        predicted = [None, None]
        temp_predictor = AdaptiveRecurrencePredictor()
        for i in range(2, len(prices)):
            prev2, prev1 = prices[i-2], prices[i-1]
            pred = temp_predictor.predict_next(prev2, prev1)
            predicted.append(pred)
            temp_predictor.fit(prev2, prev1, prices[i])

        moving_avg = [None] * 4 + [np.mean(prices[i-4:i+1]) for i in range(4, len(prices))]

        plt.figure(figsize=(10, 5))
        plt.plot(rounds, prices, label='Actual Price')
        plt.plot(rounds, predicted, label='Predicted Price', linestyle='--')
        plt.plot(rounds, moving_avg, label='5-Round Moving Avg', linestyle=':')
        plt.xlabel('Round')
        plt.ylabel('Price')
        plt.title('Market Price vs Predicted')
        plt.legend()
        plt.grid(True)
        plt.show()

    def _plot_net_worth(self, prices):
        worth = self.trader.get_net_worth_series(prices)
        rounds = list(range(3, len(prices)+1))

        plt.figure(figsize=(10, 4))
        plt.plot(rounds, worth, color='green', label='Net Worth')
        plt.xlabel('Round')
        plt.ylabel('Net Worth')
        plt.title('Trader Net Worth Over Time')
        plt.grid(True)
        plt.legend()
        plt.show()

if __name__ == '__main__':
    sim = Simulator()
    sim.run()
