# GameBuilder

GameBuilder is a small Python project that uses CrewAI agents to generate a complete single-file PyGame game from a natural language prompt.

## What it does

- Accepts a game idea from the user
- Sends the request through a CrewAI workflow with multiple agents:
  - Senior Software Engineer
  - QA Engineer
  - Chief QA Engineer
- Produces a runnable Python game file named `game.py`

## Project structure

- `src/main.py` - Entry point for the app
- `src/crew.py` - Defines the CrewAI agents, tasks, and workflow
- `game.py` - Generated game output

## Requirements

Make sure you have Python installed and the required packages available.

Install dependencies with:

```bash
pip install crewai python-dotenv pygame
```

## Setup

1. Open the project folder:

```bash
cd GameBuilder
```

2. Run the app:

```bash
python src/main.py
```

3. Enter a description of the game you want, for example:

```text
A simple Ping Pong game
```

The app will generate a file named `game.py` in the project folder.

## Running the generated game

After the file is created, run:

```bash
python game.py
```

## Notes

- The project uses CrewAI and an LLM-backed workflow, so you may need to configure your environment variables or API credentials for the selected model.
- The generated game is intended to be a self-contained PyGame script.
