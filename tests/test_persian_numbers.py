#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Persian Number Conversion Test Suite
===================================

Comprehensive test program for the convert_to_persian_word() function.
This program validates Persian number conversion functionality with various test modes:
- Unit tests against reference lookup table
- Demonstration of number conversions
- Interactive testing interface
- Performance benchmarking

Supports numbers from -999,999 to +999,999 with proper error handling
for numbers outside this range.

Author: SimJowBot
Version: 1.0.0
"""

import sys
import os
import time
import unittest
from typing import Dict, List, Tuple, Any

# Add parent directory to path to import persian_numbers module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from persian_numbers import convert_to_persian_word, ABS_COUNTING_LIMIT

# Test configuration constants
SUPPORTED_RANGE = (-ABS_COUNTING_LIMIT, ABS_COUNTING_LIMIT)
PERFORMANCE_TEST_ITERATIONS = 1000
LUT_FILENAME = "lut.txt"


class TestPersianNumbers(unittest.TestCase):
    """
    Unit tests for the Persian number conversion function.

    Tests include:
    - Comprehensive validation against lookup table (1-1000)
    - Edge cases and boundary values
    - Negative number handling
    - Performance benchmarking
    - Error handling for out-of-range numbers
    """

    @classmethod
    def setUpClass(cls) -> None:
        """Load the expected results from lut.txt file."""
        cls.expected_results: Dict[int, str] = {}

        # Locate lut.txt in the same directory as this test file
        test_dir = os.path.dirname(os.path.abspath(__file__))
        lut_file_path = os.path.join(test_dir, LUT_FILENAME)

        print(f"🔍 Looking for {LUT_FILENAME} at: {lut_file_path}")

        try:
            cls._load_lookup_table(lut_file_path)
        except FileNotFoundError:
            raise unittest.SkipTest(
                f"{LUT_FILENAME} file not found at {lut_file_path}. "
                "Please ensure it exists in the tests directory."
            )

        print(
            f"✅ Loaded {len(cls.expected_results)} expected results from {LUT_FILENAME}"
        )

    @classmethod
    def _load_lookup_table(cls, file_path: str) -> None:
        """Load and parse the lookup table from file."""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse the dictionary from the file content
        lines = content.split("\n")
        for line in lines:
            if ":" in line and line.strip():
                # Skip header and bracket lines
                if line.strip().startswith(
                    "PERSIAN_NUMBERS_AS_WORDS"
                ) or line.strip() in ["{", "}"]:
                    continue

                parts = line.strip().split(":", 1)
                if len(parts) == 2:
                    try:
                        key = int(parts[0].strip())
                        value = parts[1].strip().strip('"').strip(",").strip('"')
                        cls.expected_results[key] = value
                    except ValueError:
                        # Skip malformed lines
                        continue

    def test_all_numbers_1_to_1000(self) -> None:
        """Test that convert_to_persian_word() produces correct results for numbers 1-1000."""
        failures: List[Dict[str, Any]] = []
        successes = 0

        for number in range(1, 1001):
            if number in self.expected_results:
                expected = self.expected_results[number]
                actual = convert_to_persian_word(number)

                if actual != expected:
                    failures.append(
                        {"number": number, "expected": expected, "actual": actual}
                    )
                else:
                    successes += 1

        # Report results
        print(f"\n📊 Test Results:")
        print(f"✅ Successful conversions: {successes}")
        print(f"❌ Failed conversions: {len(failures)}")

        if failures:
            print(f"\n🔍 First 10 failures:")
            for i, failure in enumerate(failures[:10]):
                print(
                    f"  {failure['number']}: expected '{failure['expected']}', "
                    f"got '{failure['actual']}'"
                )
            if len(failures) > 10:
                print(f"  ... and {len(failures) - 10} more failures")

        # Assert that there are no failures
        self.assertEqual(len(failures), 0, f"Found {len(failures)} conversion failures")

    def test_specific_edge_cases(self) -> None:
        """Test specific edge cases and boundary values."""
        test_cases: List[Tuple[int, str]] = [
            (0, "صفر"),
            (1, "یک"),
            (10, "ده"),
            (20, "بیست"),
            (100, "صد"),
            (1000, "هزار"),
            (ABS_COUNTING_LIMIT, None),  # Maximum supported positive number
            (-ABS_COUNTING_LIMIT, None),  # Maximum supported negative number
        ]

        for number, expected in test_cases:
            with self.subTest(number=number):
                actual = convert_to_persian_word(number)

                if number == 0:
                    # Special case for zero
                    self.assertEqual(
                        actual,
                        expected,
                        f"Number {number}: expected '{expected}', got '{actual}'",
                    )
                elif abs(number) == ABS_COUNTING_LIMIT:
                    # Test maximum supported range
                    self.assertIsInstance(
                        actual, str, f"Function should return a string for {number}"
                    )
                    # Should not contain error messages for numbers within range
                    error_keywords = ["خطا", "error", "محدوده", "range"]
                    self.assertFalse(
                        any(keyword in actual.lower() for keyword in error_keywords),
                        f"Should not show error for {number} within supported range, got: {actual}",
                    )
                elif number in self.expected_results:
                    # Use lut.txt for other cases
                    expected_from_lut = self.expected_results[number]
                    self.assertEqual(
                        actual,
                        expected_from_lut,
                        f"Number {number}: expected '{expected_from_lut}', got '{actual}'",
                    )

    def test_negative_numbers(self) -> None:
        """Test negative number handling with various ranges."""
        test_cases: List[Tuple[int, str]] = [
            (-1, "منفی یک"),
            (-10, "منفی ده"),
            (-100, "منفی صد"),
            (-999, "منفی نهصد و نود و نه"),
            (-ABS_COUNTING_LIMIT, "منفی نهصد و نود و نه هزار و نهصد و نود و نه"),
        ]

        for number, expected in test_cases:
            with self.subTest(number=number):
                actual = convert_to_persian_word(number)
                self.assertEqual(
                    actual,
                    expected,
                    f"Number {number}: expected '{expected}', got '{actual}'",
                )

    def test_performance(self) -> None:
        """Test performance of the conversion function."""
        start_time = time.time()
        for i in range(1, PERFORMANCE_TEST_ITERATIONS + 1):
            convert_to_persian_word(i)
        end_time = time.time()

        duration = end_time - start_time
        avg_time = duration / PERFORMANCE_TEST_ITERATIONS

        print(f"\n⚡ Performance Test:")
        print(
            f"   Total time for {PERFORMANCE_TEST_ITERATIONS} conversions: {duration:.4f} seconds"
        )
        print(f"   Average time per conversion: {avg_time * 1000:.4f} ms")

        # Assert that conversion is reasonably fast (less than 1ms per conversion on average)
        self.assertLess(
            avg_time,
            0.001,
            f"Conversion too slow: {avg_time * 1000:.4f} ms per conversion",
        )

    def test_large_numbers_beyond_limit(self) -> None:
        """Test handling of numbers beyond the supported range (±999,999)."""
        test_cases: List[int] = [
            1000000,  # One million
            -1000000,  # Negative one million
            ABS_COUNTING_LIMIT + 1,  # Large positive number (beyond limit)
            -(ABS_COUNTING_LIMIT + 1),  # Large negative number (beyond limit)
        ]

        for number in test_cases:
            with self.subTest(number=number):
                result = convert_to_persian_word(number)

                # Check that the function returns an appropriate error message
                self.assertIsInstance(
                    result, str, f"Function should return a string for {number}"
                )

                # Should indicate limitation for numbers beyond supported range
                if abs(number) > SUPPORTED_RANGE[1]:
                    error_keywords = [
                        "خطا",
                        "error",
                        "محدوده",
                        "range",
                        "پشتیبانی",
                        "support",
                    ]
                    self.assertTrue(
                        any(keyword in result.lower() for keyword in error_keywords),
                        f"Expected error message for {number}, got: {result}",
                    )


def run_unit_tests() -> bool:
    """
    Run the comprehensive unit test suite.

    Returns:
        bool: True if all tests passed, False otherwise
    """
    print("=" * 70)
    print("🧪 Running Unit Tests for Persian Number Conversion")
    print("=" * 70)

    # Create a test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPersianNumbers)

    # Run the tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("🎉 All tests passed!")
    else:
        print(
            f"❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)"
        )
    print("=" * 70)

    return result.wasSuccessful()


def test_function() -> None:
    """
    Demonstrate the convert_to_persian_word function with various test cases.

    Shows conversions for different number ranges including:
    - Single digits, teens, tens
    - Compound numbers
    - Hundreds and thousands
    - Large numbers within supported range
    - Numbers beyond supported range (with error messages)
    """
    print("=== Persian Number Conversion Demonstration ===\n")

    # Comprehensive test cases organized by category
    test_cases = [
        # Single digits
        1,
        5,
        9,
        # Teens
        11,
        15,
        19,
        # Tens
        20,
        30,
        50,
        90,
        # Compound numbers
        21,
        35,
        47,
        68,
        99,
        # Hundreds
        100,
        200,
        500,
        900,
        # Compound hundreds
        101,
        125,
        250,
        367,
        499,
        # Thousands
        1000,
        2000,
        5000,
        # Compound thousands
        1001,
        1234,
        2500,
        3456,
        9999,
        # Large numbers within supported range
        50000,
        100000,
        500000,
        ABS_COUNTING_LIMIT,
        # Current counter value
        173,
        # Some interesting numbers
        42,
        123,
        555,
        777,
        1357,
        2468,
    ]

    print("Testing numbers within supported range:")
    print("-" * 50)
    for num in test_cases:
        persian = convert_to_persian_word(num)
        print(f"{num:>6} → {persian}")

    # Test numbers beyond the supported range
    print(
        f"\nTesting numbers beyond supported range ({SUPPORTED_RANGE[0]:,} to {SUPPORTED_RANGE[1]:,}):"
    )
    print("-" * 50)
    beyond_limit_cases = [1000000, -1000000, 5000000]
    for num in beyond_limit_cases:
        persian = convert_to_persian_word(num)
        print(f"{num:>8} → {persian}")


def interactive_test() -> None:
    """
    Interactive mode for testing specific numbers entered by the user.

    Allows users to input numbers and see their Persian conversions.
    Handles empty input gracefully and provides clear instructions.
    """
    print("\n" + "=" * 60)
    print("Interactive Test - Enter numbers to convert (or 'quit' to exit)")
    print(f"Supported range: {SUPPORTED_RANGE[0]:,} to {SUPPORTED_RANGE[1]:,}")
    print("=" * 60)

    while True:
        try:
            user_input = input("\nEnter a number: ").strip()

            if user_input.lower() in ["quit", "exit", "q"]:
                print("خداحافظ! (Goodbye!)")
                break

            if not user_input:
                print("Please enter a number or 'quit' to exit.")
                continue

            try:
                number = int(user_input)
                persian = convert_to_persian_word(number)
                print(f"📝 {number:,} → {persian}")
            except ValueError:
                print("❌ Please enter a valid integer.")

        except EOFError:
            # Handle EOF gracefully (e.g., when piped input ends)
            print("\n\nInput ended. Running automatic performance test instead...\n")
            performance_test()
            break
        except KeyboardInterrupt:
            print("\n\nTest interrupted by user. خداحافظ! (Goodbye!)")
            break


def performance_test() -> None:
    """
    Test the performance of the Persian number conversion function.

    Measures conversion speed for 1000 consecutive numbers and reports:
    - Total execution time
    - Average time per conversion
    - Conversions per second
    """
    import time

    print("\n" + "=" * 40)
    print("Performance Test")
    print("=" * 40)

    # Test conversion speed with timing
    start_time = time.time()
    test_count = 1000

    for i in range(1, test_count + 1):
        convert_to_persian_word(i)

    end_time = time.time()

    # Calculate and display performance metrics
    total_time = end_time - start_time
    avg_time_ms = (total_time * 1000) / test_count
    conversions_per_second = test_count / total_time if total_time > 0 else float("inf")

    print(f"✅ Successfully converted {test_count:,} numbers (1-{test_count})")
    print(f"⏱️  Total time: {total_time:.4f} seconds")
    print(f"📊 Average time per conversion: {avg_time_ms:.4f} ms")
    print(f"🚀 Conversions per second: {conversions_per_second:.0f}")

    if total_time < 0.1:
        print("🎯 Excellent performance!")
    elif total_time < 0.5:
        print("✨ Good performance!")
    else:
        print("⚠️  Consider optimization for better performance")


if __name__ == "__main__":
    print("🔍 Persian Number Conversion Test Suite")
    print("=" * 50)

    # Ask user what they want to run
    print("Choose test mode:")
    print("1. Run unit tests (verify against lut.txt)")
    print("2. Run demonstration tests")
    print("3. Run interactive test")
    print("4. Run all tests")

    try:
        choice = input("\nEnter your choice (1-4): ").strip()

        if choice == "1":
            # Run unit tests only
            run_unit_tests()

        elif choice == "2":
            # Run demonstration tests only
            test_function()

        elif choice == "3":
            # Run interactive test only
            interactive_test()

        elif choice == "4":
            # Run all tests
            print("\n🧪 Running Unit Tests first:")
            unit_test_success = run_unit_tests()

            if unit_test_success:
                print("\n✅ Unit tests passed! Running demonstration tests...")
                test_function()

                # Ask if user wants to run performance test
                print("\n" + "-" * 50)
                try:
                    run_perf = (
                        input("Run additional performance test? (y/n): ")
                        .strip()
                        .lower()
                    )
                    if run_perf in ["y", "yes"]:
                        performance_test()
                    else:
                        print("Skipping performance test.")
                except EOFError:
                    # Auto-run performance test when no input is available (piped mode)
                    print("Auto-running performance test (no input available)...")
                    performance_test()
            else:
                print("\n❌ Unit tests failed! Skipping demonstration tests.")

        else:
            print("❌ Invalid choice. Please run the script again and select 1-4.")

    except EOFError:
        # Handle piped input scenarios - auto-run performance test
        print(
            "\nNo interactive input available. Running automatic performance test...\n"
        )
        performance_test()

    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user. خداحافظ! (Goodbye!)")

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("Please check your input and try again.")

    print("\n🎉 Test session completed!")
