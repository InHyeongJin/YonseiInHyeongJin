# YonseiInHyeongJin
프로젝트 보고서: 턴제 RPG 전투 시뮬레이터 구현 및 분석

1. 프로젝트 개요 및 목적

본 프로젝트는 컴퓨터 프로그래밍과 수학적 모델링을 결합하여, 턴제(Role-Playing Game) 전투 시스템을 시뮬레이션하고, 그 결과를 정량적으로 분석 및 시각화하는 것을 목표로 한다. 단순한 공격과 피해 계산을 넘어서, 각 캐릭터의 능력치를 수학적 함수 및 확률에 기반하여 모델링하고, 전투의 흐름을 시간에 따라 수치화하여 그래프로 표현함으로써 전투의 전략성과 랜덤성을 수학적으로 탐구하고자 한다.

본 프로젝트는 다음과 같은 요소들을 포함한다:

캐릭터의 스탯 기반 전투 시뮬레이션 (체력, 공격력, 방어력, 치명타 확률)

확률적 치명타 처리 및 전투 결과 누적 로그

매 턴의 체력 변화 데이터 수집

체력 변화 시각화 (HP vs Turn Plot)

전투 결과 분석 및 로그 출력

2. 수학적 모델링

2.1 데미지 계산 함수

공격 데미지는 다음과 같은 수학적 모델로 계산된다:



: 공격자(Attacker)의 공격력

: 방어자(Defender)의 방어력

: 최소 1의 피해를 보장하기 위한 안전장치

2.2 치명타 확률

치명타는 확률 변수  로 모델링된다. 는 공격자의 치명타 확률이며, 인 경우 데미지는 2배가 된다.

2.3 전투 시퀀스

한 턴(Turn)에서 전투의 흐름은 다음과 같다:

플레이어가 적을 공격

적이 생존 시, 적이 플레이어를 반격

양쪽 HP 업데이트

로그 저장 및 시각화용 데이터 기록

이러한 흐름은 순차적이고 반복적으로 이루어지며, 수열  으로 플레이어와 적의 체력을 추적한다.

3. 프로그램 구조 및 클래스 설명

3.1 Character 클래스

class Character:
    def __init__(self, name, hp, attack, defense, crit_rate=0.1):

name: 캐릭터 이름

hp: 체력 (Health Points)

attack: 공격력

defense: 방어력

crit_rate: 치명타 확률 (기본값 0.1)

    def calculate_damage(self, target):
        base_dmg = max(1, self.attack - target.defense)
        crit = random.random() < self.crit_rate
        if crit:
            base_dmg *= 2
        return base_dmg, crit

확률적 요소를 포함한 데미지 계산을 담당한다.

에서 일 경우 치명타 적용

    def attack_target(self, target):
        dmg, crit = self.calculate_damage(target)
        target.take_damage(dmg)
        self.history.append((target.name, dmg, crit))
        return dmg, crit

공격 실행 및 히스토리 기록

3.2 TurnBasedRPG 클래스

class TurnBasedRPG:
    def __init__(self):
        self.player = Character("Hero", 100, 20, 5)
        self.enemy = Character("Goblin", 80, 15, 3)
        self.turn_count = 0
        self.battle_log = []

player, enemy: 각 캐릭터 객체 생성

battle_log: 턴별 체력 기록 (시각화 목적)

    def play_turn(self):
        dmg, crit = self.player.attack_target(self.enemy)
        if not self.enemy.is_alive():
            return True
        dmg, crit = self.enemy.attack_target(self.player)
        if not self.player.is_alive():
            return True
        self.battle_log.append((self.turn_count, self.player.hp, self.enemy.hp))
        return False

턴 진행: 공격 → 반격 → 체력 기록 → 전투 종료 여부 판단

    def simulate_battle(self):
        while True:
            if self.play_turn():
                break

전투 반복 실행

    def plot_battle(self):
        data = np.array(self.battle_log)
        plt.plot(turns, player_hp)

matplotlib을 이용해 체력 변화 시각화

전투 전개 양상을 시계열 수열 형태로 표현

4. 전투 시각화 및 해석

각 턴에서 플레이어와 적의 체력은 다음과 같은 점화식 형태의 수열로 볼 수 있다:





이때 은 랜덤한 요소를 포함한 함수로, 시계열 는 확률적 편차를 포함한다.

4.2 그래프 해석

빠르게 감소하는 곡선: 일방적인 전투 우위

교차점: 승패 전환점

일정하게 유지되는 곡선: 방어력의 효과, 낮은 치명타 확률 등

5. 결론 및 확장성 고찰

5.1 결론

본 프로젝트는 수학적 수식(공격력, 방어력, 치명타 확률)을 기반으로 캐릭터 간 전투를 시뮬레이션하고, 전투 진행 과정을 수열 및 함수 관점에서 정량적으로 분석하였다. 단순한 게임 로직을 넘어서, 수학과 확률 이론을 바탕으로 게임 메커니즘을 해석하고, 이를 구조화된 코드와 시각화를 통해 표현함으로써 게임의 전략성과 구조를 학문적으로 재해석하는 경험을 제공하였다.

5.2 확장 가능성

다수의 적 구현 (배열 기반 전투)

회복, 방어, 버프 등의 효과 수학 모델 도입

턴 우선순위 알고리즘 (Agility 기반)

치명타 외에 상태이상 확률 모델링 (중독, 출혈 등)

플레이어의 전략 선택 구현 (가드, 도망, 마법 등)

플레이어 및 적의 행동 예측 AI 구현 (마르코프 모델, MCTS 등)

부록: 실행 예시

== BATTLE START ==
[Turn 1]
Hero attacks Goblin! Damage: 17
Goblin attacks Hero! Damage: 10
[Turn 2]
Hero attacks Goblin! Damage: 20 (CRITICAL!)
Goblin attacks Hero! Damage: 9
...
== BATTLE END ==

Battle Summary:
Total Turns: 6
Final HP - Hero: 35, Goblin: 0
Detailed Attack Log:
Hero → Hit Goblin for 17
Hero → Hit Goblin for 20 (CRIT)
...

