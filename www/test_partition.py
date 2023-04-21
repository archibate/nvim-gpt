import unittest

from partition import partition

class TestPartition(unittest.TestCase):
    
    def test_empty_array(self):
        arr = []
        pivot = 5
        result = partition(arr, pivot)
        self.assertEqual(result, 0)
        
    def test_all_elements_greater_than_pivot(self):
        arr = [10, 21, 34, 27]
        pivot = 5
        result = partition(arr, pivot)
        self.assertEqual(result, 0)
        
    def test_all_elements_smaller_than_pivot(self):
        arr = [2, 1, 4, 3]
        pivot = 5
        result = partition(arr, pivot)
        self.assertEqual(result, len(arr))
        
    def test_some_elements_equal_to_pivot(self):
        arr = [4, 1, 5, 3, 5]
        pivot = 5
        result = partition(arr, pivot)
        self.assertEqual(result, 3)
        
    def test_all_elements_equal_to_pivot(self):
        arr = [5, 5, 5, 5, 5]
        pivot = 5
        result = partition(arr, pivot)
        self.assertEqual(result, len(arr))
        
    def test_negative_and_positive_values(self):
        arr = [-5, 2, 0, 3, -1]
        pivot = 0
        result = partition(arr, pivot)
        self.assertEqual(result, 3)
        
    def test_duplicate_values(self):
        arr = [1, 4, 3, 4, 2, 4]
        pivot = 4
        result = partition(arr, pivot)
        self.assertEqual(result, 4)
        
    def test_pivot_not_present(self):
        arr = [1, 2, 3, 4, 5]
        pivot = 6
        result = partition(arr, pivot)
        self.assertEqual(result, len(arr))
        
    def test_only_one_element(self):
        arr = [5]
        pivot = 5
        result = partition(arr, pivot)
        self.assertEqual(result, 1)
        
    def test_large_array(self):
        arr = [34, 65, 12, 19, 3, 67, 42, 98, 5, 76, 19, 23, 1, 44, 90, 98, 1, 3, 2, 5, 87, 76, 99, 33, 23, 10, 80, 54, 31, 60]
        pivot = 50
        result = partition(arr, pivot)
        self.assertEqual(result, 20)

if __name__ == '__main__':
    unittest.main()
