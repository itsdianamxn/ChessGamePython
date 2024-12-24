import tkinter as tk
from tkinter import messagebox, PhotoImage
import random
import sys
from PIL import Image, ImageTk

tile_size = 50

# Load images into a dictionary for easier access
image_paths = {
    "black_queen": "./Images/black_queen.png",
    "black_king": "./Images/black_king.png",
    "black_rook": "./Images/black_rook.png",
    "black_bishop": "./Images/black_bishop.png",
    "black_knight": "./Images/black_knight.png",
    "black_pawn": "./Images/black_pawn.png",
    "white_queen": "./Images/white_queen.png",
    "white_king": "./Images/white_king.png",
    "white_rook": "./Images/white_rook.png",
    "white_bishop": "./Images/white_bishop.png",
    "white_knight": "./Images/white_knight.png",
    "white_pawn": "./Images/white_pawn.png"
}

class ChessGame:
    def __init__(self, root, opponent_type):
        self.root = root
        self.black_player = opponent_type
        self.board = self.initialize_board()
        self.current_player = "white"
        self.selected_piece = None
        self.valid_moves = []
        self.images = {key: ImageTk.PhotoImage(Image.open(path).resize((tile_size, tile_size), Image.Resampling.BILINEAR)) for key, path in image_paths.items()}
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
        self.canvas = tk.Canvas(self.root, width=8 * tile_size, height=8 * tile_size)
        self.canvas.pack()
        self.draw_board()
        self.canvas.bind("<Button-1>", self.on_click)

    def draw_board(self):
        self.canvas.delete("all")
        for row in range(8):
            for col in range(8):
                color = "white" if (row + col) % 2 == 0 else "gray"
                x1, y1 = col * tile_size, row * tile_size
                x2, y2 = x1 + tile_size, y1 + tile_size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)

                piece = self.board[row][col]
                if piece:
                    piece_image = self.images.get(piece)
                    if piece_image:
                        self.canvas.create_image(
                            x1 + tile_size // 2,
                            y1 + tile_size // 2,
                            image=piece_image
                        )
        if self.selected_piece is not None:
            row, col = self.selected_piece
            x1, y1 = col * tile_size+2, row * tile_size+2
            x2, y2 = x1 + tile_size-3, y1 + tile_size-3
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="blue", width=2)
            for move in self.valid_moves:
                x1, y1 = move[1] * tile_size+2, move[0] * tile_size+2
                x2, y2 = x1 + tile_size-3, y1 + tile_size-3
                if self.board[move[0]][move[1]]:
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="red", width=2)
                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="green", width=2)

    def on_click(self, event):
        if self.current_player == "black" and self.black_player == "computer":
            return

        row, col = event.y // tile_size, event.x // tile_size
        print(f"{self.current_player} clicked on {row}, {col}: {self.board[row][col]}")

        if self.selected_piece is None:  # First click
            piece = self.board[row][col]
            if not piece or \
               ("white" in piece and self.current_player == "black") or \
               ("black" in piece and self.current_player == "white"):
                return
            self.selected_piece = (row, col)
            self.valid_moves = self.get_valid_moves(row, col)
            self.draw_board()
        else:  # Second click: do the move
            from_row, from_col = self.selected_piece
            if not self.is_valid_move(from_row, from_col, row, col):
                return
            self.make_move(from_row, from_col, row, col)

            if self.current_player == "black" and self.black_player == "computer":
                self.root.after(1, self.computer_move)

    def make_move(self, from_row, from_col, to_row, to_col):
        self.board[to_row][to_col] = self.board[from_row][from_col]
        self.board[from_row][from_col] = None
        self.current_player = "black" if self.current_player == "white" else "white"
        self.selected_piece = None
        self.draw_board()

        if self.check_game_over():
            winner = "White" if self.current_player == "black" else "Black"
            messagebox.showinfo("Game Over", f"{winner} wins!")
            self.root.quit()

    def computer_move(self):
        all_moves = []
        for row in range(8):
            for col in range(8):
                if (self.get_color(row, col) == "black"):
                    moves = self.get_valid_moves(row, col)
                    for move in moves:
                        all_moves.append((row, col, move[0], move[1]))
        move = random.choice(all_moves)
        self.make_move(move[0], move[1], move[2], move[3])

    def check_game_over(self):
        # Simple game-over logic: check if kings are present
        white_king = any("white_king" in row for row in self.board)
        black_king = any("black_king" in row for row in self.board)
        return not (white_king and black_king)

    def is_valid_move(self, from_row, from_col, to_row, to_col):
        # Check if destination piece is of same color
        if self.board[to_row][to_col] and \
           self.board[from_row][from_col].split('_')[0] == self.board[to_row][to_col].split('_')[0]:
            self.selected_piece = (to_row, to_col)
            self.valid_moves = self.get_valid_moves(to_row, to_col)
            self.draw_board()
            return False
        for move in self.valid_moves:
            if move == (to_row, to_col):
                return True
        return False

    def get_valid_moves(self, row, col):
        piece = self.board[row][col]
        if "pawn" in piece:
            return self.get_pawn_moves(row, col)
        elif "rook" in piece:
            return self.get_rook_moves(row, col)
        elif "knight" in piece:
            return self.get_knight_moves(row, col)
        elif "bishop" in piece:
            return self.get_bishop_moves(row, col)
        elif "queen" in piece:
            return self.get_queen_moves(row, col)
        elif "king" in piece:
            return self.get_king_moves(row, col)

    def get_pawn_moves(self, row, col):
        moves = []
        if "white" in self.board[row][col]:
            if row > 0:
                if not self.board[row-1][col]:
                    moves.append((row-1, col))
                    if row == 6 and not self.board[row-2][col]:
                        moves.append((row-2, col))
                if col > 0 and self.board[row-1][col-1] and self.get_color(row - 1, col - 1) == "black":
                    moves.append((row-1, col-1))
                if col < 7 and self.board[row-1][col+1] and self.get_color(row - 1, col + 1) == "black":
                    moves.append((row-1, col+1))
        else: #black piece
            if row < 7:
                if not self.board[row+1][col]:
                    moves.append((row+1, col))
                    if row == 1 and not self.board[row+2][col]:
                        moves.append((row+2, col))
                if col > 0 and self.board[row+1][col-1] and self.get_color(row+1, col-1) == "white":
                    moves.append((row+1, col-1))
                if col < 7 and self.board[row+1][col+1] and self.get_color(row+1, col+1) == "white":
                    moves.append((row+1, col+1))
        return moves

    def get_rook_moves(self, row, col):
        moves = []
        for i in range(col+1, 8):
            if not self.board[row][i]:
                moves.append((row, i))
            else:
                if self.get_color(row, col) != self.get_color(row, i):
                    moves.append((row, i))
                break
        for i in range(col-1, -1, -1):
            if not self.board[row][i]:
                moves.append((row, i))
            else:
                if self.get_color(row, col) != self.get_color(row, i):
                    moves.append((row, i))
                break
        for i in range(row+1, 8):
            if not self.board[i][col]:
                moves.append((i, col))
            else:
                if self.get_color(row, col) != self.get_color(i, col):
                    moves.append((i, col))
                break
        for i in range(row-1, -1, -1):
            if not self.board[i][col]:
                moves.append((i, col))
            else:
                if self.get_color(row, col) != self.get_color(i, col):
                    moves.append((i, col))
                break
        return moves

    def get_color(self, row, col):
        if not self.board[row][col]:
            return None
        return self.board[row][col].split('_')[0]

    def get_knight_moves(self, row, col):
        return []

    def get_bishop_moves(self, row, col):
        return []

    def get_queen_moves(self, row, col):
        return []

    def get_king_moves(self, row, col):
        return []


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
