#!/usr/bin/env python3
"""
Card list comparison tool.

This script compares two text files containing card entries and identifies
which entries are unique to each file, accounting for quantities.
"""

import re
import sys
import argparse
from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple


def normalize_card_name(card_name: str) -> str:
    """
    Normalize a card name by taking only the part before any double slash or slash.

    For double-faced cards like "Bala Ged Recovery // Bala Ged Sanctuary",
    this returns "Bala Ged Recovery".

    Args:
        card_name: The card name to normalize

    Returns:
        The normalized card name
    """
    # Handle double slash format with spaces: "Card Name // Card Name"
    if " // " in card_name:
        card_name = card_name.split(" // ")[0].strip()
    # Handle single slash format: "Card Name/Card Name"
    elif "/" in card_name:
        card_name = card_name.split("/")[0].strip()

    return card_name


def parse_card_line(line: str) -> Tuple[str, int]:
    """
    Parse a card line and extract the card name and quantity.

    Handles both formats:
    - "1 Aftermath Analyst (EOC) 91"
    - "1x Aftermath Analyst (mkm) 148 [Recursion,Creature]"

    For double-faced cards, only the first part of the name is used.
    Cards with the 'Sideboard' tag are ignored.

    Returns:
        Tuple containing (card_name, quantity)
    """
    # Strip whitespace and skip empty lines
    line = line.strip()
    if not line:
        return "", 0

    # Check if the line has tags to filter
    if '[' in line and ']' in line:
        # Extract the tags part (text within the last set of square brackets)
        tags_match = re.search(r'\[([^\]]+)\]', line)
        if tags_match:
            tags_text = tags_match.group(1)
            tags = tags_text.split(',')

            # Check if 'Sideboard' is in the tags
            if any(tag.strip() == 'Sideboard' for tag in tags):
                return "", 0

            # Check if any tag contains '{noDeck}'
            if '{noDeck}' in tags_text:
                return "", 0

    # Match the quantity at the beginning (with or without 'x')
    quantity_match = re.match(r'^(\d+)x?\s+', line)
    if not quantity_match:
        return "", 0

    quantity = int(quantity_match.group(1))

    # Extract the text after the quantity and before the first parenthesis
    remaining_text = line[quantity_match.end():]
    card_name_match = re.match(r'([^(]+)', remaining_text)

    if not card_name_match:
        return "", 0

    card_name = card_name_match.group(1).strip()

    # Normalize the card name (handle double-faced cards)
    card_name = normalize_card_name(card_name)

    return card_name, quantity


# List of basic lands to ignore
BASIC_LANDS = {"Forest", "Island", "Swamp", "Plains", "Mountain"}


def read_card_file(file_path: str) -> Dict[str, int]:
    """
    Read a card file and return a dictionary of card names to quantities.

    Basic lands (Forest, Island, Swamp, Plains, Mountain) are ignored.

    Args:
        file_path: Path to the card file

    Returns:
        Dictionary mapping card names to quantities
    """
    cards: Dict[str, int] = defaultdict(int)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                card_name, quantity = parse_card_line(line)
                # Skip empty card names and basic lands
                if card_name and card_name not in BASIC_LANDS:
                    cards[card_name] += quantity
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
        sys.exit(1)

    return cards


def read_filter_file(file_path: str) -> Set[str]:
    """
    Read a filter file and return a set of card names to filter out.

    Args:
        file_path: Path to the filter file

    Returns:
        Set of card names to filter out
    """
    filter_cards = set()

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                card_name, _ = parse_card_line(line)
                if card_name:
                    filter_cards.add(card_name)
    except FileNotFoundError:
        print(
            f"Warning: Filter file '{file_path}' not found. No cards will be filtered.")
    except Exception as e:
        print(
            f"Warning: Error reading filter file '{file_path}': {e}. No cards will be filtered.")

    return filter_cards


def compare_card_lists(file1: str, file2: str, filter_file: Optional[str] = None) -> Tuple[Dict[str, int], Dict[str, int], Dict[str, Tuple[int, int]]]:
    """
    Compare two card lists and return the differences.

    Args:
        file1: Path to the first card file
        file2: Path to the second card file
        filter_file: Optional path to a filter file containing cards to exclude

    Returns:
        Tuple containing:
        - Cards unique to file1 (with quantities)
        - Cards unique to file2 (with quantities)
        - Cards in both files but with different quantities
    """
    cards1 = read_card_file(file1)
    cards2 = read_card_file(file2)

    # If a filter file is provided, read it and filter out those cards
    filter_cards = set()
    if filter_file:
        filter_cards = read_filter_file(filter_file)

        # Remove filtered cards from both card lists
        for card in filter_cards:
            if card in cards1:
                del cards1[card]
            if card in cards2:
                del cards2[card]

    # Find cards unique to each file
    unique_to_file1 = {card: qty for card,
                       qty in cards1.items() if card not in cards2}
    unique_to_file2 = {card: qty for card,
                       qty in cards2.items() if card not in cards1}

    # Find cards with different quantities
    different_quantities = {}
    for card, qty1 in cards1.items():
        if card in cards2 and cards2[card] != qty1:
            different_quantities[card] = (qty1, cards2[card])

    return unique_to_file1, unique_to_file2, different_quantities


def main():
    """Main function to run the card comparison."""
    parser = argparse.ArgumentParser(
        description='Compare two Magic: The Gathering card lists.')
    parser.add_argument('file1', help='Path to the first card list file')
    parser.add_argument('file2', help='Path to the second card list file')
    parser.add_argument(
        '--filter', help='Path to a file containing cards to exclude from the comparison')

    args = parser.parse_args()

    file1 = args.file1
    file2 = args.file2
    filter_file = args.filter

    if filter_file:
        print(
            f"Comparing card lists in '{file1}' and '{file2}', filtering cards from '{filter_file}'...\n")
    else:
        print(f"Comparing card lists in '{file1}' and '{file2}'...\n")

    unique_to_file1, unique_to_file2, different_quantities = compare_card_lists(
        file1, file2, filter_file)

    # Print results
    print(f"Cards unique to '{file1}':")
    if unique_to_file1:
        for card, qty in sorted(unique_to_file1.items()):
            print(f"  {qty}x {card}")
    else:
        print("  None")

    print(f"\nCards unique to '{file2}':")
    if unique_to_file2:
        for card, qty in sorted(unique_to_file2.items()):
            print(f"  {qty}x {card}")
    else:
        print("  None")

    print("\nCards with different quantities:")
    if different_quantities:
        for card, (qty1, qty2) in sorted(different_quantities.items()):
            print(f"  {card}: {qty1}x in '{file1}', {qty2}x in '{file2}'")
    else:
        print("  None")


if __name__ == "__main__":
    main()
