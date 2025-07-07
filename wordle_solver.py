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
                    correct_letters: Set[str] = None,
                    incorrect_letters: Set[str] = None,
                    wrong_positions: Dict[str, Set[int]] = None) -> List[str]:
        """
        Filter words based on Wordle constraints.
        
        Args:
            correct_positions: Dict mapping position (0-4) to correct letter
            correct_letters: Set of letters that are in the word but position unknown
            incorrect_letters: Set of letters that are not in the word
            wrong_positions: Dict mapping letter to set of positions where it's NOT located
                           (but the letter is in the word somewhere else)
        
        Returns:
            List of words that satisfy all constraints
        """
        if correct_positions is None:
            correct_positions = {}
        if correct_letters is None:
            correct_letters = set()
        if incorrect_letters is None:
            incorrect_letters = set()
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
                             correct_letters: Set[str],
                             incorrect_letters: Set[str],
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
            if letter in word:
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
        all_known_letters = set(correct_positions.values()) | correct_letters | set(wrong_positions.keys())
        for letter in all_known_letters:
            required_count = 0
            
            # Count from correct positions
            required_count += sum(1 for l in correct_positions.values() if l == letter)
            
            # Count from correct letters (yellow/wrong position)
            if letter in correct_letters:
                required_count += 1
            if letter in wrong_positions:
                required_count += 1
            
            # Remove double counting if letter appears in both correct_letters and wrong_positions
            if letter in correct_letters and letter in wrong_positions:
                required_count -= 1
            
            if word_letter_count[letter] < required_count:
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
                score *= (self.letter_frequencies[letter] ** count) * (0.9 ** (count - 1))
            else:
                score *= 0.001
        
        return score
    
    def solve(self, 
              correct_positions: Dict[int, str] = None,
              correct_letters: Set[str] = None,
              incorrect_letters: Set[str] = None,
              wrong_positions: Dict[str, Set[int]] = None,
              max_results: int = 20) -> List[Tuple[str, float]]:
        """
        Solve Wordle puzzle given constraints and return ranked list of possibilities.
        
        Args:
            correct_positions: Dict mapping position (0-4) to correct letter
            correct_letters: Set of letters that are in the word but position unknown
            incorrect_letters: Set of letters that are not in the word
            wrong_positions: Dict mapping letter to set of positions where it's NOT located
            max_results: Maximum number of results to return
        
        Returns:
            List of tuples (word, probability_score) sorted by probability (highest first)
        """
        # Filter words based on constraints
        possible_words = self.filter_words(correct_positions, correct_letters, 
                                         incorrect_letters, wrong_positions)
        
        if not possible_words:
            return []
        
        # Calculate probability for each word
        word_probabilities = []
        for word in possible_words:
            prob = self.calculate_word_probability(word)
            word_probabilities.append((word, prob))
        
        # Sort by probability (highest first)
        word_probabilities.sort(key=lambda x: x[1], reverse=True)
        
        return word_probabilities[:max_results]
    
    def get_best_guess(self, 
                      correct_positions: Dict[int, str] = None,
                      correct_letters: Set[str] = None,
                      incorrect_letters: Set[str] = None,
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
