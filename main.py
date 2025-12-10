import chess
import chess.engine
import chess.pgn
import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

# === Configuration ===
TILE_SIZE = 64
PIECE_PATH = "images/"
STOCKFISH_PATH = "/home/vincent/documents/programme/stockfish/stockfish-ubuntu-x86-64-avx2"

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
    def __init__(self, root, play_vs_engine=False, pgn_path=None):
        self.root = root
        self.root.title("Chess GUI")
        self.canvas = tk.Canvas(root, width=8*TILE_SIZE, height=8*TILE_SIZE)
        self.canvas.pack()
        self.images = load_images()
        self.board = chess.Board()
        self.selected_square = None
        self.possibleSquares = []
        self.moves = []
        self.play_vs_engine = play_vs_engine
        
        if play_vs_engine:
            self.engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
        else:
            self.engine = None
        
        if pgn_path:
            with open(pgn_path, 'r') as pgn_file:
                game = chess.pgn.read_game(pgn_file)
                self.board = game.board()
                for move in game.mainline_moves():
                    self.board.push(move)   
                
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
                if square in self.possibleSquares:
                    self.draw_dot(file, rank)

    # === Event Handler ===
    def on_click(self, event):
        if self.play_vs_engine and self.board.turn == chess.BLACK:
            return
        
        file = event.x // TILE_SIZE
        rank = 7 - (event.y // TILE_SIZE)
        square = chess.square(file, rank)

        if self.selected_square is None:
            piece = self.board.piece_at(square)
            if piece and piece.color == self.board.turn:
                self.selected_square = square
                self.draw_board()
        elif self.selected_square is square:
            self.selected_square = None
            self.draw_board()
            return
        else:
            move = chess.Move(self.selected_square, square)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.selected_square = None  
                self.moves.append(move);    
                self.draw_board()
                if self.play_vs_engine:
                    self.root.after(200, self.engine_move) 
            else:
                piece = self.board.piece_at(square)
                self.selected_square = square if piece and piece.color == self.board.turn else None
                self.draw_board()

    # === Handles Engine Moves ===
    def engine_move(self):
        if not self.board.is_game_over() and self.board.turn == chess.BLACK:
            # adapt the time setting here for stronger engine performance
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
                    
    def draw_dot(self, file, rank, radius=8, color="#8B6848"):
        x = file * TILE_SIZE + TILE_SIZE // 2
        y = (7 - rank) * TILE_SIZE + TILE_SIZE // 2
        self.canvas.create_oval(
            x - radius, y - radius,
            x + radius, y + radius,
            fill=color, outline=""
        )

    # === Closing the app ===
    def on_closing(self):
        if self.engine:
            self.engine.quit()
        self.root.destroy()
        
class MainMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Menu")

        tk.Button(root, text="Play Against Human", width=30, height=2,
                  command=self.play_vs_human).pack(pady=10)

        tk.Button(root, text="Play Against Stockfish", width=30, height=2,
                  command=self.play_vs_engine).pack(pady=10)

        tk.Button(root, text="Upload PGN to Analyse", width=30, height=2,
                  command=self.upload_pgn).pack(pady=10)

    def play_vs_human(self):
        self.launch_gui(play_vs_engine=False)

    def play_vs_engine(self):
        self.launch_gui(play_vs_engine=True)

    def upload_pgn(self):
        from tkinter import filedialog
        pgn_path = filedialog.askopenfilename(filetypes=[("PGN files", "*.pgn")])
        if pgn_path:
            self.launch_gui(play_vs_engine=False, pgn_path=pgn_path)

    def launch_gui(self, play_vs_engine=False, pgn_path=None):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.gui = ChessGUI(self.root, play_vs_engine, pgn_path)
        self.root.protocol("WM_DELETE_WINDOW", self.gui.on_closing)

# === Run App ===
if __name__ == "__main__":
    root = tk.Tk()
    menu = MainMenu(root)
    root.mainloop()
