import os
import io
import pathlib
import unittest
from humanoidio.mmd.pymeshio.pmd import pmd_reader, pmd_writer
from humanoidio.mmd.pymeshio.pmx import pmx_reader, pmx_writer

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


if "PMX_FILE" in os.environ:
    PMX_FILE = pathlib.Path(os.environ["PMX_FILE"])

    class TestPmx(unittest.TestCase):
        def test_load(self):
            self.assertTrue(PMX_FILE.exists())
            print(PMX_FILE)
            with PMX_FILE.open("rb") as f:
                model = pmx_reader.read(f)
                assert model
                self.assertEqual(2.0, model.version)

                w = io.BytesIO()
                pmx_writer.write(w, model)
