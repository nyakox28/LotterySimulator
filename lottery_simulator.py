#!/usr/bin/env python3
"""
宝くじシミュレーター

確率値を使用せず、番号ベースの抽選によって当せんを判定するシミュレーター。
"""

import random
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class Lottery:
    """
    宝くじの1枚を表すクラス

    Attributes:
        group: 組番号（1-200）
        number: 下5桁番号（0-99999）
    """
    group: int  # 組番号（1-200）
    number: int  # 下5桁番号（00000-99999）

    def __str__(self):
        return f"{self.group:03d}組 {self.number:05d}"

    def __eq__(self, other):
        if not isinstance(other, Lottery):
            return False
        return self.group == other.group and self.number == other.number

    def __hash__(self):
        return hash((self.group, self.number))


class LotterySimulator:
    """宝くじシミュレーターのメインクラス"""

    # 定数定義
    TOTAL_GROUPS = 200  # 組の総数
    NUMBERS_PER_GROUP = 100000  # 1組あたりの番号数（00000-99999）
    TICKETS_PER_SET = 10  # 1セットあたりの枚数
    PRICE_PER_SET = 3000  # 1セットの価格
    MAX_SETS = 33  # 最大購入セット数

    # 賞金額
    PRIZE_1ST = 700_000_000  # 1等：7億円
    PRIZE_1ST_ADJACENT = 150_000_000  # 1等前後賞：1億5千万円
    PRIZE_2ND = 10_000_000  # 2等：1千万円
    PRIZE_3RD = 1_000_000  # 3等：100万円
    PRIZE_4TH = 50_000  # 4等：5万円
    PRIZE_5TH = 10_000  # 5等：1万円
    PRIZE_6TH = 3_000  # 6等：3千円
    PRIZE_7TH = 300  # 7等：300円

    def __init__(self, seed=None):
        """
        初期化

        Args:
            seed: 乱数シード（再現性のため）
        """
        if seed is not None:
            random.seed(seed)

        self.renban_tickets: List[Lottery] = []  # 連番のくじ
        self.bara_tickets: List[Lottery] = []  # バラのくじ
        self.winning_number: Lottery = None  # 1等当せん番号
        self.bonus_digit: int = None  # 7等の指定下1桁

    def generate_renban_set(self) -> List[Lottery]:
        """
        連番セットを1つ生成

        Returns:
            連番セット（10枚のくじ）
        """
        # ランダムに組を選択
        group = random.randint(1, self.TOTAL_GROUPS)

        # 連続する10枚の開始番号を選択（0-99989の範囲）
        start_number = random.randint(0, self.NUMBERS_PER_GROUP - self.TICKETS_PER_SET)

        # 連続する10枚を生成
        tickets = []
        for i in range(self.TICKETS_PER_SET):
            tickets.append(Lottery(group, start_number + i))

        return tickets

    def generate_bara_set(self) -> List[Lottery]:
        """
        バラセットを1つ生成

        Returns:
            バラセット（10枚のくじ）
        """
        tickets = []

        # 使用する組をランダムに10個選択（重複なし）
        available_groups = list(range(1, self.TOTAL_GROUPS + 1))
        selected_groups = random.sample(available_groups, self.TICKETS_PER_SET)

        # 下1桁が0-9になるように番号を生成
        for i, group in enumerate(selected_groups):
            last_digit = i  # 0-9
            # 下1桁がlast_digitになる番号をランダムに選択（0, 10, 20, ..., 99990のいずれか）
            number = random.randint(0, 9999) * 10 + last_digit
            tickets.append(Lottery(group, number))

        # シャッフルして連続性をなくす
        random.shuffle(tickets)

        return tickets

    def purchase_tickets(self, renban_sets: int, bara_sets: int):
        """
        くじを購入

        Args:
            renban_sets: 連番セット数
            bara_sets: バラセット数

        Raises:
            ValueError: セット数が不正な場合
        """
        if renban_sets < 0 or bara_sets < 0:
            raise ValueError("セット数は0以上の整数である必要があります")

        if renban_sets + bara_sets > self.MAX_SETS:
            raise ValueError(f"合計セット数は{self.MAX_SETS}セットまでです")

        # 連番セットを生成
        self.renban_tickets = []
        for _ in range(renban_sets):
            self.renban_tickets.extend(self.generate_renban_set())

        # バラセットを生成
        self.bara_tickets = []
        for _ in range(bara_sets):
            self.bara_tickets.extend(self.generate_bara_set())

    def draw_winning_number(self):
        """1等当せん番号を抽選"""
        # 組番号をランダムに選択（1-200）
        winning_group = random.randint(1, self.TOTAL_GROUPS)

        # 下5桁番号をランダムに選択（0-99999）
        winning_number = random.randint(0, self.NUMBERS_PER_GROUP - 1)

        self.winning_number = Lottery(winning_group, winning_number)

        # 7等の下1桁もランダムに決定
        self.bonus_digit = random.randint(0, 9)

    def check_prize(self, ticket: Lottery) -> Tuple[str, int]:
        """
        1枚のくじの当せん等級と賞金額を判定

        Args:
            ticket: 判定対象のくじ

        Returns:
            (等級名, 賞金額) のタプル
        """
        if self.winning_number is None:
            return ("なし", 0)

        # 1等：組番号および下5桁番号が完全一致
        if ticket == self.winning_number:
            return ("1等", self.PRIZE_1ST)

        # 1等前後賞：組番号が同一で、下5桁が±1
        if ticket.group == self.winning_number.group:
            if ticket.number == self.winning_number.number - 1:
                if self.winning_number.number > 0:  # 00000未満は無効
                    return ("1等前後賞", self.PRIZE_1ST_ADJACENT)
            elif ticket.number == self.winning_number.number + 1:
                if self.winning_number.number < self.NUMBERS_PER_GROUP - 1:  # 99999を超える場合は無効
                    return ("1等前後賞", self.PRIZE_1ST_ADJACENT)

        # 以降、下位の等級を判定
        # 2等：組番号一致かつ下4桁一致
        if ticket.group == self.winning_number.group:
            if ticket.number % 10000 == self.winning_number.number % 10000:
                return ("2等", self.PRIZE_2ND)

        # 3等：下4桁一致
        if ticket.number % 10000 == self.winning_number.number % 10000:
            return ("3等", self.PRIZE_3RD)

        # 4等：下3桁一致
        if ticket.number % 1000 == self.winning_number.number % 1000:
            return ("4等", self.PRIZE_4TH)

        # 5等：下2桁一致
        if ticket.number % 100 == self.winning_number.number % 100:
            return ("5等", self.PRIZE_5TH)

        # 6等：下1桁一致
        if ticket.number % 10 == self.winning_number.number % 10:
            return ("6等", self.PRIZE_6TH)

        # 7等：指定された下1桁と一致
        if ticket.number % 10 == self.bonus_digit:
            return ("7等", self.PRIZE_7TH)

        return ("なし", 0)

    def check_all_prizes(self) -> Dict:
        """
        すべてのくじの当せんを判定

        Returns:
            結果の辞書
        """
        renban_results = {"1等": 0, "1等前後賞": 0, "2等": 0, "3等": 0,
                         "4等": 0, "5等": 0, "6等": 0, "7等": 0}
        bara_results = {"1等": 0, "1等前後賞": 0, "2等": 0, "3等": 0,
                       "4等": 0, "5等": 0, "6等": 0, "7等": 0}

        renban_total_prize = 0
        bara_total_prize = 0

        # 連番の当せん判定
        for ticket in self.renban_tickets:
            prize_name, prize_amount = self.check_prize(ticket)
            if prize_name != "なし":
                renban_results[prize_name] += 1
                renban_total_prize += prize_amount

        # バラの当せん判定
        for ticket in self.bara_tickets:
            prize_name, prize_amount = self.check_prize(ticket)
            if prize_name != "なし":
                bara_results[prize_name] += 1
                bara_total_prize += prize_amount

        # 購入金額と収支を計算
        renban_sets = len(self.renban_tickets) // self.TICKETS_PER_SET
        bara_sets = len(self.bara_tickets) // self.TICKETS_PER_SET
        total_cost = (renban_sets + bara_sets) * self.PRICE_PER_SET
        total_prize = renban_total_prize + bara_total_prize
        profit = total_prize - total_cost

        return {
            "renban_results": renban_results,
            "renban_total_prize": renban_total_prize,
            "bara_results": bara_results,
            "bara_total_prize": bara_total_prize,
            "renban_sets": renban_sets,
            "bara_sets": bara_sets,
            "total_sets": renban_sets + bara_sets,
            "total_cost": total_cost,
            "total_prize": total_prize,
            "profit": profit
        }

    def display_results(self, results: Dict):
        """
        結果を表示

        Args:
            results: check_all_prizes()の戻り値
        """
        print("=" * 60)
        print("宝くじシミュレーション結果")
        print("=" * 60)
        print()

        # 抽選番号表示
        print(f"【1等当せん番号】: {self.winning_number}")
        print(f"【7等該当下1桁】: {self.bonus_digit}")
        print()

        # 連番の結果
        print("【連番】")
        renban_has_prize = False
        for prize_name in ["1等", "1等前後賞", "2等", "3等", "4等", "5等", "6等", "7等"]:
            count = results["renban_results"][prize_name]
            if count > 0:
                renban_has_prize = True
                prize_amount = self._get_prize_amount(prize_name)
                print(f"  {prize_name}: {count}枚 ({prize_amount:,}円 × {count} = {prize_amount * count:,}円)")

        if not renban_has_prize:
            print("  当せんなし")

        print(f"  獲得賞金合計: {results['renban_total_prize']:,}円")
        print()

        # バラの結果
        print("【バラ】")
        bara_has_prize = False
        for prize_name in ["1等", "1等前後賞", "2等", "3等", "4等", "5等", "6等", "7等"]:
            count = results["bara_results"][prize_name]
            if count > 0:
                bara_has_prize = True
                prize_amount = self._get_prize_amount(prize_name)
                print(f"  {prize_name}: {count}枚 ({prize_amount:,}円 × {count} = {prize_amount * count:,}円)")

        if not bara_has_prize:
            print("  当せんなし")

        print(f"  獲得賞金合計: {results['bara_total_prize']:,}円")
        print()

        # 全体サマリー
        print("【全体】")
        print(f"  総購入セット数: {results['total_sets']}セット")
        print(f"    - 連番: {results['renban_sets']}セット")
        print(f"    - バラ: {results['bara_sets']}セット")
        print(f"  総購入金額: {results['total_cost']:,}円")
        print(f"  総当せん金額: {results['total_prize']:,}円")

        profit_sign = "+" if results['profit'] >= 0 else ""
        print(f"  収支: {profit_sign}{results['profit']:,}円")
        print()
        print("=" * 60)

    def _get_prize_amount(self, prize_name: str) -> int:
        """等級名から賞金額を取得"""
        prize_map = {
            "1等": self.PRIZE_1ST,
            "1等前後賞": self.PRIZE_1ST_ADJACENT,
            "2等": self.PRIZE_2ND,
            "3等": self.PRIZE_3RD,
            "4等": self.PRIZE_4TH,
            "5等": self.PRIZE_5TH,
            "6等": self.PRIZE_6TH,
            "7等": self.PRIZE_7TH
        }
        return prize_map.get(prize_name, 0)


def main():
    """メイン実行関数"""
    print("=" * 60)
    print("宝くじシミュレーター")
    print("=" * 60)
    print()

    # ユーザー入力
    try:
        renban_sets = int(input("連番セット数を入力してください（0以上の整数）: "))
        bara_sets = int(input("バラセット数を入力してください（0以上の整数）: "))

        # シミュレーター初期化
        simulator = LotterySimulator()

        # くじ購入
        simulator.purchase_tickets(renban_sets, bara_sets)

        # 抽選実行
        simulator.draw_winning_number()

        # 当せん判定
        results = simulator.check_all_prizes()

        # 結果表示
        print()
        simulator.display_results(results)

    except ValueError as e:
        print(f"エラー: {e}")
    except KeyboardInterrupt:
        print("\n中断されました")


if __name__ == "__main__":
    main()
