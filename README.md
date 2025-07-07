# Wordle Solver

A Python-based Wordle solver that helps you find the best possible words based on your game constraints. The solver uses statistical analysis of letter frequencies and positions to rank possible answers by probability.

## Features

- **Constraint-based filtering**: Input green letters (correct position), yellow letters (wrong position), and gray letters (not in word)
- **Probability ranking**: Words are ranked by likelihood based on letter frequency analysis
- **Handles duplicate letters**: Correctly processes words with repeated characters like "poppy"
- **Multiple interfaces**: Command-line arguments, interactive mode, and Python API
- **Customizable word lists**: Use your own CSV file of possible words

## Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd wordle-solver
   ```

2. Make sure you have Python 3.6+ installed.

3. The solver uses only standard library modules, so no additional dependencies are required.

## Usage

### Command Line Interface

#### Basic Usage

```bash
# Get the best guess only
python cli.py --best-only

# Get top 10 possibilities
python cli.py --max-results 10

# Show statistics about the word list
python cli.py --stats
```

#### With Constraints

```bash
# Green letters (correct position): 'a' at position 0, 'r' at position 2
python cli.py --correct-positions "0:a,2:r"

# Yellow letters (wrong position): letters 'e' and 't' are in the word
python cli.py --correct-letters "e,t"

# Gray letters (not in word): letters 'x', 'y', 'z' are not in the word
python cli.py --incorrect-letters "x,y,z"

# Yellow letters with position constraints: 'a' is in the word but not at positions 1,3
python cli.py --wrong-positions "a:1,3"

# Combine multiple constraints
python cli.py --correct-positions "0:s,4:e" --incorrect-letters "a,i,o,u" --max-results 5
```

#### Interactive Mode

```bash
python cli.py --interactive
```

This will prompt you for each type of constraint and show the results.

### Python API

```python
from wordle_solver import WordleSolver

# Initialize solver with default word list
solver = WordleSolver()

# Or use a custom word list
solver = WordleSolver("my_words.csv")

# Define constraints
correct_positions = {0: 's', 4: 'e'}  # 's' at position 0, 'e' at position 4
correct_letters = {'a', 'r'}          # 'a' and 'r' are in the word
incorrect_letters = {'i', 'o', 'u'}   # 'i', 'o', 'u' are not in the word
wrong_positions = {'a': {1, 3}}       # 'a' is in the word but not at positions 1 or 3

# Get ranked possibilities
results = solver.solve(
    correct_positions=correct_positions,
    correct_letters=correct_letters,
    incorrect_letters=incorrect_letters,
    wrong_positions=wrong_positions,
    max_results=10
)

# Print results
for word, probability in results:
    print(f"{word.upper()}: {probability:.6f}")

# Get just the best guess
best_guess = solver.get_best_guess(
    correct_positions=correct_positions,
    correct_letters=correct_letters,
    incorrect_letters=incorrect_letters,
    wrong_positions=wrong_positions
)
print(f"Best guess: {best_guess.upper()}")
```

## Constraint Types

### Green Letters (Correct Position)
Letters that are in the correct position in the word.
- **Format**: `position:letter` (position is 0-4)
- **Example**: `0:a,2:r,4:e` means 'a' at position 0, 'r' at position 2, 'e' at position 4

### Yellow Letters (Wrong Position)
Letters that are in the word but in the wrong position.
- **Correct Letters**: Use this for letters you know are in the word but don't know the exact position
- **Wrong Positions**: Use this for letters you know are in the word AND know specific positions where they don't belong

### Gray Letters (Not in Word)
Letters that are not in the word at all.
- **Format**: `letter,letter,letter`
- **Example**: `x,y,z` means 'x', 'y', and 'z' are not in the word

## Examples

### Example 1: Basic Usage
You tried "CRANE" and got:
- C: Gray (not in word)
- R: Yellow (in word, wrong position)
- A: Green (correct position)
- N: Gray (not in word)
- E: Yellow (in word, wrong position)

```bash
python cli.py --correct-positions "2:a" --correct-letters "r,e" --incorrect-letters "c,n" --wrong-positions "r:1;e:4"
```

### Example 2: Duplicate Letters
You tried "POPPY" and got:
- P: Green (position 0)
- O: Gray (not in word)
- P: Yellow (in word, wrong position)
- P: Yellow (in word, wrong position)
- Y: Gray (not in word)

```bash
python cli.py --correct-positions "0:p" --wrong-positions "p:2,3" --incorrect-letters "o,y"
```

### Example 3: Multiple Constraints
After several guesses, you know:
- Position 0: S (green)
- Position 4: E (green)
- Contains: A, R (yellow)
- Doesn't contain: I, O, U, N, T
- A is not at position 1 or 3
- R is not at position 2

```bash
python cli.py --correct-positions "0:s,4:e" --correct-letters "a,r" --incorrect-letters "i,o,u,n,t" --wrong-positions "a:1,3;r:2"
```

## Word List Format

The solver expects a CSV file with one word per line. The default file is `words.csv`. Each word should be:
- Exactly 5 letters long
- Contain only alphabetic characters
- One word per line (first column if multiple columns)

Example `words.csv`:
```
about
above
abuse
actor
...
```

## Algorithm

The solver uses a two-step process:

1. **Constraint Filtering**: Eliminates words that don't satisfy the given constraints
2. **Probability Ranking**: Ranks remaining words based on:
   - Letter frequency in the word list
   - Position-specific letter frequency
   - Slight penalty for repeated letters

The probability calculation considers both the overall frequency of letters and their frequency at specific positions, giving higher scores to words with more common letter patterns.

## Files

- `wordle_solver.py`: Main solver class with all the logic
- `cli.py`: Command-line interface
- `words.csv`: Default word list (538 common 5-letter words)
- `README.md`: This documentation
- `test_solver.py`: Test suite (if you want to run tests)

## Tips for Best Results

1. **Start with common letters**: Words with common letters like E, A, R, I, O, T are often good starting guesses
2. **Use the interactive mode**: It's easier to input constraints interactively
3. **Update constraints incrementally**: After each guess, add the new information to narrow down possibilities
4. **Consider word frequency**: The solver ranks by probability, so higher-ranked words are more likely to be correct

## License

This project is open source and available under the MIT License.
