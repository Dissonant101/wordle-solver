#!/usr/bin/env python3
"""
Command-line interface for the Wordle solver.
"""

import argparse
import sys
from wordle_solver import WordleSolver


def parse_positions(positions_str):
    """Parse position string like '0:a,2:r,4:e' into dict."""
    if not positions_str:
        return {}
    
    positions = {}
    for pair in positions_str.split(','):
        try:
            pos, letter = pair.split(':')
            positions[int(pos)] = letter.lower()
        except ValueError:
            print(f"Invalid position format: {pair}. Use format like '0:a,2:r'")
            sys.exit(1)
    return positions


def parse_letters(letters_str):
    """Parse letter string like 'a,b,c' into set."""
    if not letters_str:
        return set()
    return set(letter.lower() for letter in letters_str.split(','))


def parse_wrong_positions(wrong_positions_str):
    """Parse wrong positions string like 'a:1,3;b:0,2' into dict."""
    if not wrong_positions_str:
        return {}
    
    wrong_positions = {}
    for letter_group in wrong_positions_str.split(';'):
        try:
            letter, positions = letter_group.split(':')
            wrong_positions[letter.lower()] = set(int(pos) for pos in positions.split(','))
        except ValueError:
            print(f"Invalid wrong position format: {letter_group}. Use format like 'a:1,3;b:0,2'")
            sys.exit(1)
    return wrong_positions


def main():
    parser = argparse.ArgumentParser(description='Wordle Solver - Find the best word guesses')
    parser.add_argument('--words', default='words.csv', 
                       help='Path to CSV file containing possible words (default: words.csv)')
    parser.add_argument('--correct-positions', 
                       help='Correct letters in correct positions (green). Format: 0:a,2:r,4:e')
    parser.add_argument('--correct-letters', 
                       help='Correct letters in wrong positions (yellow). Format: a,b,c')
    parser.add_argument('--incorrect-letters', 
                       help='Incorrect letters (gray). Format: x,y,z')
    parser.add_argument('--wrong-positions', 
                       help='Letters in wrong positions. Format: a:1,3;b:0,2')
    parser.add_argument('--max-results', type=int, default=20,
                       help='Maximum number of results to show (default: 20)')
    parser.add_argument('--best-only', action='store_true',
                       help='Show only the best guess')
    parser.add_argument('--stats', action='store_true',
                       help='Show statistics about the word list')
    parser.add_argument('--interactive', action='store_true',
                       help='Run in interactive mode')
    
    args = parser.parse_args()
    
    # Initialize solver
    solver = WordleSolver(args.words)
    
    if args.stats:
        stats = solver.get_stats()
        print("Word List Statistics:")
        print(f"  Total words: {stats['total_words']}")
        print(f"  Unique letters: {stats['unique_letters']}")
        print(f"  Average word length: {stats['avg_word_length']:.1f}")
        return
    
    if args.interactive:
        run_interactive(solver)
        return
    
    # Parse command line arguments
    correct_positions = parse_positions(args.correct_positions)
    correct_letters = parse_letters(args.correct_letters)
    incorrect_letters = parse_letters(args.incorrect_letters)
    wrong_positions = parse_wrong_positions(args.wrong_positions)
    
    # Solve
    if args.best_only:
        best_guess = solver.get_best_guess(correct_positions, correct_letters, 
                                         incorrect_letters, wrong_positions)
        if best_guess:
            print(f"Best guess: {best_guess.upper()}")
        else:
            print("No valid words found with given constraints.")
    else:
        results = solver.solve(correct_positions, correct_letters, incorrect_letters, 
                             wrong_positions, args.max_results)
        
        if results:
            print(f"Top {len(results)} possibilities:")
            for i, (word, probability) in enumerate(results, 1):
                print(f"{i:2d}. {word.upper()} (score: {probability:.6f})")
        else:
            print("No valid words found with given constraints.")


def run_interactive(solver):
    """Run the solver in interactive mode."""
    print("=== Wordle Solver Interactive Mode ===")
    print("Enter your constraints. Leave blank to skip a constraint type.")
    print("Positions are numbered 0-4 (left to right).")
    print()
    
    while True:
        print("\n--- New Wordle Puzzle ---")
        
        # Get correct positions (green letters)
        correct_pos_input = input("Correct positions (green letters, format: 0:a,2:r): ").strip()
        correct_positions = parse_positions(correct_pos_input) if correct_pos_input else {}
        
        # Get correct letters in wrong positions (yellow letters)
        correct_letters_input = input("Correct letters in wrong positions (yellow, format: a,b,c): ").strip()
        correct_letters = parse_letters(correct_letters_input) if correct_letters_input else set()
        
        # Get incorrect letters (gray letters)
        incorrect_letters_input = input("Incorrect letters (gray, format: x,y,z): ").strip()
        incorrect_letters = parse_letters(incorrect_letters_input) if incorrect_letters_input else set()
        
        # Get wrong positions for yellow letters
        wrong_pos_input = input("Wrong positions for yellow letters (format: a:1,3;b:0,2): ").strip()
        wrong_positions = parse_wrong_positions(wrong_pos_input) if wrong_pos_input else {}
        
        # Solve
        results = solver.solve(correct_positions, correct_letters, incorrect_letters, 
                             wrong_positions, max_results=10)
        
        if results:
            print(f"\nTop {len(results)} possibilities:")
            for i, (word, probability) in enumerate(results, 1):
                print(f"{i:2d}. {word.upper()} (score: {probability:.6f})")
        else:
            print("No valid words found with given constraints.")
        
        # Ask if user wants to continue
        continue_input = input("\nSolve another puzzle? (y/n): ").strip().lower()
        if continue_input != 'y' and continue_input != 'yes':
            break
    
    print("Thanks for using Wordle Solver!")


if __name__ == "__main__":
    main()
