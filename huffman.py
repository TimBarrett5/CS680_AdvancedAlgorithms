import csv
import time
from collections import namedtuple
import os


# Establish all data sets
data_sets = ['CS 680 Project Data Set-1.csv',
             'CS 680 Project Data Set-2.csv',
             'CS 680 Project Data Set-3.csv',
             'CS 680 Project Data Set-4.csv']

# Create namedTuple for data set
Record = namedtuple('Record', ['index', 'value', 'clen', 'ws', 'data', 'validation'])


# Load data set into list of Record namedTuples
def load_dataset(filepath):
    records = []
    skipped = 0
    with open(filepath, newline='') as f:
        reader = csv.reader(f, delimiter='|')
        next(reader)
        for record in reader:
            if len(record) == 6:
                index_int, value_int, clen_int, ws_int, data_str, validation_str = record
                record_tuple = Record(int(index_int), int(value_int), int(clen_int), int(ws_int), data_str,
                                      validation_str)
                records.append(record_tuple)
            else:
                skipped += 1

    return records, skipped


# Read raw file once using binary mode to maintain data integrity
def read_raw_file(filepath):
    with open(filepath, 'rb') as f:
        return f.read()


# Calculate frequency of characters in data set
def char_freq(data):
    freq_table = {}
    for char in data:
        if char in freq_table:
            freq_table[char] += 1
        else:
            freq_table[char] = 1

    return freq_table


# define min Heap class with pop and push methods
class MinHeap:
    def __init__(self):
        self.heap = []

    def heap_pop(self):
        if len(self.heap) == 0:
            return None

        min_item = self.heap[0]
        last_item = self.heap.pop()

        if len(self.heap) == 0:
            return min_item

        self.heap[0] = last_item
        i = 0
        while True:
            left_child = 2 * i + 1
            right_child = 2 * i + 2
            smallest = i

            if left_child < len(self.heap) and self.heap[left_child] < self.heap[smallest]:
                smallest = left_child
            if right_child < len(self.heap) and self.heap[right_child] < self.heap[smallest]:
                smallest = right_child
            if smallest == i:
                break
            else:
                self.heap[i], self.heap[smallest] = self.heap[smallest], self.heap[i]
                i = smallest

        return min_item

    def heap_push(self, item):
        self.heap.append(item)
        i = len(self.heap) - 1
        while i > 0:
            parent = (i - 1) // 2
            if self.heap[i] < self.heap[parent]:
                self.heap[i], self.heap[parent] = self.heap[parent], self.heap[i]
                i = parent
            else:
                break


# define node class for Huffman Tree
# byte is None for internals and weight is set on every node for comparisons in heap
class Node:
    def __init__(self, byte, weight, left=None, right=None):
        self.byte = byte
        self.weight = weight
        self.left = left
        self.right = right


# Build Huffman Tree with frequency table
def huff_tree(freq_table):
    min_heap = MinHeap()
    insert_order = 0  # Handle ties to avoid crashes

    for byte, weight in freq_table.items():
        leaf = Node(byte, weight)
        min_heap.heap_push((weight, insert_order, leaf))
        insert_order += 1

    while len(min_heap.heap) > 1:
        left_tuple = min_heap.heap_pop()
        right_tuple = min_heap.heap_pop()
        l_weight, l_insert, l_node = left_tuple
        r_weight, r_insert, r_node = right_tuple
        new_weight = l_weight + r_weight
        new_node = Node(byte = None, weight = new_weight, left = l_node, right = r_node)
        min_heap.heap_push((new_weight, insert_order, new_node))
        insert_order += 1

    root_tuple = min_heap.heap_pop()
    root_weight, root_insert, root_node = root_tuple

    return root_node


# Build reference table from tree
def build_huff_table(root):
    def build_table(node, current_code, table_dict):
        if node is None:
            return

        if node.byte != None:
            table_dict[node.byte] = current_code if current_code != '' else '0'
            return

        build_table(node.left, current_code + '0', table_dict)
        build_table(node.right, current_code + '1', table_dict)

    table_dict = {}
    build_table(root, '', table_dict)

    return table_dict


# Generate bitstream from raw data and huffman table
def encoder(raw_data, code_table):
    encoded_data = []
    for byte in raw_data:
        if byte in code_table:
            encoded_data.append(code_table[byte])

    encoded_stream = ''.join(encoded_data)

    return encoded_stream


