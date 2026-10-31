import tkinter as tk
import random

# Spielkonstanten
ROWS = 6
COLS = 7
EMPTY = 0
PLAYER_RED = 1
PLAYER_YELLOW = 2

class ConnectFour:
    def __init__(self, root):
        self.root = root
        self.root.title("4 Gewinnt mit KI")
        self.root.resizable(False, False)

        self.board = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]
        self.current_player = PLAYER_RED
        self.game_mode = tk.StringVar(value="ai")  # "ai" oder "pvp"
        self.is_ai_thinking = False

        # UI-Elemente erstellen
        self.create_widgets()

    def create_widgets(self):
        # Top-Bereich: Modus-Auswahl
        mode_frame = tk.Frame(self.root, pady=5)
        mode_frame.pack()

        tk.Label(mode_frame, text="Modus:", font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(
            mode_frame, text="Gegen KI (Rot vs. Gelb)", variable=self.game_mode, 
            value="ai", command=self.reset_game, font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(
            mode_frame, text="2 Spieler", variable=self.game_mode, 
            value="pvp", command=self.reset_game, font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=5)

        # Statusanzeige
        self.status_label = tk.Label(
            self.root, 
            text="Du bist am Zug (Rot)", 
            font=("Arial", 14, "bold"), 
            fg="red",
            pady=5
        )
        self.status_label.pack()

        # Canvas für das Spielfeld
        self.canvas_width = COLS * 80
        self.canvas_height = ROWS * 80
        self.canvas = tk.Canvas(
            self.root, 
            width=self.canvas_width, 
            height=self.canvas_height, 
            bg="#0055ff", 
            highlightthickness=0
        )
        self.canvas.pack(padx=10, pady=10)
        self.canvas.bind("<Button-1>", self.handle_click)

        # Neustart-Button
        self.restart_btn = tk.Button(
            self.root, 
            text="Neustart", 
            font=("Arial", 12), 
            command=self.reset_game,
            state=tk.DISABLED,
            pady=5
        )
        self.restart_btn.pack(pady=5)

        self.draw_board()

    def draw_board(self):
        self.canvas.delete("all")
        for r in range(ROWS):
            for c in range(COLS):
                x1 = c * 80 + 10
                y1 = r * 80 + 10
                x2 = x1 + 60
                y2 = y1 + 60

                color = "#ffffff"  # Leer
                if self.board[r][c] == PLAYER_RED:
                    color = "#ff3333"  # Rot
                elif self.board[r][c] == PLAYER_YELLOW:
                    color = "#ffcc00"  # Gelb

                self.canvas.create_oval(x1, y1, x2, y2, fill=color, outline="#0033cc", width=2)

    def handle_click(self, event):
        if self.is_ai_thinking:
            return

        # Im KI-Modus ist der Mensch nur am Zug, wenn er Rot ist
        if self.game_mode.get() == "ai" and self.current_player == PLAYER_YELLOW:
            return

        col = event.x // 80
        if 0 <= col < COLS:
            row = self.get_next_open_row(col)
            if row != -1:
                self.make_move(row, col)

    def make_move(self, row, col):
        self.board[row][col] = self.current_player
        self.draw_board()

        # Gewinnprüfung
        if self.check_win(self.current_player):
            if self.game_mode.get() == "ai":
                winner_text = "Du hast gewonnen! 🎉" if self.current_player == PLAYER_RED else "Die KI hat gewonnen! 🤖"
            else:
                winner_text = f"Spieler {'Rot' if self.current_player == PLAYER_RED else 'Gelb'} hat gewonnen! 🎉"
            
            self.status_label.config(text=winner_text, fg="green")
            self.canvas.unbind("<Button-1>")
            self.restart_btn.config(state=tk.NORMAL)
            return

        # Unentschieden-Prüfung
        if self.is_board_full():
            self.status_label.config(text="Unentschieden! Das Feld ist voll.", fg="orange")
            self.restart_btn.config(state=tk.NORMAL)
            return

        # Spieler wechseln
        if self.current_player == PLAYER_RED:
            self.current_player = PLAYER_YELLOW
            if self.game_mode.get() == "ai":
                self.status_label.config(text="KI überlegt...", fg="#cc9900")
                self.is_ai_thinking = True
                self.root.after(400, self.trigger_ai_move)  # Kleine Verzögerung für Echtheit
            else:
                self.status_label.config(text="Spieler 2 ist am Zug (Gelb)", fg="#cc9900")
        else:
            self.current_player = PLAYER_RED
            self.status_label.config(text="Du bist am Zug (Rot)", fg="red")

    def trigger_ai_move(self):
        col, _ = self.minimax(self.board, 4, True)
        if col is not None and self.get_next_open_row(col) != -1:
            row = self.get_next_open_row(col)
            self.is_ai_thinking = False
            self.make_move(row, col)

    def get_next_open_row(self, col):
        for r in range(ROWS - 1, -1, -1):
            if self.board[r][col] == EMPTY:
                return r
        return -1

    def is_board_full(self):
        return all(self.board[0][c] != EMPTY for c in range(COLS))

    def check_win(self, player):
        return self.check_win_static(self.board, player)

    @staticmethod
    def check_win_static(board, player):
        # Waagerecht
        for r in range(ROWS):
            for c in range(COLS - 3):
                if all(board[r][c + i] == player for i in range(4)):
                    return True
        # Senkrecht
        for r in range(ROWS - 3):
            for c in range(COLS):
                if all(board[r + i][c] == player for i in range(4)):
                    return True
        # Diagonale positiv
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                if all(board[r + i][c + i] == player for i in range(4)):
                    return True
        # Diagonale negativ
        for r in range(3, ROWS):
            for c in range(COLS - 3):
                if all(board[r - i][c + i] == player for i in range(4)):
                    return True
        return False

    # --- KI Minimax Algorithmus ---
    def score_window(self, window, player):
        score = 0
        opponent = PLAYER_RED if player == PLAYER_YELLOW else PLAYER_YELLOW

        if window.count(player) == 4:
            score += 100
        elif window.count(player) == 3 and window.count(EMPTY) == 1:
            score += 5
        elif window.count(player) == 2 and window.count(EMPTY) == 2:
            score += 2

        if window.count(opponent) == 3 and window.count(EMPTY) == 1:
            score -= 80

        return score

    def score_position(self, board, player):
        score = 0
        # Zentrum bevorzugen
        center_array = [board[r][COLS // 2] for r in range(ROWS)]
        center_count = center_array.count(player)
        score += center_count * 3

        # Waagerecht bewerten
        for r in range(ROWS):
            row_array = [board[r][c] for c in range(COLS)]
            for c in range(COLS - 3):
                window = row_array[c:c + 4]
                score += self.score_window(window, player)

        # Senkrecht bewerten
        for c in range(COLS):
            col_array = [board[r][c] for r in range(ROWS)]
            for r in range(ROWS - 3):
                window = col_array[r:r + 4]
                score += self.score_window(window, player)

        # Diagonal positiv
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                window = [board[r + i][c + i] for i in range(4)]
                score += self.score_window(window, player)

        # Diagonal negativ
        for r in range(3, ROWS):
            for c in range(COLS - 3):
                window = [board[r - i][c + i] for i in range(4)]
                score += self.score_window(window, player)

        return score

    def minimax(self, board, depth, maximizing_player):
        valid_locations = [c for c in range(COLS) if board[0][c] == EMPTY]
        is_terminal = self.check_win_static(board, PLAYER_RED) or self.check_win_static(board, PLAYER_YELLOW) or len(valid_locations) == 0

        if depth == 0 or is_terminal:
            if is_terminal:
                if self.check_win_static(board, PLAYER_YELLOW):
                    return (None, 10000000)
                elif self.check_win_static(board, PLAYER_RED):
                    return (None, -10000000)
                else:
                    return (None, 0)
            else:
                return (None, self.score_position(board, PLAYER_YELLOW))

        if maximizing_player:
            value = -float('inf')
            best_col = random.choice(valid_locations)
            for col in valid_locations:
                for r in range(ROWS - 1, -1, -1):
                    if board[r][col] == EMPTY:
                        row = r
                        break
                temp_board = [row_[:] for row_ in board]
                temp_board[row][col] = PLAYER_YELLOW
                new_score = self.minimax(temp_board, depth - 1, False)[1]
                if new_score > value:
                    value = new_score
                    best_col = col
            return best_col, value
        else:
            value = float('inf')
            best_col = random.choice(valid_locations)
            for col in valid_locations:
                for r in range(ROWS - 1, -1, -1):
                    if board[r][col] == EMPTY:
                        row = r
                        break
                temp_board = [row_[:] for row_ in board]
                temp_board[row][col] = PLAYER_RED
                new_score = self.minimax(temp_board, depth - 1, True)[1]
                if new_score < value:
                    value = new_score
                    best_col = col
            return best_col, value

    def reset_game(self):
        self.board = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]
        self.current_player = PLAYER_RED
        self.is_ai_thinking = False
        mode_text = "Du bist am Zug (Rot)" if self.game_mode.get() == "ai" else "Spieler 1 ist am Zug (Rot)"
        self.status_label.config(text=mode_text, fg="red")
        self.canvas.bind("<Button-1>", self.handle_click)
        self.restart_btn.config(state=tk.DISABLED)
        self.draw_board()

if __name__ == "__main__":
    root = tk.Tk()
    app = ConnectFour(root)
    root.mainloop()