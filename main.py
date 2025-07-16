import chess
import chess.engine
import os
import tkinter as tk
from PIL import Image, ImageTk

# === Configuration ===
TILE_SIZE = 64
PIECE_PATH = "images/"
STOCKFISH_PATH = "C://Users/vince/Documents/stockfish/stockfish-windows-x86-64-avx2.exe"

# === Load Piece Images
def load_images():
    pieces = {}
    for color in ['w', 'b']:
        for piece in ['P', 'R', 'N', 'B', 'Q', 'K']:
            filename = f"{color}{piece}.png"
            image = Image.open(os.path.join(PIECE_PATH, filename))
            image = image.resize((TILE_SIZE, TILE_SIZE), Image.Resampling.LANCZOS)
            pieces[f"{color}{piece}"] = ImageTk.PhotoImage(image)
    return pieces

# === GUI Class ===
class ChessGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess GUI with Stockfish")
        self.canvas = tk.Canvas(root, width=8*TILE_SIZE, height=8*TILE_SIZE)
        self.canvas.pack()
        self.images = load_images()
        self.board = chess.Board()
        self.selected_square = None
        self.engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

        self.draw_board()
        self.canvas.bind("<Button-1>", self.on_click)

    def draw_board(self):
        self.canvas.delete("all")
        # colors: white, black, blue (selection), brown (last move)
        colors = ["#F0D9B5", "#B58863", "#6CB0F5", "#C1A058"]
        for rank in range(8):
            for file in range(8):
                x1 = file * TILE_SIZE
                y1 = (7 - rank) * TILE_SIZE
                x2 = x1 + TILE_SIZE
                y2 = y1 + TILE_SIZE
                square = chess.square(file, rank)
                if square is self.selected_square:
                    color = colors[2]
                else:
                    color = colors[(file + rank) % 2]
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
                piece = self.board.piece_at(chess.square(file, rank))
                if piece:
                    img_key = f"{'w' if piece.color == chess.WHITE else 'b'}{piece.symbol().upper()}"
                    self.canvas.create_image(x1, y1, anchor="nw", image=self.images[img_key])

    def on_click(self, event):
        file = event.x // TILE_SIZE
        rank = 7 - (event.y // TILE_SIZE)
        square = chess.square(file, rank)

        if self.selected_square is None:
            piece = self.board.piece_at(square)
            if piece and piece.color == chess.WHITE:  # Only allow human (white) moves
                self.selected_square = square
                self.draw_board()
        else:
            move = chess.Move(self.selected_square, square)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.selected_square = None                
                self.draw_board()
                self.root.after(200, self.engine_move)
            else:
                self.selected_square = None
                self.draw_board()

    def engine_move(self):
        if not self.board.is_game_over():
            result = self.engine.play(self.board, chess.engine.Limit(time=0.1))
            self.board.push(result.move)
            self.draw_board()

    def on_closing(self):
        self.engine.quit()
        self.root.destroy()
        
# === Run App ===
if __name__ == "__main__":
    root = tk.Tk()
    gui = ChessGUI(root)
    root.protocol("WM_DELETE_WINDOW", gui.on_closing)
    root.mainloop()