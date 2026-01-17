'''
Simple example pokerbot, written in Python.
'''
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction, DiscardAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot

import random
def deck_helper(d,s):
    complete_deck=d.copy()
    for num in range(0,len(complete_deck)):
        complete_deck[num]=complete_deck[num]+s
    return complete_deck

def possible_cards(hand, board):
    deckbase=["2","3","4","5","6","7","8","9","T","Q","K","A"]
    deck=[]
    deck.extend(deck_helper(deckbase,"h"))
    deck.extend(deck_helper(deckbase,"d"))
    deck.extend(deck_helper(deckbase,"s"))
    deck.extend(deck_helper(deckbase,"c"))
    tru_hand=hand.copy()
    tru_hand.extend(board)
    for card in tru_hand:
        if card in deck:
            deck.remove(card)
    return deck

def get_value(hand, board):
    tru_hand=hand.copy()
    tru_hand.extend(board)
    values=[]
    for card1 in tru_hand:
        rem_cards=tru_hand.copy()
        rem_cards.remove(card1)
        a1=card1[0]
        b1=card1[1]
        if "T"==a1:
            a1=10
        elif "J"==a1:
            a1=11
        elif "Q"==a1:
            a1=12
        elif "K"==a1:
            a1=13
        elif "A"==a1:
            a1=14
        a1=int(a1)
        zeroes=0
        ones=0
        val=0
        for card2 in rem_cards:
            a2=card2[0]
            b2=card2[1]
            
            if b1==b2:
                val+=2
            if "T"==a2:
                a2=10
            elif "J"==a2:
                a2=11
            elif "Q"==a2:
                a2=12
            elif "K"==a2:
                a2=13
            elif "A"==a2:
                a2=14
            a2=int(a2)
            diff=abs(a2-a1)
            if diff <=1:
                val+=20
                if diff==0:
                    if zeroes>0:
                        val+=20*zeroes
                    zeroes+=1
                else:
                    if ones>0:
                        val+=20*ones
                    ones+=1
            else:
                val-=diff

        values.append(val)
    return values

def get_future(hand, table):
    pos=possible_cards(hand,table)
    megalist=[]
    for card in pos:
        megalist.append(get_value(hand.copy()+[card],table))
    return sum_it_all(megalist), len(pos)

def get_future_norm(hand, board):
    future_sum,count=get_future(hand,board)
    if count==0:
        return 0
    raw = future_sum/count
    n = len(hand) + len(board) + 1
    max_score = 25*n*(n-1)
    return raw/max_score

def get_value_norm(hand, board):
    raw=sum(get_value(hand,board))
    n=len(hand)+len(board)
    max_score=25*n*(n-1)
    if max_score==0:
        return 0
    return raw/max_score  

def sum_it_all(megalist):
    minilist=[]
    for list in megalist:
        minilist.append(sum(list))
    return sum(minilist)
