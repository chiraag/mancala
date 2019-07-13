import curses
import rules

class UIPlayer():
    def __init__(self, board):
        self.board = board
        self.nxt_pos = 0 
        self.nxt_skip = False

    @property
    def move(self):
        nxt_move = rules.Move(self.nxt_pos, self.nxt_skip)
        if self.board.check(nxt_move):
            return nxt_move
        else:
            return None

    def inc(self):
        self.nxt_pos = min(self.nxt_pos + 1, self.board.board_sz - 1)

    def dec(self):
        self.nxt_pos = max(self.nxt_pos - 1, 0)

class Window:
    def __init__(self, stdscr):
        self.screen = stdscr
        curses.curs_set(0)
        self.colors = self.setup_colors()
        self.body_state = 'game'

        self.board, self.players = self.new_game()

        self.nrows, self.ncols = self.screen.getmaxyx()
        self.header = self.screen.subwin(1, self.ncols, 0, 0)
        self.body = self.screen.subwin(self.nrows-2, self.ncols, 1, 0)
        self.footer = self.screen.subwin(1, self.ncols, self.nrows-1, 0)

        self.draw_header()
        self.draw_body()
        self.draw_footer()

        curses.doupdate()
        self.main_loop()

    def new_game(self):
        board = rules.Board()
        players = [
            UIPlayer(board),
            UIPlayer(board)
        ]
        return board, players

    def main_loop(self):
        while True:
            c = self.screen.getch()
            if c == ord('q'):
                exit()
            elif c == ord('h'):
                self.body_state = 'help'
                self.draw_body()
            elif c == ord('g'):
                self.body_state = 'game'
                self.draw_body()
            elif c == curses.KEY_RESIZE:
                self.nrows, self.ncols = self.screen.getmaxyx()
                self.header = self.screen.subwin(1, self.ncols, 0, 0)
                self.body = self.screen.subwin(self.nrows-2, self.ncols, 1, 0)
                self.footer = self.screen.subwin(1, self.ncols, self.nrows-1, 0)

                self.draw_header()
                self.draw_body()
                self.draw_footer()
            elif self.body_state == 'game':
                curr_player = self.players[self.board.player]
                is_top_player = (self.board.player == 0)
                if c == ord('n'):
                    self.board, self.players = self.new_game()
                elif c == curses.KEY_LEFT:
                    curr_player.dec() if is_top_player else curr_player.inc()
                elif c == curses.KEY_RIGHT:
                    curr_player.inc() if is_top_player else curr_player.dec()
                elif  c == curses.KEY_UP:
                    curr_player.nxt_skip = True
                elif c == curses.KEY_DOWN:
                    curr_player.nxt_skip = False
                elif c == curses.KEY_ENTER or c == 10 or c == 13:
                    if curr_player.move is not None:
                        self.board.update(curr_player.move)
                self.draw_body()
            curses.doupdate()

    def setup_colors(self):
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_BLACK, -1)
        curses.init_pair(2, curses.COLOR_RED, -1)
        curses.init_pair(3, curses.COLOR_GREEN, -1)
        return {color: curses.color_pair(idx+1) for idx, color in enumerate(['black', 'red', 'green'])}

    def draw_header(self):
        self.header.clear()
        self.header.bkgd(curses.A_REVERSE)
        header_str = "Mancala v0.1"
        self.header.addstr(0, (self.ncols-len(header_str))//2, header_str)
        self.header.noutrefresh()

    def draw_footer(self):
        self.footer.clear()
        self.footer.bkgd(curses.A_REVERSE)
        footer_items = [["New Game: n", "Help: h", "Return to Game: g"], ["Quit: q"]]
        footer_str_parts = ["    ".join(item_list) for item_list in footer_items]
        footer_str = " " + footer_str_parts[0] + " "*(self.ncols - 2 - sum([len(part) for part in footer_str_parts])) + footer_str_parts[1]
        # footer_str = footer_str_parts[0] + " " + footer_str_parts[1]
        self.footer.addstr(footer_str)
        self.footer.noutrefresh()

    def draw_body(self):
        if self.body_state == "game":
            self.draw_game()
        else:
            self.draw_help()

    def draw_help(self):
        self.body.clear()

        help_str = """
            Game Rules:
                - Board Size: 2x6
                - Seeds per hole: 4
                - Move ending on player's home results in free turn
                - Move ending on an empty hole "captures" all seeds from the opposite hole
                - Player never seeds opponent's home
                - Player may optionally skip seeding own home

            Controls:
                - Left and Right Arrow Key to select hole
                - Up Arrow activates skip move (Current move highlighted)
                - Down Arrow activates skip move (Current move underlined)
                - Enter for simple move
        """

        for idx, line in enumerate(help_str.split('\n')):
            self.body.addstr(idx, 0, line)

        self.body.noutrefresh()

    def draw_game(self):
        self.body.clear()

        height, width = 1, 4
        cell_y, cell_x = (2, self.board.state.shape[0]//2 + 1)
        total_height, total_width = cell_y * (height + 1) + 1, cell_x * (width + 1) + 1

        nrows, ncols = self.body.getmaxyx()
        uly, ulx = (nrows - total_height)//2, (ncols - total_width)//2
        lry, lrx = (uly + total_height - 1, ulx + total_width - 1)

        # Draw hlines
        for idx_y in range(cell_y+1):
            pos_y = uly + idx_y * (height + 1)
            for idx_x in range(cell_x):
                pos_x = ulx + idx_x * (width + 1)
                if idx_y == 0:
                    if idx_x == 0:
                        self.body.addch(pos_y, pos_x, curses.ACS_ULCORNER)
                    else:
                        self.body.addch(pos_y, pos_x, curses.ACS_TTEE)
                    self.body.hline(pos_y, pos_x + 1, curses.ACS_HLINE, width)
                elif idx_y == 1:
                    if idx_x == 0:
                        self.body.addch(pos_y, pos_x, curses.ACS_VLINE)
                    elif idx_x == 1:
                        self.body.addch(pos_y, pos_x, curses.ACS_LTEE)
                    elif idx_x == cell_x - 1:
                        self.body.addch(pos_y, pos_x, curses.ACS_RTEE)
                    else:
                        self.body.addch(pos_y, pos_x, curses.ACS_PLUS)
                    if idx_x != 0 and idx_x != cell_x - 1:
                        self.body.hline(pos_y, pos_x + 1, curses.ACS_HLINE, width)
                else:
                    if idx_x == 0:
                        self.body.addch(pos_y, pos_x, curses.ACS_LLCORNER)
                    else:
                        self.body.addch(pos_y, pos_x, curses.ACS_BTEE)
                    self.body.hline(pos_y, pos_x + 1, curses.ACS_HLINE, width)
            if idx_y == 0:
                self.body.addch(pos_y, lrx, curses.ACS_URCORNER)
            elif idx_y == 1:
                self.body.addch(pos_y, lrx, curses.ACS_VLINE)
            else:
                self.body.addch(pos_y, lrx, curses.ACS_LRCORNER)

        # Draw vlines
        for idx_y in range(cell_y):
            pos_y = uly + idx_y * (height + 1) + 1
            for idx_x in range(cell_x+1):
                pos_x = ulx + idx_x * (width + 1)
                self.body.vline(pos_y, pos_x, curses.ACS_VLINE, height)

        # Fill values
        pos_y = uly + (height + 1)//2
        for idx_x in range(cell_x - 2):
            pos_x = ulx + (idx_x + 1)*(width + 1) + (width) // 2
            self.body.addstr(pos_y, pos_x, "%2d" % self.board.state[idx_x], self.colors['red'])
            self.body.addstr(pos_y + (height + 1), pos_x, "%2d" % self.board.state[-idx_x-2], self.colors['green'])
        self.body.addstr(uly + height + 1, lrx - width//2 - 1, "%2d" % self.board.state[self.board.mancala[0]], self.colors['red'])
        self.body.addstr(uly + height + 1, ulx + width//2, "%2d" % self.board.state[self.board.mancala[1]], self.colors['green'])

        if self.board.done:
            # Final state
            if self.board.state[self.board.mancala[0]] > self.board.state[self.board.mancala[1]]:
                final_string = "Top player wins"
            elif self.board.state[self.board.mancala[0]] < self.board.state[self.board.mancala[1]]:
                final_string = "Bottom Player wins"
            else:
                final_string = "Draw"
            self.body.addstr(lry+2, (ncols-len(final_string))//2, final_string)
        else:
            # Highlight next move
            curr_player = self.players[self.board.player]
            move_idx = self.board.player * (self.board.board_sz + 1) + curr_player.nxt_pos
            move_format = (
                (self.colors['green'] if self.board.player else self.colors['red']) |
                (curses.A_REVERSE if curr_player.nxt_skip else curses.A_UNDERLINE)
            )
            pos_y = uly + self.board.player * (height + 1) + (height + 1)//2
            if self.board.player == 0:
                pos_x = ulx + (curr_player.nxt_pos + 1)*(width + 1) + (width)//2
            else:
                pos_x = lrx - (curr_player.nxt_pos + 1)*(width + 1) - (width)//2 - 1
            self.body.addstr(pos_y, pos_x, "%2d" % self.board.state[move_idx], move_format)

        self.body.noutrefresh()

if __name__ == "__main__":
    curses.wrapper(Window)