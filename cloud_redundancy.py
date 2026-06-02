import json
import hashlib
from bitarray import bitarray

# Set this to True to simulate a successful cloud connection without network errors!
SIMULATE_CLOUD = True  

class CloudRedundancySystem:
    def __init__(self):
        self.filter_size = 5000
        self.bloom_filter = bitarray(self.filter_size)
        self.bloom_filter.setall(0)
        self.mock_cloud_db = set()  # Simulates cloud storage array

    def _get_hash(self, text_data):
        return hashlib.md5(text_data.strip().lower().encode('utf-8')).hexdigest()

    def identify_and_classify(self, data_string):
        data_hash = self._get_hash(data_string)
        filter_index = int(data_hash, 16) % self.filter_size
        
        if self.bloom_filter[filter_index] == 0:
            return "UNIQUE", data_hash
            
        if data_hash in self.mock_cloud_db:
            return "REDUNDANT", data_hash
        return "FALSE_POSITIVE", data_hash

    def process_incoming_data(self, raw_data):
        classification, data_hash = self.identify_and_classify(raw_data)
        
        if classification == "REDUNDANT":
            print(f"❌ Cloud Blocked: '{raw_data.strip()}' is a redundant entry!")
            return False

        # Add to Simulated Cloud Storage
        self.mock_cloud_db.add(data_hash)
        self.bloom_filter[int(data_hash, 16) % self.filter_size] = 1
        print(f"☁️ Cloud Success: Appended unique entry '{raw_data.strip()}' to the cloud database.")
        return True

if __name__ == "__main__":
    print("=== STARTING CLOUD DEDUPLICATION SYSTEM ===")
    system = CloudRedundancySystem()

    print("\n--- Sending unique points to the Cloud ---")
    system.process_incoming_data("Cloud Node Location 1 - active")
    system.process_incoming_data("Cloud Node Location 2 - standby")

    print("\n--- Testing Cloud Redundancy Prevention ---")
    system.process_incoming_data("Cloud Node Location 1 - active")

    print("\n--- Testing Formatting Normalization Bypass ---")
    system.process_incoming_data("   CLOUD NODE LOCATION 1 - ACTIVE   ")