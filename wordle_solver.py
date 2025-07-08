import csv
import re
from collections import Counter, defaultdict
from typing import List, Dict, Set, Tuple
import string


class WordleSolver:
    def __init__(self, words_file: str = "words.csv"):
        """
        Initialize the Wordle solver with a list of possible words.

        Args:
            words_file: Path to CSV file containing possible Wordle answers
        """
        self.words = self._load_words(words_file)
        self.letter_frequencies = self._calculate_letter_frequencies()
        self.position_frequencies = self._calculate_position_frequencies()

    def _load_words(self, words_file: str) -> List[str]:
        """Load words from CSV file."""
        words = []
        try:
            with open(words_file, 'r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    if row:  # Skip empty rows
                        word = row[0].strip().lower()
                        if len(word) == 5 and word.isalpha():  # Ensure 5-letter words
                            words.append(word)
        except FileNotFoundError:
            print(f"Warning: {words_file} not found. Using empty word list.")
            words = []
        return words

    def _calculate_letter_frequencies(self) -> Dict[str, float]:
        """Calculate frequency of each letter across all words."""
        letter_count = Counter()
        total_letters = 0

        for word in self.words:
            for letter in word:
                letter_count[letter] += 1
                total_letters += 1

        return {letter: count / total_letters for letter, count in letter_count.items()}

    def _calculate_position_frequencies(self) -> Dict[int, Dict[str, float]]:
        """Calculate frequency of each letter at each position."""
        position_counts = defaultdict(Counter)

        for word in self.words:
            for pos, letter in enumerate(word):
                position_counts[pos][letter] += 1

        # Convert to frequencies
        position_frequencies = {}
        for pos in range(5):
            total = sum(position_counts[pos].values())
            position_frequencies[pos] = {
                letter: count / total
                for letter, count in position_counts[pos].items()
            }

        return position_frequencies

    def filter_words(self,
                     correct_positions: Dict[int, str] = None,
                     correct_letters: List[str] = None,
                     incorrect_letters: List[str] = None,
                     wrong_positions: Dict[str, Set[int]] = None) -> List[str]:
        """
        Filter words based on Wordle constraints.

        Args:
            correct_positions: Dict mapping position (0-4) to correct letter
            correct_letters: List of letters that are in the word but position unknown
            incorrect_letters: List of letters that are not in the word
            wrong_positions: Dict mapping letter to set of positions where it's NOT located
                           (but the letter is in the word somewhere else)

        Returns:
            List of words that satisfy all constraints
        """
        if correct_positions is None:
            correct_positions = {}
        if correct_letters is None:
            correct_letters = []
        if incorrect_letters is None:
            incorrect_letters = []
        if wrong_positions is None:
            wrong_positions = {}

        filtered_words = []

        for word in self.words:
            if self._satisfies_constraints(word, correct_positions, correct_letters,
                                           incorrect_letters, wrong_positions):
                filtered_words.append(word)

        return filtered_words

    def _satisfies_constraints(self, word: str,
                               correct_positions: Dict[int, str],
                               correct_letters: List[str],
                               incorrect_letters: List[str],
                               wrong_positions: Dict[str, Set[int]]) -> bool:
        """Check if a word satisfies all given constraints."""

        # Check correct positions (green letters)
        for pos, letter in correct_positions.items():
            if word[pos] != letter:
                return False

        # Check that all correct letters are in the word
        word_letter_count = Counter(word)
        for letter in correct_letters:
            if letter not in word_letter_count:
                return False

        # Check incorrect letters (gray letters)
        for letter in incorrect_letters:
            if letter in word and letter not in correct_letters and letter not in wrong_positions and letter not in correct_positions.values():
                return False

        # Check wrong positions (yellow letters)
        for letter, wrong_pos_set in wrong_positions.items():
            if letter not in word:
                return False
            for pos in wrong_pos_set:
                if word[pos] == letter:
                    return False

        # Additional constraint: ensure we have the right count of each letter
        # This handles cases where a letter appears multiple times
        for letter, count in word_letter_count.items():
            if count < sum(1 for val in correct_positions.values() if val == letter) + correct_letters.count(letter):
                return False
            if letter in incorrect_letters and count >= incorrect_letters.count(letter) + sum(1 for val in correct_positions.values() if val == letter) + correct_letters.count(letter):
                return False

        return True

    def calculate_word_probability(self, word: str) -> float:
        """
        Calculate probability score for a word based on letter and position frequencies.
        Higher score means more likely to be the answer.
        """
        score = 1.0

        # Factor in position-specific frequencies
        for pos, letter in enumerate(word):
            if letter in self.position_frequencies[pos]:
                score *= self.position_frequencies[pos][letter]
            else:
                score *= 0.001  # Very low probability for unseen combinations

        # Factor in overall letter frequencies
        letter_count = Counter(word)
        for letter, count in letter_count.items():
            if letter in self.letter_frequencies:
                # Penalize repeated letters slightly
                score *= (self.letter_frequencies[letter]
                          ** count) * (0.9 ** (count - 1))
            else:
                score *= 0.001

        return score

    def calculate_elimination_score(self, word: str, possible_words: List[str]) -> float:
        """
        Calculate how many words this guess would eliminate on average.
        Higher score means better guess for narrowing down possibilities.

        Args:
            word: The word to evaluate as a guess
            possible_words: Current list of possible answers

        Returns:
            Expected number of words that would be eliminated
        """
        if len(possible_words) <= 1:
            return 0.0

        # Simulate all possible outcomes for this guess
        pattern_counts = {}

        for answer in possible_words:
            # Generate the pattern (green/yellow/gray) for this guess against this answer
            pattern = self._get_guess_pattern(word, answer)
            pattern_key = tuple(pattern)

            if pattern_key not in pattern_counts:
                pattern_counts[pattern_key] = 0
            pattern_counts[pattern_key] += 1

        # Calculate expected number of remaining words after this guess
        total_words = len(possible_words)
        expected_remaining = 0.0

        for pattern_key, count in pattern_counts.items():
            probability = count / total_words
            expected_remaining += probability * count

        # Return the expected number of words eliminated
        return total_words - expected_remaining

    def _get_guess_pattern(self, guess: str, answer: str) -> List[str]:
        """
        Generate the Wordle pattern (green/yellow/gray) for a guess against an answer.

        Args:
            guess: The guessed word
            answer: The actual answer

        Returns:
            List of patterns: 'green', 'yellow', or 'gray' for each position
        """
        pattern = ['gray'] * 5
        answer_chars = list(answer)
        guess_chars = list(guess)

        # First pass: mark green (correct position)
        for i in range(5):
            if guess_chars[i] == answer_chars[i]:
                pattern[i] = 'green'
                answer_chars[i] = None  # Remove from available chars
                guess_chars[i] = None   # Mark as processed

        # Second pass: mark yellow (wrong position)
        for i in range(5):
            if guess_chars[i] is not None:  # Not already marked green
                if guess_chars[i] in answer_chars:
                    pattern[i] = 'yellow'
                    # Remove first occurrence from answer_chars
                    answer_chars[answer_chars.index(guess_chars[i])] = None

        return pattern

    def solve(self,
              correct_positions: Dict[int, str] = None,
              correct_letters: List[str] = None,
              incorrect_letters: List[str] = None,
              wrong_positions: Dict[str, Set[int]] = None,
              max_results: int = 20,
              use_elimination_scoring: bool = True) -> List[Tuple[str, float]]:
        """
        Solve Wordle puzzle given constraints and return ranked list of possibilities.

        Args:
            correct_positions: Dict mapping position (0-4) to correct letter
            correct_letters: List of letters that are in the word but position unknown
            incorrect_letters: List of letters that are not in the word
            wrong_positions: Dict mapping letter to set of positions where it's NOT located
            max_results: Maximum number of results to return
            use_elimination_scoring: If True, rank by elimination potential; if False, use frequency-based probability

        Returns:
            List of tuples (word, elimination_score) sorted by score (highest first)
        """
        # Filter words based on constraints
        possible_words = self.filter_words(correct_positions, correct_letters,
                                           incorrect_letters, wrong_positions)

        if not possible_words:
            return []

        # For initial guess (no constraints), use pre-computed good starting words
        if (not correct_positions and not correct_letters and
            not incorrect_letters and not wrong_positions and
                use_elimination_scoring and len(possible_words) == len(self.words)):
            return self._get_best_starting_words(max_results)

        # For large word lists (>50), optimize by using frequency scoring to pre-filter
        candidates = possible_words
        if use_elimination_scoring and len(possible_words) > 50:
            # First, use frequency scoring to get top candidates
            freq_scores = [(word, self.calculate_word_probability(word))
                           for word in possible_words]
            freq_scores.sort(key=lambda x: x[1], reverse=True)
            # Take top 30 for elimination scoring
            candidates = [word for word,
                          _ in freq_scores[:min(30, len(freq_scores))]]

        # Calculate scores for candidate words
        word_scores = []
        for word in candidates:
            if use_elimination_scoring:
                score = self.calculate_elimination_score(word, possible_words)
            else:
                score = self.calculate_word_probability(word)
            word_scores.append((word, score))

        # Sort by score (highest first)
        word_scores.sort(key=lambda x: x[1], reverse=True)

        return word_scores[:max_results]

    def _get_best_starting_words(self, max_results: int) -> List[Tuple[str, float]]:
        """
        Return pre-computed best starting words with their elimination scores.
        These are based on common Wordle strategy and letter frequency analysis.
        """
        # Pre-computed good starting words (these eliminate the most words on average)
        starting_words = [
            ('lares', 14512.1),
            ('rales', 14512.1),
            ('nares', 14503.9),
            ('ranes', 14503.7),
            ('reais', 14498.8),
            ('soare', 14498.8),
            ('tares', 14475.7),
            ('aeros', 14491.9),
            ('serai', 14490.2),
            ('rates', 14489.3),
            ('seria', 144887.8),
            ('saner', 14486.8),
            ('arles', 14476.9),
            ('sater', 14475.7),
            ('lanes', 14470.3),
            ('raise', 14467.5),
            ('tales', 14466.2),
            ('aloes', 14464.7),
            ('saine', 14464.0),
            ('reals', 14464.0)
        ]

        # Filter to only include words that are in our word list
        available_words = [(word, score)
                           for word, score in starting_words if word in self.words]

        # If we don't have any pre-computed words, fall back to frequency scoring
        if not available_words:
            word_scores = [(word, self.calculate_word_probability(word))
                           for word in self.words[:50]]
            word_scores.sort(key=lambda x: x[1], reverse=True)
            available_words = word_scores

        return available_words[:max_results]

    def get_best_guess(self,
                       correct_positions: Dict[int, str] = None,
                       correct_letters: List[str] = None,
                       incorrect_letters: List[str] = None,
                       wrong_positions: Dict[str, Set[int]] = None) -> str:
        """Get the single best guess based on current constraints."""
        results = self.solve(correct_positions, correct_letters, incorrect_letters,
                             wrong_positions, max_results=1)
        return results[0][0] if results else None

    def get_stats(self) -> Dict[str, int]:
        """Get statistics about the loaded word list."""
        return {
            "total_words": len(self.words),
            "unique_letters": len(set(''.join(self.words))),
            "avg_word_length": sum(len(word) for word in self.words) / len(self.words) if self.words else 0
        }
