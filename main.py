from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from mytoken import token
import random
import texasholdem

# 初始設定
SUITS = ['♠', '♥', '♦', '♣']
RANK = list('23456789TJQKA')

money = [100, 100, 100, 100]
status = ["None", "None", "None", "None"]
rnd = 0
stage = 0
community = []
bet = [0, 0, 0, 0]
hand = ["", "", "", ""]

# 重制新遊戲
def reset(): # reset game
    global money, status, rnd, stage, community, bet, hand
    money = [100, 100, 100, 100]
    status = ["None", "None", "None", "None"]
    rnd, stage = 0, 0
    community = []
    bet = [0, 0, 0, 0]
    hand = ["", "", "", ""]

# 版面定義
def board():
    stage_name = {
        0: "等待發牌",
        1: "PREFLOP",
        2: "FLOP",
        3: "TURN",
        4: "RIVER",
        5: "SHOWDOWN"
    }
    readable_stage = stage_name.get(stage, "未知階段") #找出stage對應名稱
    community_str = " ".join(str(card) for card in community) if community else "" #把公共排轉成字串格式
    return f'''Round: {rnd} | Stage: {readable_stage} 

Community: {community_str}

Computer 1: {status[0]} | Bet: {bet[0]} | Money: {money[0]}
Computer 2: {status[1]} | Bet: {bet[1]} | Money: {money[1]}
Computer 3: {status[2]} | Bet: {bet[2]} | Money: {money[2]}

Hand: {hand[-1]} | Status: {status[-1]} | Bet: {bet[-1]} Money: {money[-1]}
'''

#初始新一輪遊戲
def round_init():
    global deck, hand, status, community, bet, stage
    suits = SUITS
    ranks = RANK
    deck = [r + s for s in suits for r in ranks]
    random.shuffle(deck)

    hand = ["", "", "", ""]
    for i in range(4):
        hand[i] = deck.pop() + deck.pop()
    
    community = []
    status = ["None", "None", "None", "None"]
    bet = [0] * 4
    stage = 1  # 從Preflop(1)開始
    do_ai_action(stage)

# 按鈕選項設定
def get_player_buttons():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton('All in', callback_data='a'),
        InlineKeyboardButton('Bet', callback_data='b'),
        InlineKeyboardButton('Fold', callback_data='f')
    ]])
def get_pass_button():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton('Pass', callback_data='p')
    ]])

async def start(update, context):
    reset() # Reset game
    await update.message.reply_text("Game starts! Every player has $100. Send /deal to start a round.")

async def deal(update, context):
    global rnd, stage
    if stage > 0: return # Do nothing if a round has been started
    round_init()
    rnd += 1
    await update.message.reply_text(board(), reply_markup=get_player_buttons())

async def play_stage(update, context):
    global stage, community, deck

    try:
        if stage == 2:  # Flop
            if len(deck) < 3:
                await update.callback_query.message.reply_text("錯誤：牌堆不足以發Flop")
                return
            for _ in range(3):
                community.append(deck.pop())
            do_ai_action(stage)
        elif stage == 3:  # Turn
            if len(deck) < 1:
                await update.callback_query.message.reply_text("錯誤：牌堆不足以發Turn")
                return
            community.append(deck.pop())
            do_ai_action(stage)
        elif stage == 4:  # River
            if len(deck) < 1:
                await update.callback_query.message.reply_text("錯誤：牌堆不足以發River")
                return
            community.append(deck.pop())
            do_ai_action(stage)
        elif stage == 5:  # Showdown
            await do_showdown(update, context)
            stage = 0
            return
        
        # 更新遊戲狀態顯示
        new_text = board()
        try:
            old_text = update.callback_query.message.text
        except AttributeError:
            old_text = ""

        if status[3] in ['FOLD', 'ALL IN']:
                reply_markup = get_pass_button()
        else:
            reply_markup = get_player_buttons()
            
        if new_text != old_text:
            await context.bot.edit_message_text(
                text=new_text,
                chat_id=update.callback_query.message.chat_id,
                message_id=update.callback_query.message.message_id,
                reply_markup=reply_markup
)
    except Exception as e:
        await update.callback_query.message.reply_text(f"發生錯誤：{str(e)}")
        print(f"錯誤詳情：{e}")
        # 發生錯誤時，印出當前狀態以便除錯
        print(f"Current stage: {stage}")
        print(f"Community cards: {community}")
        print(f"Deck size: {len(deck) if 'deck' in globals() else 'deck not initialized'}")

