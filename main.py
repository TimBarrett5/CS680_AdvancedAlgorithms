import csv
import time


# Load and read data files
def load_dataset(filepath):
    records = []
    skipped = 0
    with open(filepath, newline='') as f:
        reader = csv.reader(f, delimiter='|')
        # Skip header row
        next(reader)
        # Loop through records, skip if data is dirty
        for record in reader:
            if (len(record) == 4):
                key_str, data_a_str, data_b_str, validation_str = record
                # Convert key to int for cheaper comparisons
                records.append((int(key_str), data_a_str, data_b_str, validation_str))
            else: #Skip records with missing data
                skipped += 1
    return records, skipped


# Sort by key field
def sort_key(record):
    return record[0]


def heapify(record, n, i):
    # Init root, left & right index
    largest = i
    left = 2 * i + 1
    right = 2 * i + 2

    # Compare left child with root
    if left < n and sort_key(record[left]) > sort_key(record[largest]):
        largest = left

    # Compare right child with root
    if right < n and sort_key(record[right]) > sort_key(record[largest]):
        largest = right

    # if largest is not root, recursive call on sub-tree
    if largest != i:
        record[i], record[largest] = record[largest], record[i]
        heapify(record, n, largest)


def heap_sort(record):
    n = len(record)

    for i in range(n // 2 - 1, -1, -1):
        heapify(record, n, i)

    # Move current root to end & call heapify on reduced heap
    for i in range(n - 1, 0, -1):
        record[0], record[i] = record[i], record[0]
        heapify(record, i, 0)


def main():
    # Add files to array
    dataset_files = [
        'Module 3-1 Activity Data Set-1.csv',
        'Module  3-1 Activity Data Set-2.csv',
        'Module 3-1 Activity Data Set-3.csv',
        'Module  3-1 Activity Data Set-4.csv',
        'Module  3-1 Activity Data Set-5.csv'
    ]

    # Iterate through datasets to sort and capture time
    cumulative_time = 0
    for file in dataset_files:
        records, skipped = load_dataset(file)
        n = len(records)
        file_time = time_sort(records)

        if skipped:
            print(f"Skipped {skipped} records in {file}.")

        print(f"Sorted {n} records from {file} in {file_time} seconds.")
        cumulative_time += file_time

    print(f"Average time to sort: {cumulative_time / len(dataset_files)} seconds")
    print(f"Total time to sort: {cumulative_time} seconds")


# Capture sorting time
def time_sort(record):
    start = time.perf_counter()
    heap_sort(record)
    end = time.perf_counter() - start
    print(f"Sorted {len(record)} records in {end} seconds.")
    return end


if __name__ == '__main__':
    main()