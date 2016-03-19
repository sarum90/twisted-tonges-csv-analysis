import unittest

class TestTravisSetUp(unittest.TestCase):

  def test_passes(self):
      self.assertEqual('foo', 'foo')

  def test_fails(self):
      self.assertEqual('foo', 'bar')

if __name__ == '__main__':
    unittest.main()

