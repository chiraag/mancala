import numpy as np
import re

class Board():
    def __init__(self, board_sz=6, init_seeds=4):
        self.player = 0
        self.status = "In Progress" # "Player 1 wins", "Player 2 wins", "Draw"
        self.board_sz = board_sz
        self.mancala = [self.board_sz, 2*self.board_sz+1]

        self.state = np.zeros(2*(self.board_sz+1))
        self.state[:self.board_sz] = init_seeds
        self.state[self.board_sz+1:-1] = init_seeds

    def check(self, move):
        bounds_pass = (0 <= move[0] < self.board_sz)
        curr_base = self.player*(self.board_sz+1)
        curr_stones = self.state[curr_base + move[0]]
        return bounds_pass and (curr_stones != 0)

    def update(self, move):
        curr_base = self.player*(self.board_sz+1)
        opp_base = (1-self.player)*(self.board_sz+1)
        curr_m, opp_m = (curr_base + self.board_sz, opp_base + self.board_sz)

        idx = curr_base + move[0]
        curr_stones = self.state[idx]

        self.state[idx] = 0
        while curr_stones > 0:
            idx = (idx + 1) % self.state.size
            if ((idx == opp_m) or (move[1] and idx == curr_m)):
                continue
            else:
                self.state[idx] += 1
                curr_stones -= 1
                # print(idx, self.state[idx])

        if idx == opp_m:
            assert False, "Impossible to end move on opposite mancala"

        if idx != curr_m:
            # Resolve the steal interaction
            if self.state[idx] == 1:
                delta = self.board_sz - (idx % (self.board_sz + 1))
                opp_idx = (idx + 2*delta) % self.state.size
                # print(delta, opp_idx)
                self.state[curr_m] += self.state[opp_idx]
                self.state[opp_idx] = 0
            self.player = (1 - self.player)

        if np.sum(self.state[curr_base:curr_m]) == 0 or np.sum(self.state[opp_base:opp_m]) == 0:
            if self.state[self.mancala[0]] > self.state[self.mancala[1]]:
                self.status = "Player 1 wins"
            elif self.state[self.mancala[0]] < self.state[self.mancala[1]]:
                self.status = "Player 2 wins"
            else:
                self.status = "Draw"

    def __str__(self):
        c_end = "\033[0m"
        c_red = "\033[31m"
        c_green = "\033[32m"
        c_blue = "\033[94m"
        c_gray = "\033[96m"

        space = " "*2
        top_marker = c_blue+" >"+c_end if self.player == 0 else space
        bot_marker = c_blue+" <"+c_end if self.player == 1 else space
        hint_top = c_gray+" ".join([space] + ["%2d" % x for x in range(self.board_sz)] + [space])+c_end
        hint_bot = c_gray+" ".join([space] + ["%2d" % x for x in range(self.board_sz)][::-1] + [space])+c_end
        line_top = " ".join(
            [top_marker] + 
            ["%2d" % x for x in self.state[:self.board_sz]] +
            ["%s%2d%s" % (c_red, self.state[self.board_sz], c_end)]
        )
        line_bot = " ".join(
            ["%s%2d%s" % (c_green, self.state[2*self.board_sz+1], c_end)] +
            ["%2d" % x for x in self.state[self.board_sz+1:2*self.board_sz+1][::-1]] + 
            [bot_marker]
        )
        # line_status = "next player: %d" % (self.player, )
        return "\n".join([hint_top, line_top, line_bot, hint_bot])

class HumanPlayer():
    def __init__(self, board):
        self.board = board
        self.move_pattern = re.compile('(\d+)([s]?)')

    def move(self):
        try:
            while True:
                match = re.fullmatch(self.move_pattern, input("Move: "))
                if match:
                    nxt_move = (int(match[1]), match[2] == 's')
                    if self.board.check(nxt_move):
                        return nxt_move
        except KeyboardInterrupt:
            exit()

def run_game(board, players):
    while board.status == "In Progress":
        print(board)
        nxt_move = players[board.player].move()
        if board.check(nxt_move):
            board.update(nxt_move)
    print(board.status)

if __name__ == "__main__":
    board = Board()
    players = [
        HumanPlayer(board),
        HumanPlayer(board)
    ]
    run_game(board, players)