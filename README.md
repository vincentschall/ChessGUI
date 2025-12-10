# ChessGUI
Integrating the python-chess library and stockfish into my own GUI.

## Abilities
- Play against AI (stockfish)
- Play against human (offline)
- Analyze PGN files

## Development Roadmap
- [x] Basic GUI for Board (images)
- [x] Colors and images
- [x] Making moves
- [x] Integrating stockfish
- [x] Menu
- [ ] Drag and drop
- [ ] Analyzing PGN Files

## Installation
Using conda (recommended):  
- `conda create -n chessgui python=3.12`
- `conda activate chessgui`
- `conda install python-chess pillow`  
If you want to play against an engine or analyse PGN files, you will need to download Stockfish and set the correct path to the executable at the top of main.py.  
Now you can run the app with `python3 main.py`!
