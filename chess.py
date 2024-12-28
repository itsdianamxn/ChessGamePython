import tkinter as tk
from tkinter import messagebox, PhotoImage
import random
import sys
from PIL import Image, ImageTk

tile_size = 50
border_width = 20
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

        self.white_king_moved = False
        self.white_right_rook_moved = False
        self.white_left_rook_moved = False

        self.black_king_moved = False
        self.black_right_rook_moved = False
        self.black_left_rook_moved = False

        self.allow_recursion = True
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
        self.canvas = tk.Canvas(self.root, width=8 * tile_size + 2*border_width, height=8 * tile_size + 2*border_width)
        self.canvas.pack()
        self.draw_board()
        self.canvas.bind("<Button-1>", self.on_click)

    def draw_board(self):
        self.canvas.delete("all")
        for row in range(8):
            for col in range(8):
                color = "white" if (row + col) % 2 == 0 else "gray"
                x1, y1 = col * tile_size + border_width, row * tile_size + border_width
                x2, y2 = x1 + tile_size, y1 + tile_size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)

                piece = self.board[row][col]
                if piece:
                    piece_image = self.images.get(piece)
                    if piece_image:
                        self.canvas.create_image(
                            x1 + tile_size // 2,
                            y1 + tile_size // 2,
                            image=piece_image)

        if self.selected_piece is not None:
            row, col = self.selected_piece
            x1, y1 = col * tile_size+2 + border_width, row * tile_size+2 + border_width
            x2, y2 = x1 + tile_size-3, y1 + tile_size-3
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="blue", width=2)
            for move in self.valid_moves:
                x1, y1 = move[1] * tile_size+2 + border_width, move[0] * tile_size+2 + border_width
                x2, y2 = x1 + tile_size-3, y1 + tile_size-3
                if self.board[move[0]][move[1]]:
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="red", width=2)
                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="green", width=2)
        for i in range(8):
            self.canvas.create_text(border_width + tile_size // 2 + i * tile_size, border_width // 2, text=chr(ord('A')+i))
            self.canvas.create_text(border_width // 2, border_width + tile_size // 2 + i * tile_size, text=8-i)
            self.canvas.create_text(border_width + tile_size // 2 + i * tile_size, tile_size * 8 + 3 * border_width // 2, text=chr(ord('A')+i))
            self.canvas.create_text(tile_size * 8 + 3 * border_width // 2, border_width + tile_size // 2 + i * tile_size, text=8-i)
    def on_click(self, event):
        if self.current_player == "black" and self.black_player == "computer":
            return

        row, col = (event.y - border_width) // tile_size, (event.x - border_width) // tile_size
        if row < 0 or row >= 8 or col < 0 or col >= 8:
            return
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
            if (row, col) not in self.valid_moves:
                if self.board[row][col] and self.get_color(row, col) == self.current_player:
                    self.selected_piece = (row, col)
                    self.valid_moves = self.get_valid_moves(row, col)
                    self.draw_board()
                return
            self.make_move(from_row, from_col, row, col)

            if self.current_player == "black" and self.black_player == "computer":
                self.root.after(1, self.computer_move)

    def make_move(self, from_row, from_col, to_row, to_col):
        if self.board[from_row][from_col] == "white_king":
            self.white_king_moved = True
            if to_col == 2 and from_col == 4:
                self.board[7][3] = "white_rook"
                self.board[7][0] = None
            elif to_col == 6 and from_col == 4:
                self.board[7][5] = "white_rook"
                self.board[7][7] = None
        elif self.board[from_row][from_col] == "white_rook":
            if from_col == 0:
                self.white_left_rook_moved = True
            elif from_col == 7:
                self.white_right_rook_moved = True
        elif self.board[from_row][from_col] == "black_king":
            self.black_king_moved = True
            if to_col == 2 and from_col == 4:
                self.board[0][3] = "black_rook"
                self.board[0][0] = None
            elif to_col == 6 and from_col == 4:
                self.board[0][5] = "black_rook"
                self.board[0][7] = None
        elif self.board[from_row][from_col] == "black_rook":
            if from_col == 0:
                self.black_left_rook_moved = True
            elif from_col == 7:
                self.black_right_rook_moved = True

        self.board[to_row][to_col] = self.board[from_row][from_col]
        self.board[from_row][from_col] = None
        self.current_player = "black" if self.current_player == "white" else "white"
        self.selected_piece = None
        self.draw_board()

        if self.check_game_over():
            self.root.quit()

    def computer_move(self):
        all_my_moves = self.get_all_moves(self.current_player)
        for move in all_my_moves.copy():
            if not self.is_safe_move(move[0], move[1], move[2], move[3]):
                all_my_moves.remove(move)
        move = random.choice(all_my_moves)
        self.make_move(move[0], move[1], move[2], move[3])

    def get_all_moves(self, color):
        all_moves = []
        if not self.allow_recursion:
            return all_moves
        self.allow_recursion = False
        for row in range(8):
            for col in range(8):
                if self.get_color(row, col) == color:
                    moves = self.get_valid_moves(row, col)
                    for move in moves:
                        all_moves.append((row, col, move[0], move[1]))
        self.allow_recursion = True
        return all_moves

    def check_game_over(self):
        all_my_moves = self.get_all_moves(self.current_player)
        for move in all_my_moves.copy():
            if not self.is_safe_move(move[0], move[1], move[2], move[3]):
                all_my_moves.remove(move)
        if all_my_moves != []:
            return False

        king_loc = self.get_king_location()
        all_opp_moves = self.get_all_moves("white" if self.current_player == "black" else "black")
        for move in all_opp_moves:
            if move[2] == king_loc[1] and move[3] == king_loc[0]: # king is in check, mate
                winner = "White" if self.current_player == "black" else "Black"
                messagebox.showinfo("Game Over", f"{winner} wins!")
                return True
        messagebox.showinfo("Game Over", "It's a draw!")
        return True

    def get_valid_moves(self, row, col):
        moves = []
        piece = self.board[row][col]
        if "pawn" in piece:
            moves = self.get_pawn_moves(row, col)
        elif "rook" in piece:
            moves = self.get_rook_moves(row, col)
        elif "knight" in piece:
            moves = self.get_knight_moves(row, col)
        elif "bishop" in piece:
            moves = self.get_bishop_moves(row, col)
        elif "queen" in piece:
            moves = self.get_queen_moves(row, col)
        elif "king" in piece:
            moves = self.get_king_moves(row, col)

        # avoid moves that put the king in check
        self.filter_check_moves(row, col, moves)
        return moves

    def get_pawn_moves(self, row, col):
        moves = []
        if "white" in self.board[row][col]:
            if row > 0:
                if not self.board[row-1][col]:
                    moves.append((row-1, col))
                    if row == 6 and not self.board[row-2][col]:
                        moves.append((row-2, col))
                if col > 0:
                    if self.board[row-1][col-1] and self.get_color(row - 1, col - 1) == "black":
                        moves.append((row-1, col-1))
                if col < 7:
                    if self.board[row-1][col+1] and self.get_color(row - 1, col + 1) == "black":
                        moves.append((row-1, col+1))
        else: #black piece
            if row < 7:
                if not self.board[row+1][col]:
                    moves.append((row+1, col))
                    if row == 1 and not self.board[row+2][col]:
                        moves.append((row+2, col))
                if col > 0:
                    if self.board[row+1][col-1] and self.get_color(row+1, col-1) == "white":
                        moves.append((row+1, col-1))
                if col < 7:
                    if self.board[row+1][col+1] and self.get_color(row+1, col+1) == "white":
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

    def get_knight_moves(self, row, col):
        moves = []
        for i, j in [(2, 1), (2, -1), (-2, 1), (-2, -1),
                     (1, 2), (1, -2), (-1, 2), (-1, -2)]:
            if 0 <= row + i < 8 and 0 <= col + j < 8:
                if not self.board[row+i][col+j] or self.get_color(row, col) != self.get_color(row+i, col+j):
                    moves.append((row+i, col+j))
        return moves

    def get_bishop_moves(self, row, col):
        moves = []
        for i in range(1, min(row, col)+1):
            if not self.board[row-i][col-i]:
                moves.append((row-i, col-i))
            else:
                if self.get_color(row, col) != self.get_color(row-i, col-i):
                    moves.append((row-i, col-i))
                break
        for i in range(1, min(row, 7-col)+1):
            if not self.board[row-i][col+i]:
                moves.append((row-i, col+i))
            else:
                if self.get_color(row, col) != self.get_color(row-i, col+i):
                    moves.append((row-i, col+i))
                break
        for i in range(1, min(7-row, col)+1):
            if not self.board[row+i][col-i]:
                moves.append((row+i, col-i))
            else:
                if self.get_color(row, col) != self.get_color(row+i, col-i):
                    moves.append((row+i, col-i))
                break
        for i in range(1, min(7-row, 7-col)+1):
            if not self.board[row+i][col+i]:
                moves.append((row+i, col+i))
            else:
                if self.get_color(row, col) != self.get_color(row+i, col+i):
                    moves.append((row+i, col+i))
                break
        return moves

    def get_queen_moves(self, row, col):
        moves = []
        moves.extend(self.get_rook_moves(row, col))
        moves.extend(self.get_bishop_moves(row, col))
        return moves

    def get_king_moves(self, row, col):
        moves = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if 0 <= row + i < 8 and 0 <= col + j < 8:
                    if not self.board[row+i][col+j] or self.get_color(row, col) != self.get_color(row+i, col+j):
                        moves.append((row+i, col+j))

        # Castling white
        if self.get_color(row, col) == "white" and not self.white_king_moved:
            if not self.white_right_rook_moved and not self.board[7][1] and not self.board[7][2] and not self.board[7][3] and \
               self.board[7][0] == "white_rook":
                moves.append((7, 2))
            if not self.white_right_rook_moved and not self.board[7][5] and not self.board[7][6] and \
               self.board[7][7] == "white_rook":
                moves.append((7, 6))

        # Castling black
        if self.get_color(row, col) == "black" and not self.black_king_moved:
            if not self.black_right_rook_moved and not self.board[0][1] and not self.board[0][2] and not self.board[0][3] and \
               self.board[0][0] == "black_rook":
                moves.append((0, 2))
            if not self.black_right_rook_moved and not self.board[0][5] and not self.board[0][6] and \
               self.board[0][7] == "black_rook":
                moves.append((0, 6))
        return moves

    def filter_check_moves(self, row, col, moves):
        moves_iter = moves.copy()  # avoid modifying the list while iterating
        for move in moves_iter:
            if not self.is_safe_move(row, col, move[0], move[1]):
                moves.remove(move)


    def is_safe_move(self, from_row, from_col, to_row, to_col):
        piece = self.board[from_row][from_col]
        old_piece = self.board[to_row][to_col]
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None

        king_col, king_row = self.get_king_location()

        opp_moves = self.get_all_moves("white" if self.current_player == "black" else "black")
        for opp_move in opp_moves:
            if opp_move[2] == king_row and opp_move[3] == king_col:
                self.board[from_row][from_col] = piece
                self.board[to_row][to_col] = old_piece
                return False # not a safe move, king is in check

        self.board[from_row][from_col] = piece
        self.board[to_row][to_col] = old_piece
        return True

    def get_king_location(self):
        king_row = -1
        king_col = -1
        for i in range(8):
            for j in range(8):
                if self.board[i][j] == f"{self.current_player}_king":
                    king_row = i
                    king_col = j
                    break
        return king_col, king_row

    def get_color(self, row, col):
        if not self.board[row][col]:
            return None
        return self.board[row][col].split('_')[0]

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
