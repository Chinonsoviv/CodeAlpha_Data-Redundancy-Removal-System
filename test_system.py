import unittest
from cloud_redundancy import CloudRedundancySystem

class TestRedundancySystem(unittest.TestCase):
    def setUp(self):
        # Set up a fresh instance of your system before each test
        self.system = CloudRedundancySystem()

    def test_unique_insertion(self):
        """Verify that completely new data is accepted."""
        result = self.system.process_incoming_data("Unique Record 100")
        self.assertTrue(result)

    def test_duplicate_blocking(self):
        """Verify that exact copies are identified and blocked."""
        self.system.process_incoming_data("Duplicate Record 200")
        # Try inserting it a second time
        result = self.system.process_incoming_data("Duplicate Record 200")
        self.assertFalse(result)

    def test_formatting_normalization(self):
        """Verify that trailing spaces and uppercase characters are neutralized."""
        self.system.system = CloudRedundancySystem() # clear cache
        self.system.process_incoming_data("Clean Record 300")
        # Try a messy duplicate version
        result = self.system.process_incoming_data("   CLEAN RECORD 300   ")
        self.assertFalse(result)

if __name__ == "__main__":
    print("=== RUNNING AUTOMATED UNIT TESTS ===")
    unittest.main()