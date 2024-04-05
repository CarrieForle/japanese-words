import unittest
import random
from importlib import import_module

jw = import_module('japanese-word')

class TestJapaneseWord(unittest.TestCase):
    def test_run(self):
        jw.run('desc', 'README.md')
        
if __name__ == '__main__':
    unittest.main()