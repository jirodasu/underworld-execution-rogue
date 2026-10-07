import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'game'))
import storage

class StorageTests(unittest.TestCase):
    def test_best_survives_reload(self):
        with tempfile.TemporaryDirectory() as d, patch.object(storage.Path,'home',return_value=Path(d)):
            self.assertEqual(storage.load(),0)
            self.assertTrue(storage.save(286))
            self.assertEqual(storage.load(),286)

    def test_corrupt_record_does_not_stop_game(self):
        with tempfile.TemporaryDirectory() as d, patch.object(storage.Path,'home',return_value=Path(d)):
            (Path(d)/'.underworld-bureau-v2.json').write_text('broken')
            self.assertEqual(storage.load(),0)
