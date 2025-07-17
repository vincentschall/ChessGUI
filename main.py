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
    
    # === Initialize global variables ===
    def __init__(self, root):
        self.root = root
        self.root.title("Chess GUI with Stockfish")
        self.canvas = tk.Canvas(root, width=8*TILE_SIZE, height=8*TILE_SIZE)
        self.canvas.pack()
        self.images = load_images()
        self.board = chess.Board()
        self.selected_square = None
        self.possibleSquares = []
        self.engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
        self.moves = []
        self.draw_board()
        self.canvas.bind("<Button-1>", self.on_click)

    # === (Re-)draws the board ===
    def draw_board(self):
        self.canvas.delete("all")
        self.updatePossibleMoves()
        # colors:
        # light squares, dark squares
        # selected square
        # light square (last move), dark square (last move)
        # king in check
        colors = ["#F0D9B5", "#B58863", "#6CB0F5", "#FFD474", "#C1A058", "#FF5454"]
        
        if self.moves:
            last_move = self.moves[-1]
            from_file = chess.square_file(last_move.from_square)
            from_rank = chess.square_rank(last_move.from_square)
            to_file = chess.square_file(last_move.to_square)
            to_rank = chess.square_rank(last_move.to_square)          
            
        for rank in range(8):
            for file in range(8):
                x1 = file * TILE_SIZE
                y1 = (7 - rank) * TILE_SIZE
                x2 = x1 + TILE_SIZE
                y2 = y1 + TILE_SIZE
                square = chess.square(file, rank)
                if square is self.selected_square:
                    color = colors[2]
                elif self.moves and ((file == from_file and rank == from_rank) or (file == to_file and rank == to_rank)):
                    color = colors[((file + rank) % 2) + 3]                 
                else:
                    color = colors[(file + rank) % 2]
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
                piece = self.board.piece_at(chess.square(file, rank))
                if piece:
                    img_key = f"{'w' if piece.color == chess.WHITE else 'b'}{piece.symbol().upper()}"
                    self.canvas.create_image(x1, y1, anchor="nw", image=self.images[img_key])

    # === Event Handler ===
    def on_click(self, event):
        file = event.x // TILE_SIZE
        rank = 7 - (event.y // TILE_SIZE)
        square = chess.square(file, rank)

        if self.selected_square is None:
            piece = self.board.piece_at(square)
            if piece and piece.color == chess.WHITE:
                self.selected_square = square
                self.draw_board()
        else:
            move = chess.Move(self.selected_square, square)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.selected_square = None  
                self.moves.append(move);    
                self.draw_board()
                self.root.after(200, self.engine_move) 
            else:
                piece = self.board.piece_at(square)
                if piece and piece.color == chess.WHITE:
                    self.selected_square = square
                else:
                    self.selected_square = None
                self.draw_board()

    # === Handles Engine Moves ===
    def engine_move(self):
        if not self.board.is_game_over():
            result = self.engine.play(self.board, chess.engine.Limit(time=0.1))
            move = result.move
            self.moves.append(move)
            self.board.push(move)
            self.draw_board()
            
    def updatePossibleMoves(self):
        self.possibleSquares = []
        if self.selected_square:
            legal_moves = self.board.legal_moves
            for move in legal_moves:
                if self.selected_square is move.from_square:
                    self.possibleSquares.append(move.to_square)

    # === Closing the app ===
    def on_closing(self):
        self.engine.quit()
        self.root.destroy()
        
# === Run App ===
if __name__ == "__main__":
    root = tk.Tk()
    gui = ChessGUI(root)
    root.protocol("WM_DELETE_WINDOW", gui.on_closing)
    root.mainloop()