# 3台電腦操作
def do_ai_action(stage):
    for i in range(3):  # AI 0, 1, 2
        if stage == 1:  # Preflop：都BET
            bet[i] += 1
            money[i] -= 1
            status[i] = "BET"
        elif stage == 2:  # Flop
            # 將手牌字串轉換為列表
            player_cards = [hand[i][0:2], hand[i][2:4]]  # 每張牌佔2個字符
            score, hand_type = texasholdem.hand_rank(player_cards, community)
            if i == 0: # 電腦1
                bet[i] += 1
                money[i] -= 1
                status[i] = "BET"
            elif i == 1:  # 電腦2
                if score == 9:  # High card
                    status[i] = "FOLD"
                else:
                    bet[i] += 1
                    money[i] -= 1
                    status[i] = "BET"
            elif i == 2:  # 電腦3
                if score >= 7:  # Two Pair
                    status[i] = "FOLD"
                else:
                    bet[i] += money[i]
                    money[i] = 0
                    status[i] = "ALL IN"
        elif stage in [3, 4]:  # Turn & River
            player_cards = [hand[i][0:2], hand[i][2:4]]  # 每張牌佔2個字符
            score, hand_type = texasholdem.hand_rank(player_cards, community)
            if i == 0: # 電腦1
                bet[i] += 1
                money[i] -= 1
                status[i] = "BET"
            if i == 1 and status[i] == "BET":  # 電腦2 (上輪不得all in或fold)
                if score <= 3:  # Full House 或以上
                    bet[i] += money[i]
                    money[i] = 0
                    status[i] = "All in"
                else:
                    bet[i] += 1
                    money[i] -= 1
                    status[i] = "BET"
        
        # 輸出除錯資訊
        print(f"AI {i+1} hand: {hand[i]}")
        print(f"Stage: {stage}")
        if community:
            community_str = " ".join(str(card) for card in community)
            print(f"Community: {community_str}")
            print(f"Hand type: {hand_type}")
        else:
            print("Community: (尚未發牌)")

#結果顯示
async def do_showdown(update, context):
    global money

    scores = []
    for i in range(4):
        player_cards = [hand[i][0:2], hand[i][2:4]]  # 每張牌佔2個字符
        scores.append((texasholdem.hand_rank(player_cards, community)[0], i))

    scores.sort() # 分數由低到高排序
    max_score = scores[0][0]
    winners = [i for s, i in scores if s == max_score]

    pot = sum(bet)
    share = pot // len(winners)

    # 顯示所有玩家牌組與勝者
    community_str = " ".join(str(card) for card in community)
    result = f"Round: {rnd}\n\nCommunity: {community_str}\n\n"

    player_info = []
    for i in range(4):
        player_name = 'You' if i == 3 else f'Computer {i+1}'
        player_cards = [hand[i][0:2], hand[i][2:4]]  # 每張牌佔2個字符
        score, hand_type = texasholdem.hand_rank(player_cards, community)

        player_info.append((score, player_name, hand[i], hand_type, bet[i], money[i]))
        player_info.sort()

    # 依序列印排序後的玩家資訊
    for score, name, cards, hand_type, b, m in player_info:
        result += f"{name}: {cards} [{hand_type}] | Bet: {b} | Money: {m}\n"

    result += f"\nPot: ${pot}"
    if len(winners)==1:
        result += f"\nWinner: {', '.join(['You' if w==3 else f'Computer {w+1}' for w in winners])} wins the pot of ${share}!"
    else:
        result += f"\nTie: {', '.join(['You' if w==3 else f'Computer {w+1}' for w in winners])} each win ${share}!"

    for w in winners:
        money[w] += share

    if any(m >= 250 for m in money) or any(m <= 0 for m in money):
        result += f"\n\nGame over! Send /start to start a new game."
    else:
        result += f"\n\nSend /deal to start the next round."
    
    await context.bot.edit_message_text(
        text=result,
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id
    )

#按鈕操作
async def action(update, context):
    global status, bet, money, stage

    query = update.callback_query
    await query.answer()

    choice = query.data
    if choice == 'a':
        bet[3] += money[3]
        money[3] = 0
        status[3] = "ALL IN"
    elif choice == 'b':
        bet[3] += 1
        money[3] -= 1
        status[3] = "BET"
    elif choice == 'f':
        status[3] = "FOLD"

    stage += 1

    await play_stage(update, context)


def main():
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(token).build()

    # Start / Restart games
    application.add_handler(CommandHandler("start", start))

    # Start a round
    application.add_handler(CommandHandler("deal", deal))

    # Process the button press to advance stages
    application.add_handler(CallbackQueryHandler(action))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
