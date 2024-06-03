class FixedSizedPartitioning:
    def __init__(self, memory_size, partition_size):
        self.memory_size = memory_size
        self.partition_size = partition_size
        self.partitions = [None] * (memory_size // partition_size)

    def allocate(self, process_id, size):
        partitions_needed = (size + self.partition_size - 1) // self.partition_size
        for i in range(len(self.partitions) - partitions_needed + 1):
            if all(p is None for p in self.partitions[i:i+partitions_needed]):
                for j in range(partitions_needed):
                    self.partitions[i + j] = process_id
                return True
        return False

    def deallocate(self, process_id):
        for i in range(len(self.partitions)):
            if self.partitions[i] == process_id:
                self.partitions[i] = None

    def display(self):
        print("Fixed-sized Memory Partitioning Status:")
        for i, partition in enumerate(self.partitions):
            status = "Free" if partition is None else f"Process {partition}"
            print(f"Partition {i}: {status}")


class UnequalSizedPartitioning:
    def __init__(self, partitions):
        self.partitions = partitions
        self.allocated = [None] * len(partitions)

    def allocate(self, process_id, size, strategy="first_fit"):
        index = self._find_partition(size, strategy)
        if index is not None:
            self.allocated[index] = process_id
            return True
        return False

    def deallocate(self, process_id):
        for i in range(len(self.allocated)):
            if self.allocated[i] == process_id:
                self.allocated[i] = None

    def display(self):
        print("Unequal-sized Memory Partitioning Status:")
        for i, partition in enumerate(self.partitions):
            status = "Free" if self.allocated[i] is None else f"Process {self.allocated[i]}"
            print(f"Partition {i} (Size {partition}): {status}")

    def _find_partition(self, size, strategy):
        if strategy == "first_fit":
            for i in range(len(self.partitions)):
                if self.allocated[i] is None and self.partitions[i] >= size:
                    return i
        elif strategy == "best_fit":
            best_index = None
            best_size = None
            for i in range(len(self.partitions)):
                if self.allocated[i] is None and self.partitions[i] >= size:
                    if best_size is None or self.partitions[i] < best_size:
                        best_index = i
                        best_size = self.partitions[i]
            return best_index
        elif strategy == "worst_fit":
            worst_index = None
            worst_size = None
            for i in range(len(self.partitions)):
                if self.allocated[i] is None and self.partitions[i] >= size:
                    if worst_size is None or self.partitions[i] > worst_size:
                        worst_index = i
                        worst_size = self.partitions[i]
            return worst_index
        return None


class DynamicMemoryAllocation:
    def __init__(self, memory_size):
        self.memory_size = memory_size
        self.memory = [(0, memory_size, None)]  # (start, size, process_id)

    def allocate(self, process_id, size, strategy="first_fit"):
        index = self._find_block(size, strategy)
        if index is not None:
            start, block_size, pid = self.memory[index]
            # Allocate the block
            self.memory[index] = (start + size, block_size - size, None)
            if self.memory[index][1] == 0:
                self.memory.pop(index)
            self.memory.append((start, size, process_id))
            self.memory.sort()
            return True
        return False

    def deallocate(self, process_id):
        self.memory = [(start, size, pid) if pid != process_id else (start, size, None)
                       for start, size, pid in self.memory]
        self.merge_free_blocks()

    def merge_free_blocks(self):
        merged_memory = []
        for block in sorted(self.memory):
            if merged_memory and merged_memory[-1][2] is None and block[2] is None:
                last_start, last_size, _ = merged_memory.pop()
                merged_memory.append((last_start, last_size + block[1], None))
            else:
                merged_memory.append(block)
        self.memory = merged_memory

    def display(self):
        print("Dynamic Memory Allocation Status:")
        for start, size, pid in self.memory:
            if pid is None:
                print(f"Free Block: Start {start}, Size {size}")
            else:
                print(f"Process {pid}: Start {start}, Size {size}")

    def _find_block(self, size, strategy):
        if strategy == "first_fit":
            for i, (start, block_size, pid) in enumerate(self.memory):
                if pid is None and block_size >= size:
                    return i
        elif strategy == "best_fit":
            best_index = None
            best_size = None
            for i, (start, block_size, pid) in enumerate(self.memory):
                if pid is None and block_size >= size:
                    if best_size is None or block_size < best_size:
                        best_index = i
                        best_size = block_size
            return best_index
        elif strategy == "worst_fit":
            worst_index = None
            worst_size = None
            for i, (start, block_size, pid) in enumerate(self.memory):
                if pid is None and block_size >= size:
                    if worst_size is None or block_size > worst_size:
                        worst_index = i
                        worst_size = block_size
            return worst_index
        return None


class BuddySystem:
    def __init__(self, size):
        self.size = size
        self.free_blocks = {size: [0]}

    def allocate(self, process_id, size):
        size = self._next_power_of_two(size)
        for current_size in sorted(self.free_blocks):
            if current_size >= size and self.free_blocks[current_size]:
                address = self.free_blocks[current_size].pop(0)
                if not self.free_blocks[current_size]:
                    del self.free_blocks[current_size]
                while current_size > size:
                    current_size //= 2
                    self.free_blocks.setdefault(current_size, []).append(address + current_size)
                return address
        return None

    def deallocate(self, address, size):
        size = self._next_power_of_two(size)
        while size <= self.size:
            buddy_address = address ^ size
            if buddy_address in self.free_blocks.get(size, []):
                self.free_blocks[size].remove(buddy_address)
                address = min(address, buddy_address)
                size *= 2
            else:
                self.free_blocks.setdefault(size, []).append(address)
                break

    def _next_power_of_two(self, x):
        return 1 << (x - 1).bit_length()

    def display(self):
        print("Buddy System Memory Allocation Status:")
        for size in sorted(self.free_blocks):
            print(f"Block size {size}: {self.free_blocks[size]}")


class Paging:
    def __init__(self, memory_size, page_size):
        self.memory_size = memory_size
        self.page_size = page_size
        self.frames = memory_size // page_size
        self.page_table = {}

    def allocate(self, process_id, process_size):
        pages_needed = (process_size + self.page_size - 1) // self.page_size
        allocated_frames = []
        for frame in range(self.frames):
            if frame not in self.page_table.values():
                allocated_frames.append(frame)
                if len(allocated_frames) == pages_needed:
                    break
        if len(allocated_frames) < pages_needed:
            return False
        for page in range(pages_needed):
            self.page_table[(process_id, page)] = allocated_frames[page]
        return True

    def deallocate(self, process_id):
        for key in list(self.page_table.keys()):
            if key[0] == process_id:
                del self.page_table[key]

    def display(self):
        print("Paging Memory Allocation Status:")
        for (process_id, page), frame in self.page_table.items():
            print(f"Process {process_id} Page {page} -> Frame {frame}")


def main():
    memory_size = int(input("Enter total memory size: "))
    technique = input("Select memory management technique (fixed, unequal, dynamic, buddy, paging): ")

    if technique == 'fixed':
        partition_size = int(input("Enter partition size: "))
        manager = FixedSizedPartitioning(memory_size, partition_size)
    elif technique == 'unequal':
        partitions = list(map(int, input("Enter partition sizes separated by space: ").split()))
        strategy = input("Select allocation strategy (first_fit, best_fit, worst_fit): ")
        manager = UnequalSizedPartitioning(partitions)
    elif technique == 'dynamic':
        strategy = input("Select allocation strategy (first_fit, best_fit, worst_fit): ")
        manager = DynamicMemoryAllocation(memory_size)
    elif technique == 'buddy':
        manager = BuddySystem(memory_size)
    elif technique == 'paging':
        page_size = int(input("Enter page size: "))
        manager = Paging(memory_size, page_size)
    else:
        print("Invalid technique selected")
        return

    while True:
        command = input("Enter command (allocate, deallocate, display, exit): ")
        if command == 'allocate':
            process_id = int(input("Enter process ID: "))
            size = int(input("Enter memory size required: "))
            if not manager.allocate(process_id, size, strategy):
                print("Allocation failed")
        elif command == 'deallocate':
            process_id = int(input("Enter process ID: "))
            manager.deallocate(process_id)
        elif command == 'display':
            manager.display()
        elif command == 'exit':
            break
        else:
            print("Invalid command")

if __name__ == "__main__":
    main()
