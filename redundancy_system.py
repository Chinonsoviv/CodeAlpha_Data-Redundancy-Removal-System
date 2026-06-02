import sqlite3
import hashlib
from bitarray import bitarray

class DataRedundancySystem:
    def __init__(self, database_path="cloud_database.db"):
        self.db_path = database_path
        
        # TASK 2: Validation Mechanism (In-Memory Bloom Filter for ultra-fast checks)
        self.filter_size = 5000
        self.bloom_filter = bitarray(self.filter_size)
        self.bloom_filter.setall(0)
        
        self._initialize_database()
        self._prime_validation_filter()

    def _initialize_database(self):
        """TASK 5: Ensure database accuracy and efficiency using structural keys."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # TASK 3 & 5: Using UNIQUE constraints to prevent duplicate database writes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cloud_storage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                raw_data TEXT NOT NULL,
                data_hash TEXT UNIQUE NOT NULL,
                classification TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def _get_hash(self, text_data):
        """Standardizes text formatting to reveal hidden duplicates."""
        clean_text = text_data.strip().lower()
        return hashlib.md5(clean_text.encode('utf-8')).hexdigest()

    def _prime_validation_filter(self):
        """Loads existing data hashes into memory to validate fresh streams."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT data_hash FROM cloud_storage")
        for row in cursor.fetchall():
            self._add_to_filter(row[0])
        conn.close()

    def _add_to_filter(self, data_hash):
        """Helper to map elements inside our validation filter."""
        index = int(data_hash, 16) % self.filter_size
        self.bloom_filter[index] = 1

    # ==========================================
    # TASK 1: IDENTIFY AND CLASSIFY SYSTEM
    # ==========================================
    def identify_and_classify(self, data_string):
        """
        Classifies incoming items into distinct states:
        - 'UNIQUE': Safe brand new record
        - 'REDUNDANT': Identical copy matches historical state
        - 'FALSE_POSITIVE': Filter flags it as matched, but verified unique inside DB
        """
        data_hash = self._get_hash(data_string)
        filter_index = int(data_hash, 16) % self.filter_size
        
        # Check if the validation layer flags it
        filter_match = self.bloom_filter[filter_index] == 1
        
        if not filter_match:
            return "UNIQUE", data_hash

        # Deep validation check inside the database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM cloud_storage WHERE data_hash = ?", (data_hash,))
        db_match = cursor.fetchone() is not None
        conn.close()

        if db_match:
            return "REDUNDANT", data_hash
        else:
            # It matched the memory index but doesn't exist in our DB!
            return "FALSE_POSITIVE", data_hash

    # ==========================================
    # TASK 2, 3 & 4: VALIDATION, PREVENTION & APPEND PIPELINE
    # ==========================================
    def process_incoming_data(self, raw_data):
        """Handles the live routing pipeline based on classifications."""
        # Task 1 & 2 execution
        classification, data_hash = self.identify_and_classify(raw_data)
        
        if classification == "REDUNDANT":
            # TASK 3: Prevent duplicate data from hitting database storage
            print(f"❌ Blocked: Data entry '{raw_data.strip()}' classified as REDUNDANT.")
            return False
            
        if classification == "FALSE_POSITIVE":
            print(f"⚠️ Flagged: False Positive index encounter cleared for unique item '{raw_data.strip()}'.")

        # TASK 4: Append only unique and verified data entries
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO cloud_storage (raw_data, data_hash, classification) VALUES (?, ?, ?)",
                (raw_data.strip(), data_hash, classification)
            )
            conn.commit()
            conn.close()
            
            # Update memory verification filter
            self._add_to_filter(data_hash)
            print(f"✅ Success: Appended unique entry '{raw_data.strip()}' to the database.")
            return True
            
        except sqlite3.IntegrityError:
            # Backup safety fallback for Task 3
            print(f"🔒 Database Layer Guard blocked accidental write for '{raw_data.strip()}'.")
            return False

# --- TASK TESTS ---
if __name__ == "__main__":
    import os
    # Reset old data runs for a clean test
    if os.path.exists("cloud_database.db"):
        os.remove("cloud_database.db")
        
    print("=== STARTING SYSTEM VERIFICATION TESTING ===")
    system = DataRedundancySystem()

    # Test Step A: Add fresh entries (Should parse as UNIQUE)
    print("\n--- Phase 1: Ingesting Unique Data ---")
    system.process_incoming_data("Sensor Location Alpha - Temp 22C")
    system.process_incoming_data("Sensor Location Beta - Temp 25C")

    # Test Step B: Submit Exact Duplicate (Should catch and drop)
    print("\n--- Phase 2: Ingesting Redundant Data ---")
    system.process_incoming_data("Sensor Location Alpha - Temp 22C")

    # Test Step C: Test Format-disguised Redundancy
    print("\n--- Phase 3: Ingesting Sneaky Formatted Redundancy ---")
    system.process_incoming_data("   SENSOR LOCATION ALPHA - TEMP 22C   ")

    print("\n=== VERIFICATION TESTING COMPLETE ===")