import os
from crew import GameBuilder

def run():

    """Run the crew to generate a game based on user input."""

    print("🎮 Welcome to the Game Builder 🎮")
    print("------------------------------------------")
    game_prompt = input("Describe the game you want to build (e.g., 'A simple Pong game'):\n>")

    inputs ={
        'game': game_prompt
    }

    try:
        print("\n🚀 Starting the Game Builder Crew. Please wait...\n")

        result = GameBuilder().crew().kickoff(inputs=inputs)

        print("\n==============================================")
        print("✅ GAME GENERATION COMPLETE!")
        print("==============================================\n")

        output_filename = "game.py"
        with open(output_filename, "w", encoding="utf-8") as f:
            # Strip out markdown formatting if the LLM adds it by mistake
            clean_code = str(result).replace("```python", "").replace("```", "").strip()
            f.write(clean_code)

    except Exception as e:
        print("Sorry could not Generate the game",e)


if __name__ == '__main__':
    run()