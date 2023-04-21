def partition(arr, pivot):
    i = 0    # Initialize the partition index
    
    # Move all elements smaller than pivot to the left
    for j in range(len(arr)):
        if arr[j] < pivot:
            arr[i], arr[j] = arr[j], arr[i]    # Swap the elements
            i += 1    # Increment the partition index
    
    # Return the partition index
    return i

a = [1, 4, 2, 8, 5, 7]
print(partition(a, 3))
print(a)
