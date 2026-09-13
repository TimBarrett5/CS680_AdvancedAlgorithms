import csv


# Load and read datasets, unpack to list & keep only data, dropping sequence from each entry
def load_dataset(filepath):
    records = []
    skipped = 0
    with open(filepath, newline='') as f:
        reader = csv.reader(f, delimiter='|')
        next(reader)
        for record in reader:
            if (len(record) == 2):
                sequence_int, data_str = record
                records.append(data_str)
            else:
                skipped += 1
    return records, skipped

class Tree_Node:
    def __init__(self, value):
        self.val = value
        self.l = None
        self.r = None
        self.height = 1

class AVL_Tree:
    def __init__(self):
        self.root = None

    # Function for height
    def height(self, node):
        if not node:
            return 0
        return node.height

    # Function to check tree balance
    def balance(self, node):
        if not node:
            return 0
        return self.height(node.l) - self.height(node.r)

    # Insert new nodes to tree
    def insert(self, root, value):
        # Create new node in empty spot
        if not root:
            return Tree_Node(value)
        # If less than root go left & insert into left subtree
        elif value < root.val:
            root.l = self.insert(root.l, value)
        # If greater than root go right & insert into right subtree
        else:
            root.r = self.insert(root.r, value)

        root.height = 1 + max(self.height(root.l), self.height(root.r))
        root = self.rebalance(root)
        return root

    def rebalance(self, node):
        if self.balance(node) >= -1 and self.balance(node) <= 1:
            return node
        else:
            balance_check = self.balance(node)
            #Left side is bigger
            if balance_check > 1:
                #Rotate for zigzag - child then node
                if self.balance(node.l) < 0:
                    node.l = self.rotate_left(node.l)
                    return self.rotate_right(node)
                else: #Rotate for straight heavy
                    return self.rotate_right(node)
            #Right side is bigger
            elif balance_check < -1:
                #Rotate for zigzag - child then node
                if self.balance(node.r) > 0:
                    node.r = self.rotate_right(node.r)
                    return self.rotate_left(node)
                else: #Rotate for straight heavy
                    return self.rotate_left(node)

    # Rotate to the left, making b the left child of a with c the right child of b
    def rotate_left(self, node_b):
        node_a = node_b.r
        node_c = node_a.l

        node_a.l = node_b
        node_b.r = node_c

        node_b.height = 1 + max(self.height(node_b.l), self.height(node_b.r))
        node_a.height = 1 + max(self.height(node_a.l), self.height(node_a.r))

        return node_a  # becomes new top

    # Rotate to the right, making b the right child of a with d the left child of b
    def rotate_right(self, node_b):
        node_a = node_b.l
        node_d = node_a.r

        node_a.r = node_b
        node_b.l = node_d

        node_b.height = 1 + max(self.height(node_b.l), self.height(node_b.r))
        node_a.height = 1 + max(self.height(node_a.l), self.height(node_a.r))

        return node_a  # becomes new top

    # Insert root value utility function
    def insert_value(self, val):
        self.root = self.insert(self.root, val)

    # Tree traversal
    def traverse(self, root):
        if root:
            self.traverse(root.l)
            print(root.val)
            self.traverse(root.r)

    # Tree traversal utility function
    def traverse_tree(self):
        self.traverse(self.root)

    # Search tree for target value and count nodes
    def search(self, root, target, nodes_visited=0):
        nodes_visited += 1
        if not root:
            return None, nodes_visited
        if root.val == target:
            return root, nodes_visited
        if target < root.val:
            return self.search(root.l, target, nodes_visited)
        return self.search(root.r, target, nodes_visited)

    # Utility function for search
    def search_value(self, target):
        return self.search(self.root, target)


def main():
    dataset_files = [
        'Module 4-1 Data Set-1.csv',
        'Module 4-1 Data Set-2.csv',
        'Module 4-1 Data Set-3.csv',
        'Module 4-1 Data Set-4.csv',
        'Module 4-1 Data Set-5.csv'
    ]

    tree = AVL_Tree()
    total_loaded = 0
    total_skipped = 0
    all_words = []

    #Data insertion
    for file in dataset_files:
        records, skipped = load_dataset(file)
        total_loaded += len(records)
        total_skipped += skipped
        all_words.extend(records)
        for word in records:
            tree.insert_value(word)
        print(f"Loaded {len(records)} words from {file} ({skipped} skipped)")

    #Data insertion validation outputs
    print(f"Total words loaded: {total_loaded}, total skipped: {total_skipped}")
    print(f"Root balance factor: {tree.balance(tree.root)}")
    print(f"Tree height: {tree.height(tree.root)}")

    #Searching step & validation outputs
    search_word = 'Britannia'
    found_node, nodes_visited = tree.search_value(search_word)
    if found_node:
        print(f"Found '{search_word}' after visiting {nodes_visited} nodes")
    else:
        print(f"Could not find '{search_word}' in {nodes_visited} nodes")
    occurence_count = all_words.count(search_word)
    print(f"'{search_word}' occurs {occurence_count} time(s) in the data files")


if __name__ == "__main__":
    main()