# Compress data to 8-bit chunks with padding for cases that dont use all 8
def packing(encoded_stream):
    padding = (8 - len(encoded_stream) % 8) % 8
    encoded_stream += '0' * padding

    packed = bytearray()
    for i in range(0, len(encoded_stream), 8):
        chunk = encoded_stream[i:i + 8]
        packed.append(int(chunk, 2))

    return packed, padding


# Write compressed data to file
def write_compressed(filepath, code_table, padding, packed):
    with open(filepath, 'wb') as f:
        f.write(f"{len(code_table)}\n".encode())

        for byte in code_table.items():
            key = byte[0]
            value = byte[1]
            code_length = len(value)
            f.write(f"{key}, {code_length}, {value}\n".encode())

        f.write(f"{padding}\n".encode())
        f.write(packed)


# Unpack bitstream and slice padding without losing data
def unpacking(packed, padding):
    unpacked = []
    for item in packed:
        unpacked.append(format(item, '08b'))

    bitstream = ''.join(unpacked)

    return bitstream[:-(padding)] if padding > 0 else bitstream


# Decode the compressed data
def decode(encoded_stream, code_table):
    current_code = ''
    decoded_bytes = bytearray()

    # Invert code table for faster lookups
    invert_table = {code: byte for byte, code in code_table.items()}
    for chunk in encoded_stream:
        current_code += chunk
        if current_code in invert_table:
            decoded_bytes.append(invert_table[current_code])
            current_code = ''

    return decoded_bytes


# Read compressed data from file
def read_compressed(filepath):
    with open(filepath, 'rb') as f:
        header = f.readline().decode().strip()
        num_codes = int(header)
        code_table = {}

        for _ in range(num_codes):
            key, code_length, code = f.readline().decode().strip().split(', ')
            code_table[int(key)] = code

        padding = int(f.readline().decode().strip())
        packed = f.read()

    return code_table, padding, packed


# Write the uncompressed data to file
def write_uncompressed(filepath, decoded_bytes):
    with open(filepath, 'wb') as f:
        f.write(decoded_bytes)


# Create output paths for new files with appropriate names and types
def output_paths(filepath):
    name, ext = os.path.splitext(filepath)
    return name + '_compressed' + '.txt', name + '_uncompressed' + ext


# Framework for benchmarking time details of functions
def benchmark(task, function, *args, **kwargs):
    print(f"Starting: {task}")
    start = time.time()
    result = function(*args, **kwargs)
    end = time.time()
    elapsed = end - start
    print(f"Finished: {task} in {elapsed:.6f} seconds")

    return result, elapsed


# Verify bytes of raw against uncompressed data to detect loss
def verify(raw_data, uncompressed_path, filepath):
    uncompressed_data = read_raw_file(uncompressed_path)
    if raw_data == uncompressed_data:
        print(f"Data validation for {filepath} passed!")
    else:
        print(f"Data validation for {filepath} failed!")


# Primary driver function
# Loops through all data_sets encoding and decoding each creating respective files
# Close loop by verifying each set byte for byte
def main():
    for filepath in data_sets:
        records, skipped = load_dataset(filepath)
        print(f"Loaded {len(records)} from {filepath}, skipped {skipped} records.")
        raw_data, read_time = benchmark("Reading original file", read_raw_file, filepath)

        freq_table = char_freq(raw_data)
        root = huff_tree(freq_table)
        code_table = build_huff_table(root)
        encoded_stream = encoder(raw_data, code_table)
        packed, padding = packing(encoded_stream)

        # Check compression amount
        compression_ratio = len(packed) / len(raw_data) * 100
        print(f"Original size: {len(raw_data)} bytes | Compressed size: {len(packed)} bytes")
        print(f"Compressed is {compression_ratio:.2f}% of original!")

        compressed_path, uncompressed_path = output_paths(filepath)
        compressed_file, compressed_write_time = benchmark("Writing compressed file", write_compressed,
                                                           compressed_path, code_table, padding, packed)
        read_table, compressed_read_time = benchmark("Reading compressed file", read_compressed, compressed_path)
        read_table, padding, packed = read_table
        unpacked_stream = unpacking(packed, padding)
        decoded_bytes = decode(unpacked_stream, read_table)
        uncompressed_file, write_time = benchmark("Writing uncompressed file", write_uncompressed, uncompressed_path,
                                                  decoded_bytes)

        verify(raw_data, uncompressed_path, filepath)


if __name__ == '__main__':
    main()