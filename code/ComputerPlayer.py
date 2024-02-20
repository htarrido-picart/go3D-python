import re, time
from openai import OpenAI
import os
ASSISTANT_API = os.environ['ASSISTANT_API']
client = OpenAI()

class ComputerGPTPlayer():
    def __init__(self,
                 mode: str,
                 board_size: int,
                 gpt_stone_color: str,
                 assistant_id = ASSISTANT_API):
        self.assistant_id = assistant_id
        self.thread = client.beta.threads.create()
        self.mode = mode
        self.board_size = board_size
        self.gpt_stone_color = gpt_stone_color

    def extract_assistant_move_str(self, input_str) -> str:
        """
        Extracts the substring that follows 'move_str:' in the given input string.

        Parameters:
        - input_str (str): The input string containing the 'move_str:' pattern.

        Returns:
        - str: The substring following 'move_str:', or None if the pattern is not found.
        """

        # Define a regular expression pattern to find 'move_str:' followed by any non-space characters
        pattern = re.compile(r'move_str:\s*(\S+)')

        # Search for the pattern in the input string
        match = pattern.search(input_str)

        # If a match is found, return the capturing group which contains the string after 'move_str:'
        if match:
            return match.group(1)

        # Return None if no match is found
        return None

    def get_assistant_message(self, messages) -> str:
        """
        Retrieves the 'value' from the most recent assistant message.

        Parameters:
        - messages (list): A list of ThreadMessage objects returned from the API.

        Returns:
        - str: The 'value' from the most recent assistant message, or None if there are no assistant messages.
        """

        # Filter messages to only include those from the assistant
        assistant_messages = [msg for msg in messages if msg.role == 'assistant']

        # Sort the assistant messages by 'created_at' in descending order
        assistant_messages.sort(key=lambda x: x.created_at, reverse=True)

        # Get the most recent assistant message, if any
        if assistant_messages:
            latest_message = assistant_messages[0]
            # Assuming there's at least one content item and it's of type 'text'
            if latest_message.content and latest_message.content[0].type == 'text':
                move = self.extract_assistant_move_str(latest_message.content[0].text.value)
                print(move)
                return move

            else:
                print(latest_message)
                time.sleep(5)

        return None

    def run_status(self, run):
        # Waits for the run to be completed.
        while True:
            run_status = client.beta.threads.runs.retrieve(thread_id=self.thread.id,
                                                           run_id=run.id)
            print(run_status.status)
            if run_status.status == "completed":
                break
            elif run_status.status == "failed":
                print("Run failed:", run_status.last_error)
                break
            time.sleep(2)  # wait for 2 seconds before checking again

    def get_play(self, move_str, board, board_history, captured_stones) -> str:

        oponent_move_msg = f"The oponent made {move_str}. "
        captured_stone_msg = f"The move caused stones to be captured: {captured_stones}" if not captured_stones.black or captured_stones.white else ""
        board_status_msg = f"The current board looks like this: {board}. "
        move_history = f"This is the history of moves, that has led to the current board status: {board_history}."

        message_payload = ''.join([oponent_move_msg,captured_stone_msg, board_status_msg, move_history])

        print(message_payload)

        time.sleep(5)

        message = client.beta.threads.messages.create(thread_id=self.thread.id,
                                                      role="user",
                                                      content=message_payload)

        run = client.beta.threads.runs.create(thread_id=self.thread.id,
                                              assistant_id=self.assistant_id,
                                             instructions=f'You are playing in {self.mode} mode as {self.gpt_stone_color} stone colors a {self.board_size}x{self.board_size}x{self.board_size} Go Game. You always respond with "move_str: MYMOVE", where MYMOVE is your move.')

        self.run_status(run)

        messages = client.beta.threads.messages.list(thread_id=self.thread.id)

        gpt_move_str = self.get_assistant_message(messages)

        return gpt_move_str
