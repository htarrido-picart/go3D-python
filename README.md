# 3D Go Game

Welcome to the 3D Go Game repository! This project is an innovative take on the ancient board game Go, extending the traditional 2D board into a three-dimensional space. This new dimension adds a fresh layer of strategy and complexity, making it an exciting variant for both new players and seasoned Go enthusiasts.

## Getting Started

To start playing 3D Go on your local machine, you have two main options: running the game directly in your terminal or using a Jupyter Notebook. Both methods provide an interactive experience, allowing you to play against another player or challenge ChatGPT in a match of wits and strategy.

I highly recommend setting up an environment following the requirements.txt file.

### Requirements

- Python 3.x
- Plotly
- OpenAI API
- IPython, Numpy
- Jupyter Notebook (optional, for those who prefer a notebook interface)
- Internet connection (for playing against ChatGPT)

### Running the Game in Terminal

1. Clone this repository to your local machine.
2. Navigate to the cloned directory in your terminal.
3. Make sure you have an environment with the libraries installed.
3. Run the game by executing:

```python
python Go3D.py
```

### Running the Game in Jupyter Notebook

Open the `playgroud.ipynb` file from the cloned repository and run it.

## Playing Against ChatGPT

To enhance your 3D Go experience, you can play against ChatGPT. This requires setting up an assistant with OpenAI or Gemini and obtaining an API Key and Assistant ID. You will need to provide the instructions to the Agent on what the game is and how to play it. The game expects the agent to always responds with a move using the ‘move_srt: A1-1(THE MOVE’ format.

* I plan on converting this into a JSON soon.

### Configuration

For a secure and seamless experience, it is recommended to set your OpenAI API Key and Assistant ID as environment variables in your local development environment:

- `OPENAI_API_KEY`: Your OpenAI API Key.
- `ASSISTANT_ID`: Your Assistant ID from OpenAI or Gemini.

You can set these environment variables in your terminal session or add them to your `.bashrc`, `.zshrc`, or equivalent shell configuration file:

```bash
export OPENAI_API_KEY='your_api_key_here'
export ASSISTANT_ID='your_assistant_id_here'
```

### 1-Player mode(against ChatGPT) or 2-Player mode

Once you have configured your API Key and Assistant ID, you can start a game against ChatGPT by following the prompts in the terminal or Jupyter Notebook interface to play 1-player mode. The game will automatically use your API credentials to communicate with ChatGPT and provide a challenging AI opponent.

You can also play 2-player mode with a friend in front of the computer.

### Contribution

Contributions to the 3D Go game are welcome! Whether it's bug fixes, new features, or improvements to the existing codebase, feel free to fork this repository and submit a pull request.
License

### License: n8n

The game has a n8n license that allows for personal fun use but does not allow commercial use or distribution.
