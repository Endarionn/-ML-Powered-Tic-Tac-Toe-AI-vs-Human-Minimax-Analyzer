import tkinter as tk
import numpy as np
from tensorflow.keras.models import load_model
import copy

# Modeli yükle
model = load_model("tictactoe_model.keras")

root = tk.Tk()

# Eğitim verisi büyüklüğü (bunu kendi verine göre ayarla)
root.title(f"ML Tic Tac Toe — Endarionn")

board = [["" for _ in range(3)] for _ in range(3)]
buttons = [[None]*3 for _ in range(3)]
player = "X"  # insan
ai = "O"      # bot
game_over = False

result_label = None
info_label = None
log_text = None

def encode_board(bd):
    flat = []
    for row in bd:
        for cell in row:
            if cell == "X":
                flat.append(-1)
            elif cell == "O":
                flat.append(1)
            else:
                flat.append(0)
    return np.array([flat])

def check_winner_static(bd):
    for r in range(3):
        if bd[r][0] == bd[r][1] == bd[r][2] != "":
            return bd[r][0]
    for c in range(3):
        if bd[0][c] == bd[1][c] == bd[2][c] != "":
            return bd[0][c]
    if bd[0][0] == bd[1][1] == bd[2][2] != "":
        return bd[0][0]
    if bd[0][2] == bd[1][1] == bd[2][0] != "":
        return bd[0][2]
    if all(bd[r][c] != "" for r in range(3) for c in range(3)):
        return "Draw"
    return None

def minimax(bd, current_player):
    winner = check_winner_static(bd)
    if winner == ai:
        return 1, []
    elif winner == player:
        return -1, []
    elif winner == "Draw":
        return 0, []

    best_score = -2 if current_player == ai else 2
    best_moves = []

    for r in range(3):
        for c in range(3):
            if bd[r][c] == "":
                bd_copy = copy.deepcopy(bd)
                bd_copy[r][c] = current_player
                score, _ = minimax(bd_copy, player if current_player == ai else ai)
                if current_player == ai:
                    if score > best_score:
                        best_score = score
                        best_moves = [(r, c)]
                    elif score == best_score:
                        best_moves.append((r, c))
                else:
                    if score < best_score:
                        best_score = score
                        best_moves = [(r, c)]
                    elif score == best_score:
                        best_moves.append((r, c))
    return best_score, best_moves

def estimate_chance(bd, side):
    # Mevcut tahtadan başlayıp, bütün olası devamları tarayan Minimax türevi
    # Kazanma durumlarının sayısını toplam durum sayısına böl
    def count_results(board, current_player):
        winner = check_winner_static(board)
        if winner == ai:
            return (1,0,0)  # AI wins
        elif winner == player:
            return (0,0,1)  # Player wins
        elif winner == "Draw":
            return (0,1,0)  # Draw
        
        wins = draws = losses = 0
        for r in range(3):
            for c in range(3):
                if board[r][c] == "":
                    board[r][c] = current_player
                    w,d,l = count_results(board, player if current_player == ai else ai)
                    board[r][c] = ""
                    wins += w
                    draws += d
                    losses += l
        return wins, draws, losses

    wins, draws, losses = count_results(copy.deepcopy(bd), side)
    total = wins + draws + losses
    if total == 0:
        return 0
    # side için kazanma yüzdesi
    return round(100 * wins / total, 2)


def ai_move():
    global game_over
    if game_over:
        return

    encoded = encode_board(board)
    pred = model.predict(encoded, verbose=0)[0]
    sorted_indices = np.argsort(pred)[::-1]

    model_move = None
    for idx in sorted_indices:
        r, c = divmod(idx, 3)
        if board[r][c] == "":
            model_move = (r, c)
            break

    # Minimax ile model hamlesini doğrula
    score, best_moves = minimax(board, ai)
    correct = model_move in best_moves

    status_text = f"Model move: Row {model_move[0]+1}, Col {model_move[1]+1}\n"
    status_text += f"Is move optimal? {'Yes' if correct else 'No'}\n"
    status_text += f"Player win chance: {estimate_chance(board, player)}%\n"
    status_text += f"AI win chance: {estimate_chance(board, ai)}%"

    info_label.config(text=status_text)

    if not correct:
        log_text.delete("1.0", tk.END)
        log_text.insert(tk.END, "Model move is NOT optimal.\nBest moves suggested by Minimax:\n")
        for m in best_moves:
            log_text.insert(tk.END, f"Row {m[0]+1}, Col {m[1]+1}\n")
    else:
        log_text.delete("1.0", tk.END)

    # Modelin hamlesini yap
    r, c = model_move
    board[r][c] = ai
    buttons[r][c].config(text=ai, state="disabled")

    result = check_winner_static(board)
    if result:
        end_game(result)

def click(r, c):
    global game_over
    if board[r][c] == "" and not game_over:
        board[r][c] = player
        buttons[r][c].config(text=player, state="disabled")
        result = check_winner_static(board)
        if result:
            end_game(result)
        else:
            root.after(300, ai_move)

def end_game(winner):
    global game_over
    game_over = True
    info_label.config(text=f"Game over! Winner: {winner}")

def restart_game():
    global game_over
    game_over = False
    for r in range(3):
        for c in range(3):
            board[r][c] = ""
            buttons[r][c].config(text="", state="normal")
    info_label.config(text="")
    log_text.delete("1.0", tk.END)

# UI oluşturma
for r in range(3):
    for c in range(3):
        btn = tk.Button(root, text="", width=6, height=3, font=("Arial", 24),
                        command=lambda r=r, c=c: click(r, c))
        btn.grid(row=r, column=c)
        buttons[r][c] = btn

info_label = tk.Label(root, text="", font=("Arial", 12), justify="left")
info_label.grid(row=3, column=0, columnspan=3)

log_text = tk.Text(root, height=6, width=25)
log_text.grid(row=4, column=0, columnspan=3)

restart_button = tk.Button(root, text="Restart", font=("Arial", 14), command=restart_game)
restart_button.grid(row=5, column=0, columnspan=3, pady=10)

root.mainloop()
