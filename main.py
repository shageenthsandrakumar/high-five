import os
from dotenv import load_dotenv
from agents.team import build_team

load_dotenv()

def main():
    print("=== High-Five Multi-Agent System ===\n")
    task = input("Enter your task: ").strip()
    if not task:
        print("No task provided.")
        return
    print("\nRunning agents...\n")
    result = build_team(task)
    print("\n=== Result ===")
    print(result)

if __name__ == "__main__":
    main()
