import tkinter as tk
from tkinter import messagebox
import random
import sys

tile_size = 50

class ChessGame:
    def __init__(self, root, opponent_type):
        self.root = root
        self.black_player = opponent_type
        self.board = self.initialize_board()
        self.current_player = "white"
        self.selected_piece = None
        self.create_gui()

    def initialize_board(self):
        # Initialize an 8x8 chess board
        board = [[None for _ in range(8)] for _ in range(8)]
        pieces = ["rook", "knight", "bishop", "queen", "king", "bishop", "knight", "rook"]

        # Place pawns
        board[1] = ["black_pawn"] * 8
        board[6] = ["white_pawn"] * 8

        # Place other pieces
        for i in range(8):
            board[0][i] = f"black_{pieces[i]}"
            board[7][i] = f"white_{pieces[i]}"

        return board

    def create_gui(self):
        self.canvas = tk.Canvas(self.root, width=400, height=400)
        self.canvas.pack()
        self.draw_board()
        self.canvas.bind("<Button-1>", self.on_click)

    def draw_board(self):
        self.canvas.delete("all")
        for row in range(8):
            for col in range(8):
                color = "white" if (row + col) % 2 == 0 else "gray"
                x1 = col * tile_size
                y1 = row * tile_size
                x2 = x1 + tile_size
                y2 = y1 + tile_size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)

                piece = self.board[row][col]
                if piece:
                    self.canvas.create_text(
                        (x1 + x2) // 2,
                        (y1 + y2) // 2,
                        text=piece.split('_')[1][0].upper(),
                        fill="black" if "white" in piece else "red"
                    )

    def on_click(self, event):
        if self.current_player == "black" and self.black_player == "computer":
            return
        row = event.y // tile_size
        col = event.x // tile_size
        print(f"{self.current_player} clicked on {row}, {col}: {self.board[row][col]}")

        if self.selected_piece is None: # First click
            piece = self.board[row][col]
            if (not piece or
                ("white" in piece and self.current_player == "black") or
                ("black" in piece and self.current_player == "white")):
                return
            self.selected_piece = (row, col)
        else:
            from_row, from_col = self.selected_piece
            if not self.is_valid_move(from_row, from_col, row, col):
                return False
            self.make_move(from_row, from_col, row, col)

            if self.current_player == "white" and self.black_player == "computer":
                self.computer_move()

    def make_move(self, from_row, from_col, to_row, to_col):
        self.board[to_row][to_col] = self.board[from_row][from_col]
        self.board[from_row][from_col] = None
        self.current_player = "black" if self.current_player == "white" else "white"
        self.draw_board()
        self.selected_piece = None

        if self.check_game_over():
            winner = "White" if self.current_player == "black" else "Black"
            messagebox.showinfo("Game Over", f"{winner} wins!")
            self.root.quit()

    def computer_move(self):
        all_moves = []
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and "black" in piece:
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                        nr, nc = row + dr, col + dc
                        if 0 <= nr < 8 and 0 <= nc < 8 and (not self.board[nr][nc] or "white" in self.board[nr][nc]):
                            all_moves.append(((row, col), (nr, nc)))

        if all_moves:
            move = random.choice(all_moves)
            self.make_move(*move[0], *move[1])

    def check_game_over(self):
        # Simple game-over logic: check if kings are present
        white_king = any("white_king" in row for row in self.board)
        black_king = any("black_king" in row for row in self.board)
        return not (white_king and black_king)

    def is_valid_move(self, from_row, from_col, to_row, to_col):
        # Check if destination piece is of same color
        if self.board[to_row][to_col] and self.board[from_row][from_col].split('_')[0] == self.board[to_row][to_col].split('_')[0]:
            return False

        return True


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ["computer", "opponent"]:
        print("Usage: python chess.py <opponent_type>")
        print("opponent_type: 'computer' or 'opponent'")
        sys.exit(1)

    opponent_type = sys.argv[1]
    window = tk.Tk()
    window.title("Chess Game")
    game = ChessGame(window, opponent_type)
    window.mainloop()
