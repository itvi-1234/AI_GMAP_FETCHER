import csv
import os
def save_venues_to_csv_simple(venues, filename="extracted_venues.csv"):
    """
    Saves venues to a CSV file.

    Args:
        venues (list): List of venue dictionaries.
        filename (str, optional): Filename to save to. Defaults to "extracted_venues.csv".

    Functionality:
        - Reads existing venue keys (name + phone) to avoid duplicates
        - Filters new venues for uniqueness
        - Collects all keys from new venues and saves them to a CSV file
    """
    
    if not venues:
        print("❌ No venues to save")
        return

    # Read existing venue keys (name + phone) to avoid duplicates
    existing_venues = set()
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                unique_key = (row.get('name', '').strip(), row.get('phone', '').strip())
                existing_venues.add(unique_key)

    # Filter new venues for uniqueness
    new_unique_venues = []
    for venue in venues:
        unique_key = (venue.get('name', '').strip(), venue.get('phone', '').strip())
        if unique_key not in existing_venues:
            new_unique_venues.append(venue)
            existing_venues.add(unique_key)

    if not new_unique_venues:
        print("ℹ️ No new unique venues to add.")
        return

    # Collect all keys from new venues
    all_keys = set()
    for venue in new_unique_venues:
        all_keys.update(venue.keys())
    fieldnames = sorted(list(all_keys))

    # Append to file
    file_exists = os.path.isfile(filename)
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        for venue in new_unique_venues:
            row = {key: venue.get(key, "N/A") for key in fieldnames}
            writer.writerow(row)

    print(f"✅ Appended {len(new_unique_venues)} new unique venues to '{filename}'")

