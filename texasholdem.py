from collections import Counter
from itertools import combinations

def parse_hand(hand):
    ranks = []
    suits = []
    for card in hand:

        rank_str = card[:-1]  # 最後一個是花色
        suit = card[-1]       # 取花色

        if rank_str == 'A':
            rank = 14
        elif rank_str == 'K':
            rank = 13
        elif rank_str == 'Q':
            rank = 12
        elif rank_str == 'J':
            rank = 11
        elif rank_str == 'T':
            rank = 10
        else:
            #try:
            rank = int(rank_str)  # 2~9

        ranks.append(rank)
        suits.append(suit)
    return ranks, suits


def royal_flush(hand): # 是10到A的同花順
    ranks, suits = parse_hand(hand)
    return set(ranks) == set([10, 11, 12, 13, 14]) and flush(hand)

def straight_flush(hand): # 是同花且是順子
    return straight(hand) and flush(hand)

def four_kind(hand): # 有某個點數出現四次
    ranks, _ = parse_hand(hand)
    counter = Counter(ranks)
    return 4 in counter.values() # 有出現次數的值是4

def full_house(hand): # 同時有三張一樣和兩張一樣的牌
    ranks, _ = parse_hand(hand) # 取得數字
    counter = Counter(ranks) # 計算數字出現次數
    values = counter.values() # 取得出現次數的值
    return 3 in values and 2 in values # 如果是3和2就回傳true

def flush(hand): # 花色都一樣
    _, suits = parse_hand(hand) # 取得花色
    return len(set(suits)) == 1 # set() 自動去除重複元素

def straight(hand): #連續5張牌
    ranks, _ = parse_hand(hand)
    ranks = sorted(set(ranks)) # 去除重複元素後排序
    if len(ranks) < 5:
        return False
    for i in range(len(ranks) - 4):
        if ranks[i+4] - ranks[i] == 4:
            return True
    return set([14, 2, 3, 4, 5]).issubset(ranks)

def three_kind(hand): #有某個點數出現三次（葫蘆的一部分或是三條）
    ranks, _ = parse_hand(hand)
    counter = Counter(ranks)
    return 3 in counter.values() #有出現次數的值是3

def two_pairs(hand): #有兩個不同的點數都出現了兩次（兩對）
    ranks, _ = parse_hand(hand)
    counter = Counter(ranks)
    return list(counter.values()).count(2) == 2 #出現次數的值是2的出現了兩次

def one_pair(hand): #如果有任何點數出現了2次 代表是一對
    ranks, _ = parse_hand(hand)
    counter = Counter(ranks)
    return 2 in counter.values() #有出現次數的值是2

def high_card(hand): #什麼都不是
    return True

def card_power(hand): # 檢定牌力
    card_types = [royal_flush, straight_flush, four_kind, full_house, flush,
                  straight, three_kind, two_pairs, one_pair, high_card]
    for i in range(10):
        if card_types[i](hand):
            return i
    return 10

def hand_rank(player_cards, community_cards):
    all_cards = player_cards + community_cards
    if len(all_cards) < 2:  # 至少需要2張牌才能判斷
        return 9, "High Card"
    
    best_score = 9  # 分數越小越強
    best_hand_type = "High Card" #先預設是high card

    if royal_flush(all_cards):
        return 0, "Royal Flush"
    elif straight_flush(all_cards):
        return 1, "Straight Flush"
    elif four_kind(all_cards):
        return 2, "Four of a Kind"
    elif full_house(all_cards) and len(all_cards) >= 5:  #Full House 需要5張牌
        return 3, "Full House"
    elif flush(all_cards) and len(all_cards) >= 5:  #Flush 需要5張牌
        return 4, "Flush"
    elif straight(all_cards) and len(all_cards) >= 5:  #Straight 需要5張牌
        return 5, "Straight"
    elif three_kind(all_cards):
        return 6, "Three of a Kind"
    elif two_pairs(all_cards):
        return 7, "Two Pairs"
    elif one_pair(all_cards):
        return 8, "One Pair"
    
    # 如果有5張或以上的牌，檢查是否有更好的牌型組合
    if len(all_cards) >= 5:
        for combo in combinations(all_cards, 5):
            score = card_power(combo)
            if score < best_score:
                best_score = score
                best_hand_type = card_type(combo)

    return best_score, best_hand_type

def card_type(hand):
    types = [
        royal_flush, straight_flush, four_kind, full_house, flush,
        straight, three_kind, two_pairs, one_pair, high_card
    ]
    names = [
        "Royal Flush", "Straight Flush", "Four of a Kind", "Full House", "Flush",
        "Straight", "Three of a Kind", "Two Pairs", "One Pair", "High Card"
    ]
    for i, func in enumerate(types):
        if func(hand):
            return names[i]
