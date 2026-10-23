import hashlib
from pathlib import Path
import tempfile
import unittest
from lans_risk import verify_manifest

class IntegrityTests(unittest.TestCase):
    def test_detects_corruption_and_missing_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            evidence = root/'episode.json'
            evidence.write_bytes(b'{"collision": false}')
            manifest = {'episode.json':hashlib.sha256(evidence.read_bytes()).hexdigest()}
            self.assertEqual(verify_manifest(root, manifest), [])
            evidence.write_bytes(b'{"collision": true}')
            self.assertEqual(verify_manifest(root, manifest), ['changed: episode.json'])
            evidence.unlink()
            self.assertEqual(verify_manifest(root, manifest), ['missing: episode.json'])

if __name__ == '__main__':
    unittest.main()
