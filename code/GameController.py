import numpy as np
import ComputerPlayer as gpt_player
import Board as game
import time

class GameController:
    def __init__(self,
                board_size,
                display_mode_view = '3d',
                captured_stones = {"black": 0, "white": 0},
                territory = {'black': 0, 'white': 0},
                board_history = []):
        #player
        self.player_mode = 0
        self.computerPlayer = None
        self.current_player = None

        self.opponent_color = None
        #board
        self.board_size = board_size
        self.board = np.zeros((board_size, board_size, board_size))
        self.captured_stones = captured_stones # Initialize captured stone counters for both players
        self.territory = territory

        # board history and last move tracker
        self.board_history = board_history
        self.last_stone_captured = []
        self.last_move: str = ""
        self.last_move_player = None

        #global coordinate system
        self.directions = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
        # Track consecutive passes
        self.pass_count = 0
        # Display in 3D by default
        self.display_mode_view = display_mode_view

        #End game
        self.pass_status = {'black': False, 'white': False}  # Track if each player has passed their last turn
        self.game_over = False

    def track_captured_stones(self, board_past, board_present):
        """Track the number of captured stones for each player."""
        # Assuming 'captured_stones' is a dictionary initialized in __init__ to track the count for each player
        black_stones_before = np.sum(board_past == 1)
        white_stones_before = np.sum(board_past == 2)

        # Update the board based on the 'is_captured' checks within the 'make_move' or similar method

        black_stones_after = np.sum(board_present == 1)
        white_stones_after = np.sum(board_present == 2)

        # Calculate the number of stones captured during the last move
        black_captured = white_stones_before - white_stones_after  # Stones captured by Black
        white_captured = black_stones_before - black_stones_after  # Stones captured by White

        # Update the captured stones count
        self.captured_stones['black'] += black_captured
        self.captured_stones['white'] += white_captured

        print(f"Captured stones - Black: {self.captured_stones['black']}, White: {self.captured_stones['white']}")

    def make_move(self, move_str, current_player):
        player_id = 1 if current_player == "black" else 2

        try:
            # Convert move string to coordinates
            x, y, z = self.parse_move(move_str)
        except ValueError:
            print("Invalid move format. Please use the format 'LetterNumber-Number' (e.g., 'A1-1').")
            return False

        if not self.is_valid_move(x, y, z):
            return False

        if self.is_suicidal_move(x, y, z, player_id):
            print("Invalid move: Placing a stone here would result in suicide. Please try again.")

            return False
        # Update the board, check for captures
        board_prior_move = self.board
        self.board[x, y, z] = player_id
        captured = self.is_captured(current_player, move_str)

        # Provide feedback on the move result
        if captured:
            print(f"Move at {move_str} resulted in a capture.")
            self.track_captured_stones(board_past = board_prior_move, board_present = self.board)
        else:
            print(f"Move at {move_str} did not result in a capture.")

        self.board_history.append(move_str)

        return True

    def parse_move(self, move):
        col_str, z_str = move.upper().split('-')
        x = ord(col_str[0]) - ord('A')
        y = int(col_str[1:]) - 1
        z = int(z_str) - 1
        return x, y, z

    def is_valid_move(self, x, y, z):
        # Check if the move is within the board and the position is not already occupied
        if 0 <= x < self.board_size and 0 <= y < self.board_size and 0 <= z < self.board_size and self.board[x, y, z] == 0:
            return True
        print("Invalid move: Position is either out of bounds or already occupied.")
        return False

    def is_suicidal_move(self, x, y, z, player_id):
        # Temporarily place the stone on the board to assess the move
        self.board[x, y, z] = player_id
        connected_stones = self.find_connected_stones(x, y, z, player_id)

        # Check if placing this stone captures any opponent stones
        captures_opponent = self.check_for_opponent_capture(x, y, z, player_id)

        if not self.has_liberty(connected_stones) and not captures_opponent:
            # Revert the move since it's considered self-capture
            self.board[x, y, z] = 0
            return True  # The move is self-capture

        # Revert the move after assessment
        self.board[x, y, z] = 0
        return False  # The move is not self-capture

    def check_for_opponent_capture(self, x, y, z, player_id):
        opponent = 3 - player_id
        captures_opponent = False
        for dx, dy, dz in self.directions:
            nx, ny, nz = x + dx, y + dy, z + dz
            if self.is_opponent_stone(nx, ny, nz, opponent):
                opponent_connected_stones = self.find_connected_stones(nx, ny, nz, opponent)
                if not self.has_liberty(opponent_connected_stones):
                    captures_opponent = True
                    break  # No need to check further if an opponent's stone is captured
        return captures_opponent

    def is_captured(self, current_player, move_str):
        player_id = 1 if current_player == "black" else 2
        print(f"\n--- Checking captures for move: {move_str} ---")

        x, y, z = self.parse_move(move_str)
        opponent = 3 - player_id
        print(f"Current player: {current_player}, Opponent: {opponent}")

        captured = False
        for dx, dy, dz in self.directions:
            nx, ny, nz = x + dx, y + dy, z + dz
            if self.is_opponent_stone(nx, ny, nz, opponent):
                connected_stones = self.find_connected_stones(nx, ny, nz, opponent)
                if not self.has_liberty(connected_stones):
                    print(f"Capturing opponent's stones connected to ({nx}, {ny}, {nz})")
                    self.update_board(connected_stones)
                    self.last_stone_captured.extend(connected_stones)
                    captured = True

        print(f"Capture result for move {move_str}: {'Captured' if captured else 'Not Captured'}")
        return captured

    def is_opponent_stone(self, x, y, z, opponent):
        return 0 <= x < self.board_size and 0 <= y < self.board_size and 0 <= z < self.board_size and self.board[x, y, z] == opponent

    def find_connected_stones(self, start_x, start_y, start_z, player) -> set():
        """Find all stones connected to the starting stone of the same player."""
        stack = [(start_x, start_y, start_z)]
        connected = set()
        while stack:
            x, y, z = stack.pop()
            if (x, y, z) in connected or not (0 <= x < self.board_size and 0 <= y < self.board_size and 0 <= z < self.board_size):
                continue
            if self.board[x, y, z] == player:
                connected.add((x, y, z))
                stack.extend([(x + dx, y + dy, z + dz) for dx, dy, dz in self.directions])
        return connected

    def has_liberty(self, stones):
        """Check if the group of stones has any liberty."""
        for x, y, z in stones:
            for dx, dy, dz in self.directions:
                nx, ny, nz = x + dx, y + dy, z + dz
                if 0 <= nx < self.board_size and 0 <= ny < self.board_size and 0 <= nz < self.board_size and self.board[nx, ny, nz] == 0:
                    print(f"Liberty found at ({nx}, {ny}, {nz}) for stones.")
                    return True
        print("No liberties found")
        return False

    def update_board(self, stones):
        for x, y, z in stones:
            self.board[x, y, z] = 0

    def calculate_territory_score(self):
        def check_territory(x, y, z, visited):
            if (x, y, z) in visited:
                return True  # Already visited this empty point
            if not (0 <= x < self.board_size and 0 <= y < self.board_size and 0 <= z < self.board_size):
                return False  # Out of bounds, so not a closed territory

            visited.add((x, y, z))  # Mark this empty point as visited

            if self.board[x, y, z] > 0:
                return self.board[x, y, z]  # Return player number if stone is encountered

            # Check all surrounding points to see if they are enclosed by one player
            results = [check_territory(x + dx, y + dy, z + dz, visited) for dx, dy, dz in self.directions]
            if all(result == results[0] for result in results if result is not False):
                return results[0]  # All surrounding points are owned by the same player
            return False  # Surrounding points are not owned by a single player

        # Analyze each empty point on the board
        empty_points = np.argwhere(self.board == 0)
        for x, y, z in empty_points:
            visited = set()
            owner = check_territory(x, y, z, visited)
            if owner and owner is not False:
                self.territory['black' if owner == 1 else 'white'] += len(visited)

        print(f"Territory score - Black: {self.territory['black']}, White: {self.territory['white']}")
        return self.territory

    def determine_winner(self):
        # Territory captured
        final_scores = self.calculate_territory_score()
        black_score, white_score = final_scores['black'], final_scores['white']

        # Determine the winner based on final scores
        if black_score > white_score:
            print(f"Game over. Black wins by {black_score - white_score} point(s).")
        elif white_score > black_score:
            print(f"Game over. White wins by {white_score - black_score} point(s).")
        else:
            print("Game over. It's a tie!")

    def start_computer(self, player_mode):
        if player_mode == 1:
            computer_level = input("How hard should the computer play? easy, medium, hard")
            if computer_level in ['easy', 'medium', 'hard']:
                print(f"You will be playing ChatGPT in {computer_level} mode")
                return gpt_player.ComputerGPTPlayer(mode = computer_level,
                                                            board_size = self.board_size,
                                                            gpt_stone_color = self.opponent_color)

    def gpt_computer(self):
        while True:
            player_mode = int(input("Play against ChatGPT(1) or A physical opoonent(2) mode?"))
            self.player_mode = player_mode

            if player_mode == 1:
                return self.start_computer(self.player_mode)
            if player_mode  == 2:
                return None
            else:
                print("Invalid choice. Please type 1 for playing against ChatGPT or 2 to play with a friend.")

    def check_move(self, move_str):
        try:
            valid_choices = ['2d', '3d', 'c', 'q', 'p', 'f', 't']

            if move_str.lower() in valid_choices:
                return True  # Valid command, proceed with the game logic associated with this command

            # If the command is potentially a board move (e.g., 'A1-1')
            elif '-' in move_str and len(move_str.split('-')) == 2:
                col_str, z_str = move_str.upper().split('-')
                if col_str[0].isalpha() and col_str[1:].isdigit() and z_str.isdigit():
                    # Basic format check passed, further validation required in other methods (e.g., within bounds)
                    return True

            else:
                # Invalid command, print options and return False
                print("""Invalid choice.
                        Your choices are: \(n)(2d) for a 2D Board\(n)(3d) for a 3D board\(n)(c) for the game commands\(n)(p) to pass\(n)(f) to forfeit the game\(n)(status) to get the territory status\(n)Or make a move in the format 'LetterNumber-Number' (e.g., 'A1-1') for 3D board.""")
                return False

        except ValueError:
            print("Invalid choice. Cannot submit None or nothing to move.")
            return False

    def switch_turns(self, move_str):
        self.last_move = move_str
        self.last_move_player = self.current_player
        self.current_player = "white" if self.current_player == "black" else "black"  # Switch players

    def pass_check(self, current_player, move_str):
        self.pass_status[current_player] = True  # Mark this player as having passed
        if all(self.pass_status.values()):  # Check if both players have passed consecutively
            print("Both players have passed consecutively. The game ends.")
            self.determine_winner()
            self.game_over = True
        else:
            # If only one player has passed, switch turns
            self.switch_turns(move_str)

    def play_game(self):
