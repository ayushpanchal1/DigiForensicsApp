import unittest
from app.core.data_collection import DataCollection

class TestDataCollection(unittest.TestCase):
    def test_collect_data(self):
        collector = DataCollection(image_path="test_image.raw")
        result = collector.collect_data()
        self.assertIsNotNone(result)

if __name__ == "__main__":
    unittest.main()
