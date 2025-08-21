# MTG Card List Comparison Tool

A simple Python tool to compare two Magic: The Gathering card lists and identify differences.

## Features

- Compares two card lists and identifies:
  - Cards unique to each list
  - Cards with different quantities between lists
- Handles multiple card list formats:
  - `1 Aftermath Analyst (EOC) 91`
  - `1x Aftermath Analyst (mkm) 148 [Recursion,Creature]`
- Focuses on card names and quantities, ignoring set codes and other metadata
- Handles double-faced cards by comparing only the first part of the name
  - e.g., "Bala Ged Recovery // Bala Ged Sanctuary" matches with "Bala Ged Recovery"
- Ignores basic lands (Forest, Island, Swamp, Plains, Mountain) in the comparison
- Ignores cards with the 'Sideboard' tag in the tag list
  - e.g., "1x Amulet of Vigor (wwk) 121 _F_ [Sideboard,Artifact]"
- Ignores cards with '{noDeck}' in any tag
  - e.g., "1x Dark Ritual (cst) 120 [Sideboard,Maybeboard{noDeck}{noPrice}]"
- Supports filtering cards from a third file using the `--filter` option
  - Any card in the filter file will be excluded from the comparison

## Usage

```bash
# Run with two card list files
python -m src.card_diff.compare path/to/list1.txt path/to/list2.txt

# Filter out cards from a third file
python -m src.card_diff.compare path/to/list1.txt path/to/list2.txt --filter path/to/filter.txt

# Or using the package directly
python -m src.card_diff path/to/list1.txt path/to/list2.txt
```

## Example

```bash
python -m src.card_diff.compare tests/sample_list1.txt tests/sample_list2.txt
```

Sample output:

```
Comparing card lists in 'tests/sample_list1.txt' and 'tests/sample_list2.txt'...

Cards unique to 'tests/sample_list1.txt':
  1x Archetype of Imagination
  1x Azorius Chancery

Cards unique to 'tests/sample_list2.txt':
  1x Counterspell

Cards with different quantities:
  Azorius Signet: 3x in 'tests/sample_list1.txt', 2x in 'tests/sample_list2.txt'
  Brainstorm: 2x in 'tests/sample_list1.txt', 3x in 'tests/sample_list2.txt'
```
