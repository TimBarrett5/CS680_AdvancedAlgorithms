import csv
import heapq
import time


# Load data set and add to heap, tracking misformatted rows
def load_dataset(filepath):
    records = []
    skipped = 0
    with open(filepath, newline='') as f:
        reader = csv.reader(f, delimiter='|')
        next(reader)
        for record in reader:
            if len(record) == 2:
                sequence_int, data_str = record
                records.append(data_str)
            else:
                skipped += 1
        heapq.heapify(records)
    return records, skipped, filepath


# Depth-first search
def dfs(records, i, search_word, node_count):
    if i >= len(records):
        return False

    node_count[0] += 1

    if records[i] == search_word:
        return True

    if records[i] > search_word:
        return False

    left = 2 * i + 1
    right = 2 * i + 2

    found_left = dfs(records, left, search_word, node_count)
    if found_left:
        return True

    return dfs(records, right, search_word, node_count)


# Application driver function
def main():
    try:
        filepath = 'Module 8 Data Set-1.csv'
        records, skipped, filepath = load_dataset(filepath=filepath)
    except Exception as e:
        print(f"Error: Invalid filepath {e}")
        return

    # Print summary of data set
    print(
        f"Data set {filepath} loaded with {len(records)} records, {skipped} records were skipped because of invalid formatting.")

    # Preview records for validation
    print("Preview first 5 rows from raw file: ")
    with open(filepath, newline='') as f:
        reader = csv.reader(f, delimiter='|')
        next(reader)
        for i, row in enumerate(reader):
            if i >= 5:
                break
            print(row)

    # Preview records loaded for validation
    print("Preview of first 5 rows from heap: ")
    for record in records[:5]:
        print(record)

    search_word = input("Enter the word to search: ")
    node_count = [0]
    start = time.time()
    search_result = dfs(records, 0, search_word, node_count)
    end = time.time()
    elapsed = end - start

    if search_result == True:
        print(f"Data: {search_word} was found, in {elapsed:.6f} seconds after searching {node_count[0]} nodes.")
    else:
        print(
            f"{search_word} was not found in {filepath} after searching {node_count[0]} nodes in {elapsed:.6f} seconds")


if __name__ == '__main__':
    main()