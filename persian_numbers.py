#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Persian Numbers Module
=====================

This module provides functionality to convert numbers to Persian words
using an efficient algorithmic approach without external dependencies.

Author: SimJowBot
"""

# Constants
ABS_COUNTING_LIMIT = 999999

# Persian numbers lookup table (embedded for efficiency)
PERSIAN_NUMBERS_LUT = {
    1: "یک",
    2: "دو",
    3: "سه",
    4: "چهار",
    5: "پنج",
    6: "شش",
    7: "هفت",
    8: "هشت",
    9: "نه",
    10: "ده",
    11: "یازده",
    12: "دوازده",
    13: "سیزده",
    14: "چهارده",
    15: "پانزده",
    16: "شانزده",
    17: "هفده",
    18: "هجده",
    19: "نوزده",
    20: "بیست",
    30: "سی",
    40: "چهل",
    50: "پنجاه",
    60: "شصت",
    70: "هفتاد",
    80: "هشتاد",
    90: "نود",
    100: "صد",
    200: "دویست",
    300: "سیصد",
    400: "چهارصد",
    500: "پانصد",
    600: "ششصد",
    700: "هفتصد",
    800: "هشتصد",
    900: "نهصد",
    1000: "هزار",
}


def convert_to_persian_word(number):
    """
    Convert a number to Persian word using algorithmic approach.

    This function converts integers to their Persian word equivalents using
    an efficient algorithm that breaks down numbers into thousands, hundreds,
    tens, and ones components.

    Args:
        number (int): The number to convert (-999,999 to +999,999)

    Returns:
        str: The Persian word representation of the number, or an error message
             for numbers outside the supported range

    Examples:
        >>> convert_to_persian_word(1)
        'یک'
        >>> convert_to_persian_word(21)
        'بیست و یک'
        >>> convert_to_persian_word(173)
        'صد و هفتاد و سه'
        >>> convert_to_persian_word(1234)
        'هزار و دویست و سی و چهار'
        >>> convert_to_persian_word(1000000)
        'خطا: عدد خارج از محدوده پشتیبانی شده (-999,999 تا +999,999)'

    Note:
        - Supports numbers from -999,999 to +999,999
        - Uses only base numbers in lookup table (about 30 entries)
        - Algorithmically generates compound numbers
        - Handles proper Persian grammar with 'و' (and) connectors
        - No external dependencies or file I/O required
    """
    # Check if number is within supported range
    if abs(number) > ABS_COUNTING_LIMIT:
        return f"خطا: عدد خارج از محدوده پشتیبانی شده (-999,999 تا +999,999)"

    if number == 0:
        return "صفر"

    if number in PERSIAN_NUMBERS_LUT:
        return PERSIAN_NUMBERS_LUT[number]

    if number < 0:
        return "منفی " + convert_to_persian_word(-number)

    if number < 20:
        return str(number)  # fallback for missing numbers

    result = ""

    # Handle thousands
    if number >= 1000:
        thousands = number // 1000
        if thousands == 1:
            result += "هزار"
        else:
            result += convert_to_persian_word(thousands) + " هزار"
        number %= 1000
        if number > 0:
            result += " و "

    # Handle hundreds
    if number >= 100:
        hundreds = number // 100
        result += PERSIAN_NUMBERS_LUT[hundreds * 100]
        number %= 100
        if number > 0:
            result += " و "

    # Handle tens and ones
    if number >= 20:
        tens = (number // 10) * 10
        result += PERSIAN_NUMBERS_LUT[tens]
        number %= 10
        if number > 0:
            result += " و "

    # Handle remaining ones
    if number > 0:
        result += PERSIAN_NUMBERS_LUT[number]

    return result


def get_supported_range():
    """
    Get the supported number range for conversion.

    Returns:
        tuple: (min_value, max_value) supported by the converter
    """
    return (-ABS_COUNTING_LIMIT, ABS_COUNTING_LIMIT)


def is_number_supported(number):
    """
    Check if a number is within the supported range.

    Args:
        number (int): The number to check

    Returns:
        bool: True if the number is supported, False otherwise
    """
    min_val, max_val = get_supported_range()
    return min_val <= number <= max_val


# Module metadata
__version__ = "1.0.0"
__author__ = "SimJowBot"
__description__ = "Persian number to word conversion module"

# Export main function for convenience
__all__ = ["convert_to_persian_word", "get_supported_range", "is_number_supported"]
