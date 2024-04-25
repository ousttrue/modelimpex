import os
import io
import pathlib
import unittest
from humanoidio.mmd.pymeshio.pmd import pmd_reader, pmd_writer

if "PMD_FILE" in os.environ:
    PMD_FILE = pathlib.Path(os.environ["PMD_FILE"])

    class TestPmd(unittest.TestCase):
        def test_load(self):
            self.assertTrue(PMD_FILE.exists())
            with PMD_FILE.open("rb") as f:
                model = pmd_reader.read(f)
                assert model
                self.assertEqual(1.0, model.version)

                w = io.BytesIO()
                pmd_writer.write(w, model)
