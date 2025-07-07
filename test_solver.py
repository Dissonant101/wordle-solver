#!/usr/bin/env python3
"""
Test suite for the Wordle solver.
"""

import unittest
from wordle_solver import WordleSolver


class TestWordleSolver(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.solver = WordleSolver("words.csv")
    
    def test_load_words(self):
        """Test that words are loaded correctly."""
        self.assertGreater(len(self.solver.words), 0)
        # Check that all words are 5 letters
        for word in self.solver.words:
            self.assertEqual(len(word), 5)
            self.assertTrue(word.isalpha())
    
    def test_correct_positions(self):
        """Test filtering by correct positions (green letters)."""
        # Test single correct position
        results = self.solver.filter_words(correct_positions={0: 'a'})
        for word in results:
            self.assertEqual(word[0], 'a')
        
        # Test multiple correct positions
        results = self.solver.filter_words(correct_positions={0: 'a', 4: 'e'})
        for word in results:
            self.assertEqual(word[0], 'a')
            self.assertEqual(word[4], 'e')
    
    def test_incorrect_letters(self):
        """Test filtering by incorrect letters (gray letters)."""
        results = self.solver.filter_words(incorrect_letters={'x', 'z'})
        for word in results:
            self.assertNotIn('x', word)
            self.assertNotIn('z', word)
    
    def test_correct_letters(self):
        """Test filtering by correct letters (yellow letters)."""
        results = self.solver.filter_words(correct_letters={'a', 'e'})
        for word in results:
            self.assertIn('a', word)
            self.assertIn('e', word)
    
    def test_wrong_positions(self):
        """Test filtering by wrong positions (yellow letters with position constraints)."""
        results = self.solver.filter_words(wrong_positions={'a': {0, 1}})
        for word in results:
            self.assertIn('a', word)
            self.assertNotEqual(word[0], 'a')
            self.assertNotEqual(word[1], 'a')
    
    def test_combined_constraints(self):
        """Test filtering with multiple constraint types."""
        results = self.solver.filter_words(
            correct_positions={0: 's'},
            correct_letters={'a'},
            incorrect_letters={'i', 'o'},
            wrong_positions={'a': {1}}
        )
        for word in results:
            self.assertEqual(word[0], 's')  # Correct position
            self.assertIn('a', word)        # Contains 'a'
            self.assertNotIn('i', word)     # Doesn't contain 'i'
            self.assertNotIn('o', word)     # Doesn't contain 'o'
            self.assertNotEqual(word[1], 'a')  # 'a' not at position 1
    
    def test_duplicate_letters(self):
        """Test handling of words with duplicate letters."""
        # Test with a word that has duplicate letters
        if 'glass' in self.solver.words:
            # 'glass' has two 's' letters
            results = self.solver.filter_words(correct_positions={0: 'g', 4: 's'})
            self.assertIn('glass', results)
        
        # Test constraints that should handle duplicates correctly
        results = self.solver.filter_words(
            correct_positions={0: 'g'},
            correct_letters={'s'},
            wrong_positions={'s': {1, 2, 3}}
        )
        # Should find words where 'g' is at position 0, 's' is in the word but not at positions 1,2,3
        # This should include 'glass' if it exists
        for word in results:
            self.assertEqual(word[0], 'g')
            self.assertIn('s', word)
            if len(word) > 1:
                self.assertNotEqual(word[1], 's')
            if len(word) > 2:
                self.assertNotEqual(word[2], 's')
            if len(word) > 3:
                self.assertNotEqual(word[3], 's')
    
    def test_probability_calculation(self):
        """Test probability calculation."""
        # Test that probabilities are calculated
        prob1 = self.solver.calculate_word_probability('about')
        prob2 = self.solver.calculate_word_probability('zzzzz')
        
        self.assertGreater(prob1, 0)
        self.assertGreater(prob2, 0)
        # 'about' should have higher probability than 'zzzzz'
        self.assertGreater(prob1, prob2)
    
    def test_solve_method(self):
        """Test the main solve method."""
        results = self.solver.solve(
            correct_positions={0: 'a'},
            max_results=5
        )
        
        # Should return list of tuples (word, probability)
        self.assertIsInstance(results, list)
        self.assertLessEqual(len(results), 5)
        
        for word, prob in results:
            self.assertIsInstance(word, str)
            self.assertIsInstance(prob, float)
            self.assertEqual(word[0], 'a')
            self.assertGreater(prob, 0)
        
        # Results should be sorted by probability (highest first)
        for i in range(len(results) - 1):
            self.assertGreaterEqual(results[i][1], results[i+1][1])
    
    def test_get_best_guess(self):
        """Test getting the best guess."""
        best = self.solver.get_best_guess(correct_positions={0: 'a'})
        self.assertIsInstance(best, str)
        self.assertEqual(best[0], 'a')
        self.assertEqual(len(best), 5)
    
    def test_no_valid_words(self):
        """Test case where no words satisfy constraints."""
        # Impossible constraints
        results = self.solver.filter_words(
            correct_positions={0: 'a', 1: 'a', 2: 'a', 3: 'a', 4: 'a'},
            incorrect_letters={'a'}
        )
        self.assertEqual(len(results), 0)
        
        # solve method should return empty list
        results = self.solver.solve(
            correct_positions={0: 'a', 1: 'a', 2: 'a', 3: 'a', 4: 'a'},
            incorrect_letters={'a'}
        )
        self.assertEqual(len(results), 0)
        
        # get_best_guess should return None
        best = self.solver.get_best_guess(
            correct_positions={0: 'a', 1: 'a', 2: 'a', 3: 'a', 4: 'a'},
            incorrect_letters={'a'}
        )
        self.assertIsNone(best)
    
    def test_stats(self):
        """Test statistics method."""
        stats = self.solver.get_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn('total_words', stats)
        self.assertIn('unique_letters', stats)
        self.assertIn('avg_word_length', stats)
        
        self.assertGreater(stats['total_words'], 0)
        self.assertGreater(stats['unique_letters'], 0)
        self.assertAlmostEqual(stats['avg_word_length'], 5.0, places=1)


class TestSpecificScenarios(unittest.TestCase):
    """Test specific Wordle scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.solver = WordleSolver("words.csv")
    
    def test_crane_scenario(self):
        """Test scenario: tried CRANE, got R and E yellow, A green at position 2."""
        results = self.solver.solve(
            correct_positions={2: 'a'},
            correct_letters={'r', 'e'},
            incorrect_letters={'c', 'n'},
            wrong_positions={'r': {1}, 'e': {4}},
            max_results=10
        )
        
        # Should find valid words
        self.assertGreater(len(results), 0)
        
        # Check that all results satisfy constraints
        for word, prob in results:
            self.assertEqual(word[2], 'a')  # A at position 2
            self.assertIn('r', word)        # Contains R
            self.assertIn('e', word)        # Contains E
            self.assertNotIn('c', word)     # No C
            self.assertNotIn('n', word)     # No N
            self.assertNotEqual(word[1], 'r')  # R not at position 1
            self.assertNotEqual(word[4], 'e')  # E not at position 4
    
    def test_multiple_same_letter(self):
        """Test scenario with multiple instances of the same letter."""
        # Scenario: word has multiple P's, first P is green, others are yellow
        results = self.solver.solve(
            correct_positions={0: 'p'},
            wrong_positions={'p': {1, 2, 3}},  # P appears again but not at these positions
            incorrect_letters={'o', 'y'},
            max_results=10
        )
        
        # Should find words that start with P and have at least one more P
        for word, prob in results:
            self.assertEqual(word[0], 'p')
            self.assertNotIn('o', word)
            self.assertNotIn('y', word)
            # Should have at least one more P (but not at positions 1,2,3)
            p_count = word.count('p')
            if p_count > 1:
                # If there are multiple P's, none should be at positions 1,2,3
                for pos in [1, 2, 3]:
                    if pos < len(word):
                        self.assertNotEqual(word[pos], 'p')


if __name__ == '__main__':
    unittest.main()
