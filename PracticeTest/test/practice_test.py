import unittest

import sys
sys.path.append("..")
from src.practice import Practice


class TestPractice(unittest.TestCase):

    def test_plus(self):
        self.assertEqual(Practice().plus(1, 1), 2)        
        
        
if __name__=='__main__':
    unittest.main()
    
