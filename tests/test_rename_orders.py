import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('rename_orders', Path(__file__).parents[1] / 'rename_orders.py')
renamer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renamer)


class RenameTests(unittest.TestCase):
    def test_order_number_moves_to_front_and_preserves_extension(self):
        self.assertEqual(renamer.build_new_name('Example_№123_Draft', '.xlsx'), '№123_Example_Draft.xlsx')
        self.assertIsNone(renamer.build_new_name('№123_Example', '.xlsx'))
        self.assertIsNone(renamer.build_new_name('Example_without_number', '.xlsx'))

    def test_scan_only_plans_supported_regular_files(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            source = folder / 'Example_№123.xlsx'
            source.write_bytes(b'synthetic')
            (folder / 'Example_№456.txt').touch()
            (folder / 'Subfolder_№789.xlsx').mkdir()
            self.assertEqual(renamer.scan_folder(folder), [(source, folder / '№123_Example.xlsx')])
            self.assertEqual(source.read_bytes(), b'synthetic')

    def test_cancel_preserves_input_names(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            source = folder / 'Example_№123.xlsx'
            source.touch()
            with patch.object(renamer.sys, 'argv', ['rename_orders.py', directory]), patch('builtins.input', return_value='n'), patch('builtins.print'):
                renamer.main()
            self.assertTrue(source.exists())
            self.assertFalse((folder / '№123_Example.xlsx').exists())

    def test_confirmed_run_skips_collision_and_keeps_both_original_contents(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            original = folder / 'Example_№123.xlsx'
            destination = folder / '№123_Example.xlsx'
            original.write_bytes(b'first')
            destination.write_bytes(b'existing')
            other = folder / 'Other_№456.xlsx'
            other.write_bytes(b'second')
            with patch.object(renamer.sys, 'argv', ['rename_orders.py', directory]), patch('builtins.input', return_value='y'), patch('builtins.print'):
                renamer.main()
            self.assertEqual(original.read_bytes(), b'first')
            self.assertEqual(destination.read_bytes(), b'existing')
            self.assertEqual((folder / '№456_Other.xlsx').read_bytes(), b'second')


if __name__ == '__main__':
    unittest.main()
