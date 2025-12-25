#!/usr/bin/env python3
"""
宝くじシミュレーターのテストコード
"""

from lottery_simulator import LotterySimulator, Lottery


def test_renban_generation():
    """連番セット生成のテスト"""
    print("=" * 60)
    print("連番セット生成テスト")
    print("=" * 60)

    sim = LotterySimulator(seed=42)
    renban_set = sim.generate_renban_set()

    print(f"生成された連番セット（{len(renban_set)}枚）:")
    for i, ticket in enumerate(renban_set):
        print(f"  {i+1}. {ticket}")

    # 検証：すべて同じ組
    groups = [ticket.group for ticket in renban_set]
    assert len(set(groups)) == 1, "連番セットは同一組である必要があります"
    print(f"✓ すべて同じ組: {groups[0]}")

    # 検証：番号が連続している
    numbers = [ticket.number for ticket in renban_set]
    for i in range(1, len(numbers)):
        assert numbers[i] == numbers[i-1] + 1, "番号は連続している必要があります"
    print(f"✓ 番号が連続: {numbers[0]} ～ {numbers[-1]}")

    print()


def test_bara_generation():
    """バラセット生成のテスト"""
    print("=" * 60)
    print("バラセット生成テスト")
    print("=" * 60)

    sim = LotterySimulator(seed=42)
    bara_set = sim.generate_bara_set()

    print(f"生成されたバラセット（{len(bara_set)}枚）:")
    for i, ticket in enumerate(bara_set):
        print(f"  {i+1}. {ticket}")

    # 検証：すべて異なる組
    groups = [ticket.group for ticket in bara_set]
    assert len(set(groups)) == len(bara_set), "バラセットはすべて異なる組である必要があります"
    print(f"✓ すべて異なる組: {sorted(groups)}")

    # 検証：下1桁が0-9すべて含まれている
    last_digits = [ticket.number % 10 for ticket in bara_set]
    assert set(last_digits) == set(range(10)), "下1桁は0-9すべて含まれる必要があります"
    print(f"✓ 下1桁が0-9すべて含まれる: {sorted(last_digits)}")

    # 検証：番号が連続していない（少なくとも1つ以上の非連続があるべき）
    numbers = sorted([ticket.number for ticket in bara_set])
    consecutive = all(numbers[i] == numbers[i-1] + 1 for i in range(1, len(numbers)))
    assert not consecutive, "バラセットの番号は連続してはいけません"
    print(f"✓ 番号が連続していない")

    print()


def test_prize_checking():
    """当せん判定のテスト"""
    print("=" * 60)
    print("当せん判定テスト")
    print("=" * 60)

    sim = LotterySimulator(seed=42)
    sim.winning_number = Lottery(100, 12345)
    sim.bonus_digit = 7  # 1等の下1桁（5）と異なる値

    print(f"1等当せん番号: {sim.winning_number}")
    print(f"7等該当下1桁: {sim.bonus_digit}")
    print()

    test_cases = [
        (Lottery(100, 12345), "1等"),  # 完全一致
        (Lottery(100, 12344), "1等前後賞"),  # 前後賞（-1）
        (Lottery(100, 12346), "1等前後賞"),  # 前後賞（+1）
        (Lottery(100, 2345), "2等"),  # 組一致+下4桁一致
        (Lottery(50, 2345), "3等"),  # 下4桁一致
        (Lottery(50, 345), "4等"),  # 下3桁一致
        (Lottery(50, 45), "5等"),  # 下2桁一致
        (Lottery(50, 5), "6等"),  # 下1桁一致（1等の下1桁と同じ）
        (Lottery(50, 15), "6等"),  # 下1桁一致（1等の下1桁と同じ）
        (Lottery(50, 97), "7等"),  # 7等（bonus_digit=7、1等の下1桁とは異なる）
        (Lottery(50, 123), "なし"),  # 当せんなし
    ]

    for ticket, expected_prize in test_cases:
        prize_name, prize_amount = sim.check_prize(ticket)
        status = "✓" if prize_name == expected_prize else "✗"
        print(f"{status} {ticket} → {prize_name} (期待値: {expected_prize})")
        if prize_amount > 0:
            print(f"   賞金: {prize_amount:,}円")

    print()


def test_edge_cases():
    """エッジケースのテスト"""
    print("=" * 60)
    print("エッジケーステスト")
    print("=" * 60)

    sim = LotterySimulator(seed=42)

    # 00000の前後賞テスト
    sim.winning_number = Lottery(100, 0)
    sim.bonus_digit = 0

    print(f"1等当せん番号: {sim.winning_number}")

    # -1は存在しないので前後賞にならない
    prize_name, _ = sim.check_prize(Lottery(100, -1))  # これは実際には存在しない
    print(f"  {Lottery(100, -1)} → {prize_name} (番号が範囲外)")

    # +1は前後賞
    prize_name, _ = sim.check_prize(Lottery(100, 1))
    expected = "1等前後賞"
    status = "✓" if prize_name == expected else "✗"
    print(f"{status} {Lottery(100, 1)} → {prize_name} (期待値: {expected})")

    # 99999の前後賞テスト
    sim.winning_number = Lottery(100, 99999)

    print(f"1等当せん番号: {sim.winning_number}")

    # -1は前後賞
    prize_name, _ = sim.check_prize(Lottery(100, 99998))
    expected = "1等前後賞"
    status = "✓" if prize_name == expected else "✗"
    print(f"{status} {Lottery(100, 99998)} → {prize_name} (期待値: {expected})")

    # +1は範囲外なので前後賞にならない
    prize_name, _ = sim.check_prize(Lottery(100, 100000))
    print(f"  {Lottery(100, 100000)} → {prize_name} (番号が範囲外)")

    print()


def test_simulation():
    """シミュレーション全体のテスト"""
    print("=" * 60)
    print("シミュレーション全体テスト")
    print("=" * 60)

    sim = LotterySimulator(seed=123)

    # くじ購入
    renban_sets = 3
    bara_sets = 2
    sim.purchase_tickets(renban_sets, bara_sets)

    print(f"購入したくじ:")
    print(f"  連番: {renban_sets}セット ({len(sim.renban_tickets)}枚)")
    print(f"  バラ: {bara_sets}セット ({len(sim.bara_tickets)}枚)")
    print()

    # 抽選
    sim.draw_winning_number()

    # 結果判定と表示
    results = sim.check_all_prizes()
    sim.display_results(results)


def test_max_sets():
    """最大セット数のテスト"""
    print("=" * 60)
    print("最大セット数テスト")
    print("=" * 60)

    sim = LotterySimulator(seed=42)

    # 33セット（上限）
    try:
        sim.purchase_tickets(20, 13)
        print("✓ 33セット（上限）の購入に成功")
    except ValueError as e:
        print(f"✗ エラー: {e}")

    # 34セット（上限超過）
    try:
        sim.purchase_tickets(20, 14)
        print("✗ 34セット（上限超過）の購入が許可されました（エラーが必要）")
    except ValueError as e:
        print(f"✓ 正しくエラーが発生: {e}")

    print()


def main():
    """テスト実行"""
    test_renban_generation()
    test_bara_generation()
    test_prize_checking()
    test_edge_cases()
    test_max_sets()
    test_simulation()

    print("=" * 60)
    print("すべてのテストが完了しました")
    print("=" * 60)


if __name__ == "__main__":
    main()
