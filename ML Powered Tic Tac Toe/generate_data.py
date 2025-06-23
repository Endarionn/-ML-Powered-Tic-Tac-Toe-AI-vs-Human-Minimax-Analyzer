import tkinter as tk
import random
import csv
import copy

# === GUI Kurulumu ===
root = tk.Tk()
root.title("Tic Tac Toe Veri Üretimi - Canlı Hamle")

buttons = [[None]*3 for _ in range(3)]
board = [["" for _ in range(3)] for _ in range(3)]
current = "X"
game_states = []
step_delay = 300  # ms

csv_file = open("tic_tac_toe_data.csv", "w", newline="")
csv_writer = csv.writer(csv_file)
csv_writer.writerow([f"cell_{i}" for i in range(9)] + ["move"])

def flatten(board):
    return [cell if cell != "" else "-" for row in board for cell in row]

def check_winner(board):
    for r in range(3):
        if board[r][0] == board[r][1] == board[r][2] != "":
            return board[r][0]
    for c in range(3):
        if board[0][c] == board[1][c] == board[2][c] != "":
            return board[0][c]
    if board[0][0] == board[1][1] == board[2][2] != "":
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != "":
        return board[0][2]
    if all(cell != "" for row in board for cell in row):
        return "Draw"
    return None

def get_empty_cells(board):
    return [(r, c) for r in range(3) for c in range(3) if board[r][c] == ""]

def random_move(board):
    return random.choice(get_empty_cells(board))

def minimax(board, is_max):
    winner = check_winner(board)
    if winner == "X": return -1
    if winner == "O": return 1
    if winner == "Draw": return 0

    scores = []
    for r, c in get_empty_cells(board):
        board[r][c] = "O" if is_max else "X"
        score = minimax(board, not is_max)
        board[r][c] = ""
        scores.append(score)

    return max(scores) if is_max else min(scores)

def best_move(board):
    best_score = -999
    move = None
    for r, c in get_empty_cells(board):
        board[r][c] = "O"
        score = minimax(board, False)
        board[r][c] = ""
        if score > best_score:
            best_score = score
            move = (r, c)
    return move

def update_gui():
    for r in range(3):
        for c in range(3):
            val = board[r][c]
            buttons[r][c].config(text=val)

def reset_game():
    global board, current, game_states
    board = [["" for _ in range(3)] for _ in range(3)]
    current = "X"
    game_states = []
    update_gui()
    root.after(step_delay, play_step)

def play_step():
    global current, board, game_states
    winner = check_winner(board)
    if winner:
        # O oyuncusunun hamleleri veriye eklensin
        for state, move, player in game_states:
            if player == "O":
                csv_writer.writerow(state + [move])
        csv_file.flush()
        root.after(step_delay, reset_game)
        return

    snapshot = copy.deepcopy(board)
    if current == "X":
        r, c = random_move(board)
    else:
        r, c = best_move(board)
    board[r][c] = current
    game_states.append((flatten(snapshot), r * 3 + c, current))
    update_gui()
    current = "O" if current == "X" else "X"
    root.after(step_delay, play_step)

# === GUI Tahtası ===
for r in range(3):
    for c in range(3):
        btn = tk.Label(root, text="", width=6, height=3, font=("Arial", 24), relief="ridge", borderwidth=2)
        btn.grid(row=r, column=c)
        buttons[r][c] = btn

# === Oyunu Başlat ===
root.after(500, play_step)
root.mainloop()

csv_file.close()
