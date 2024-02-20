
import GameController as go


print("welcome to 3d go. the real 3-dimensional chess. v1.0 by @htarrido-picart\n")
board_size = int(input("What board size would you like to play? (3,4,5): "))
game = go.GameController(board_size)
game.play_game()