#        Ask the user if they want to go first (as Black)
        while True:
            first_player_choice = input("\nDo you want to go first (black stones)? (y/n): ").strip().lower()
            if first_player_choice in ["y", "n"]:
                break
            print("Invalid choice. Please type 'y','yes' or 'n','no'.")

        # Assign colors based on the user's choice
        if first_player_choice == "y":
            user_color = "black"
            self.opponent_color = "white"
        else:
            user_color = "white"
            self.opponent_color = "black"

        print(f"\nYou are playing as {user_color}. The opponent is {self.opponent_color}.")

        self.current_player = "black"  # The game always starts with Black stones

        #choose plaing player_mode
        computer = self.gpt_computer()

        #allow player to choose display mode
        while True:
            if not self.display_mode_view:
                display_mode_view = input("\nChoose your board display mode (2D/3D): ").strip().lower()
                self.display_mode_view = display_mode_view

                if self.display_mode_view in ["2d", "3d"]:
                    break
                print("Invalid choice. Please type '2D' or '3D'.")

            break

        current_game = game.Board(board = self.board,
                                board_size = self.board_size,
                                last_move= self.last_move,
                                current_player = self.current_player,
                                display_mode_view = self.display_mode_view)

        current_game.display_board(None, None)

        while not self.game_over:
            current_game.display_board(self.last_move, self.last_move_player)

            move_str = computer.get_play(self.last_move, self.board, self.board_history, self.captured_stones) if self.player_mode == 1 and self.current_player == self.opponent_color else input(f"""Player {self.current_player}'s turn. Enter your move (e.g., A1-1) or c for more commands: """)

            while self.check_move(move_str):
                if move_str == "2d":
                    self.display_mode_view = '2d'
                    break
                if move_str == "3d":
                    self.display_mode_view = '3d'
                    break
                if move_str.lower() == 'c':
                    print("The game has extra commands: \n'q' to quit\n'f' to forfeit\n'p' to pass\n't' to check game status\n'2d' for 2-dimensional board view\n'3d' for 3-dimensional board view")
                    time.sleep(5)
                    break

                if move_str.lower() == 'q':
                    print(f"Game quit by {self.current_player}. Thanks for playing!")
                    print(f"The score at this moment was: \n {self.calculate_territory_score()}")
                    self.game_over = True
                    break

                if move_str.lower() in 't':
                    print("Current game status:")
                    print(f"Captured stones - Black: {self.captured_stones['black']}, White: {self.captured_stones['white']}")
                    time.sleep(5)
                    break

                if move_str.lower() == 'f':
                    print(f"Player {self.current_player} has forfeit the game.")
                    print(f"The score at this moment was: \n {self.calculate_territory_score()}")
                    self.game_over = True
                    break

                if move_str.lower() == 'p':
                    self.pass_check(self.current_player, move_str)
                    break

                else:
                    self.pass_status = {'black': False, 'white': False}
                    if self.make_move(move_str, self.current_player):
                        self.switch_turns(move_str)
                        break

                    else:
                        print("Try again...")
                        break

# if __name__ == "__main__":
#     print("welcome to 3d go. the real 3-dimensional chess. v1.0 by @htarrido-picart\n")
#     board_size = int(input("What board size would you like to play? (3,4,5): "))
#     session = GameController(board_size)
#     session.play_game()