class Player(Bot):
    '''
    A pokerbot.
    '''

    def __init__(self):
        '''
        Called when a new game starts. Called exactly once.

        Arguments:
        Nothing.

        Returns:
        Nothing.
        '''
        pass

    def handle_new_round(self, game_state, round_state, active):
        '''
        Called when a new round starts. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Nothing.
        ''' 
        my_bankroll = game_state.bankroll  # the total number of chips you've gained or lost from the beginning of the game to the start of this round
        # the total number of seconds your bot has left to play this game
        game_clock = game_state.game_clock
        round_num = game_state.round_num  # the round number from 1 to NUM_ROUNDS
        my_cards = round_state.hands[active]  # your cards
        big_blind = bool(active)  # True if you are the big blind
        pass

    def handle_round_over(self, game_state, terminal_state, active):
        '''
        Called when a round ends. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        terminal_state: the TerminalState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        my_delta = terminal_state.deltas[active]  # your bankroll change from this round
        previous_state = terminal_state.previous_state  # RoundState before payoffs
        street = previous_state.street  # 0,2,3,4,5,6 representing when this round ended
        my_cards = previous_state.hands[active]  # your cards
        # opponent's cards or [] if not revealed
        opp_cards = previous_state.hands[1-active]
        pass

    def get_action_default(self, game_state, round_state, active):
        '''
        Where the magic happens - your code should implement this function.
        Called any time the engine needs an action from your bot.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Your action.
        '''
        legal_actions = round_state.legal_actions()  # the actions you are allowed to take
        # 0, 3, 4, or 5 representing pre-flop, flop, turn, or river respectively
        street = round_state.street
        my_cards = round_state.hands[active]  # your cards
        board_cards = round_state.board  # the board cards
        # the number of chips you have contributed to the pot this round of betting
        my_pip = round_state.pips[active]
        # the number of chips your opponent has contributed to the pot this round of betting
        opp_pip = round_state.pips[1-active]
        # the number of chips you have remaining
        my_stack = round_state.stacks[active]
        # the number of chips your opponent has remaining
        opp_stack = round_state.stacks[1-active]
        continue_cost = opp_pip - my_pip  # the number of chips needed to stay in the pot
        # the number of chips you have contributed to the pot
        my_contribution = STARTING_STACK - my_stack
        # the number of chips your opponent has contributed to the pot
        opp_contribution = STARTING_STACK - opp_stack

        # Only use DiscardAction if it's in legal_actions (which already checks street)
        # legal_actions() returns DiscardAction only when street is 2 or 3
        if DiscardAction in legal_actions:
            # Always discards the first card in the bot's hand
            return DiscardAction(0)
        if RaiseAction in legal_actions:
            # the smallest and largest numbers of chips for a legal bet/raise
            min_raise, max_raise = round_state.raise_bounds()
            min_cost = min_raise - my_pip  # the cost of a minimum bet/raise
            max_cost = max_raise - my_pip  # the cost of a maximum bet/raise
            if random.random() < 0.5:
                return RaiseAction(min_raise)
        if CheckAction in legal_actions:  # check-call
            return CheckAction()
        if random.random() < 0.5:
            return FoldAction()
        return CallAction()
    



    def get_action_old(self, game_state, round_state, active):
        '''
        Where the magic happens - your code should implement this function.
        Called any time the engine needs an action from your bot.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Your action.
        '''
        legal_actions = round_state.legal_actions()  # the actions you are allowed to take
        # 0, 3, 4, or 5 representing pre-flop, flop, turn, or river respectively
        street = round_state.street
        my_cards = round_state.hands[active]  # your cards
        board_cards = round_state.board  # the board cards
        # the number of chips you have contributed to the pot this round of betting
        my_pip = round_state.pips[active]
        # the number of chips your opponent has contributed to the pot this round of betting
        opp_pip = round_state.pips[1-active]
        # the number of chips you have remaining
        my_stack = round_state.stacks[active]
        # the number of chips your opponent has remaining
        opp_stack = round_state.stacks[1-active]
        continue_cost = opp_pip - my_pip  # the number of chips needed to stay in the pot
        # the number of chips you have contributed to the pot
        my_contribution = STARTING_STACK - my_stack
        # the number of chips your opponent has contributed to the pot
        opp_contribution = STARTING_STACK - opp_stack

        if DiscardAction in legal_actions:
            v0=get_value(my_cards[1:3],[])
            v1=get_value([my_cards[0],my_cards[2]],[])
            v2=get_value(my_cards[0:2],[])
            pothandval=[sum(v0),sum(v1),sum(v2)]
            ind=pothandval.index(max(pothandval))
            return DiscardAction(ind)
        cur=get_value(my_cards,board_cards)
        fut=get_future(my_cards,board_cards)
        fut=fut[0]/fut[1]
        if fut<0 and continue_cost>0:
            return FoldAction
        if fut/cur<=1.1 and continue_cost>0:
            return FoldAction
        if fut/cur<=1.3 and CheckAction in legal_actions:
            return CheckAction
        if fut/cur<=1.4 and CallAction in legal_actions:
            return CallAction
        if fut/cur>=1.3:
            min_raise, max_raise = round_state.raise_bounds()
            amount = int((fut/cur)**0.7 * my_contribution)
            amount = max(min_raise, min(amount, max_raise))
            return RaiseAction(amount)
        return FoldAction
    
    def get_action(self, game_state, round_state, active):
        '''
        Where the magic happens - your code should implement this function.
        Called any time the engine needs an action from your bot.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Your action.
        '''
        legal_actions = round_state.legal_actions()  # the actions you are allowed to take
        # 0, 3, 4, or 5 representing pre-flop, flop, turn, or river respectively
        street = round_state.street
        my_cards = round_state.hands[active]  # your cards
        board_cards = round_state.board  # the board cards
        # the number of chips you have contributed to the pot this round of betting
        my_pip = round_state.pips[active]
        # the number of chips your opponent has contributed to the pot this round of betting
        opp_pip = round_state.pips[1-active]
        # the number of chips you have remaining
        my_stack = round_state.stacks[active]
        # the number of chips your opponent has remaining
        opp_stack = round_state.stacks[1-active]
        continue_cost = opp_pip - my_pip  # the number of chips needed to stay in the pot
        # the number of chips you have contributed to the pot
        my_contribution = STARTING_STACK - my_stack
        # the number of chips your opponent has contributed to the pot
        opp_contribution = STARTING_STACK - opp_stack
        if DiscardAction in legal_actions:
            v0=get_value(my_cards[1:3],[])
            v1=get_value([my_cards[0],my_cards[2]],[])
            v2=get_value(my_cards[0:2],[])
            pothandval=[sum(v0),sum(v1),sum(v2)]
            ind=pothandval.index(max(pothandval))
            return DiscardAction(ind)
        cur=get_value_norm(my_cards, board_cards)
        fut=get_future_norm(my_cards, board_cards)
        delta=fut-cur

        if delta<-0.01 and FoldAction in legal_actions and continue_cost>0:
            return FoldAction()
        if delta<0.03 and CheckAction in legal_actions:
            return CheckAction()
        if delta<0.05 and CallAction in legal_actions:
            return CallAction()
        if RaiseAction in legal_actions:
            min_raise,max_raise=round_state.raise_bounds()
            aggression=min(1.0, max(0.0,delta/0.12))
            amount=int(min_raise+aggression*(max_raise-min_raise))
            return RaiseAction(amount)

        return CheckAction() if CheckAction in legal_actions else FoldAction()


        




if __name__ == '__main__':
    run_bot(Player(), parse_args())
