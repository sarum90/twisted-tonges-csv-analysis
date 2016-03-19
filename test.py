import unittest

class TestTravisSetUp(unittest.TestCase):

  def test_passes(self):
      self.assertEqual('foo', 'foo')

if __name__ == '__main__':
    unittest.main()

