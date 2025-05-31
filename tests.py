import unittest
import os
import shutil
from collections import defaultdict
from Foogle import Foogle, Console  


class TestFoogle(unittest.TestCase):
    TEST_DIR = "test_data"
    INDEX_FILE = "index.json"
    DOCS_FILE = "docs.json"

    def setUp(self):
        # Create a test directory and files
        os.makedirs(self.TEST_DIR, exist_ok=True)
        self.create_test_file("file1.txt", "This is a test file. Test.")
        self.create_test_file("file2.txt", "Another file for testing.  Another.")
        os.makedirs(os.path.join(self.TEST_DIR, "subdir"), exist_ok=True)
        self.create_test_file(os.path.join("subdir", "file3.txt"), "Subdirectory test file. Subdirectory.")
        self.foogle = Foogle(self.TEST_DIR)


    def tearDown(self):
        # Clean up the test directory and files
        shutil.rmtree(self.TEST_DIR)
        if os.path.exists(self.INDEX_FILE):
            os.remove(self.INDEX_FILE)
        if os.path.exists(self.DOCS_FILE):
            os.remove(self.DOCS_FILE)

    def create_test_file(self, filename, content):
        with open(os.path.join(self.TEST_DIR, filename), "w") as f:
            f.write(content)

    def test_clean_text(self):
        text = "This is a Test, with punctuation!?"
        expected = "this is a test with punctuation"
        self.assertEqual(self.foogle.clean_text(text), expected)

    def test_tokenize(self):
        text = "this is a test"
        expected = ["this", "is", "a", "test"]
        self.assertEqual(self.foogle.tokenize(text), expected)

    def test_read_file(self):
        content = self.foogle.read_file("file1.txt", self.TEST_DIR)
        self.assertEqual(content, "This is a test file. Test.")

    def test_build_index(self):
        # The build_index method is called in setUp, so we can check the index directly
        self.assertIn("test", self.foogle.index)
        self.assertIn(os.path.abspath(os.path.join(self.TEST_DIR, "file1.txt")), self.foogle.index["test"])
        self.assertEqual(self.foogle.index["test"][os.path.abspath(os.path.join(self.TEST_DIR, "file1.txt"))], 2) # test appears twice in file1.txt


    def test_check_if_update_needed(self):

        #Initial index
        self.assertIn("test", self.foogle.index)
        self.assertIn(os.path.abspath(os.path.join(self.TEST_DIR, "file1.txt")), self.foogle.index["test"])
        self.assertEqual(self.foogle.index["test"][os.path.abspath(os.path.join(self.TEST_DIR, "file1.txt"))], 2)

        # no update needed
        foogle_new = Foogle(self.TEST_DIR)
        self.assertEqual(foogle_new.index, self.foogle.index)

        # After file change needed update
        self.create_test_file("file1.txt", "New Content")

        foogle_new = Foogle(self.TEST_DIR)

        self.assertNotEqual(foogle_new.index, self.foogle.index)

    def test_hash_txt(self):
        text = "test string"
        expected_hash = "6f8e1f94240a5c6d92913a9219f7758640964a95731e4047c00e4e452a30c557"
        self.assertEqual(self.foogle.hash_txt(text), expected_hash)

    def test_write_and_read_docs(self):

        self.foogle.write_docs()
        loaded_docs = self.foogle.read_docs()
        self.assertEqual(self.foogle.documents, loaded_docs)

    def test_write_and_read_index(self):

        self.foogle.write_index()
        loaded_index = self.foogle.read_index()
        self.assertEqual(self.foogle.index, loaded_index)

    def test_calculate_idf(self):
        self.foogle.calculate_idf()
        self.assertIn("test", self.foogle.idf)
        # The exact IDF value will depend on the number of documents and the frequency of the term
        self.assertAlmostEqual(self.foogle.idf["test"], 0.0, places=4)

    def test_get_tf(self):
        term = "test"
        document = os.path.abspath(os.path.join(self.TEST_DIR, "file1.txt"))
        tf = self.foogle.get_tf(term, document)
        self.assertEqual(tf, 2)

        tf = self.foogle.get_tf("nonexistent", document)
        self.assertEqual(tf, 0)

        tf = self.foogle.get_tf(term, "nonexistent_file.txt")
        self.assertEqual(tf, 0)


    def test_tf_idf(self):
        term = "test"
        document = os.path.abspath(os.path.join(self.TEST_DIR, "file1.txt"))
        self.foogle.calculate_idf()  # IDF must be calculated first
        tf_idf = self.foogle.tf_idf(term, document)
        self.assertAlmostEqual(tf_idf, 0.0, places=4)


    def test_search(self):
        query = "search test"
        results = self.foogle.search(query)

        # Convert the dictionary keys to strings for comparison
        expected_file1 = os.path.abspath(os.path.join(self.TEST_DIR, "file1.txt"))

        # Check if the file is in result
        resulted_files = []
        for file in results:
            resulted_files.append(file[0])
        self.assertIn(expected_file1, resulted_files)


        # Check search with empty results
        query = "search nonexistentterm"
        results = self.foogle.search(query)
        self.assertEqual(results, [])

    def test_console_help_command(self, capsys): #Need to fix it
        Console.help_command()
        captured = capsys.readouterr()
        self.assertTrue("To move between directories use standart cd:" in captured.out) #TODO:: FIX it

    def test_console_cd_command(self):
        console = Console()
        current_directory = self.TEST_DIR
        new_directory = console.cd_command(current_directory + " cd subdir")
        self.assertEqual(new_directory, current_directory)
        new_directory = console.cd_command(current_directory + " cd ..")
        self.assertEqual(new_directory, current_directory)
        new_directory = console.cd_command(current_directory + " cd /abs/path")
        self.assertEqual(new_directory, current_directory)

        # Create subdir for test
        os.makedirs(os.path.join(self.TEST_DIR, "subdir"), exist_ok=True)
        new_directory = console.cd_command(self.TEST_DIR + " cd subdir")
        self.assertEqual(new_directory, self.TEST_DIR)

    def test_console_print_search_result(self, capsys): #Need to fix it
        results = [("file1.txt", (2, 0.5)), ("file2.txt", (1, 0.2))]
        Console.print_search_result(results)
        captured = capsys.readouterr()
        self.assertTrue("<-----------------Finded some files:---------------->" in captured.out) #TODO:: FIX it


if __name__ == "__main__":
    unittest.main()