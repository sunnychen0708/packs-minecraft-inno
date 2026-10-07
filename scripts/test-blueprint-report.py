"""Reject report schemas that cannot safely use independent property matching."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('matcher_generator', Path(__file__).with_name('gen-blueprint-matcher.py'))
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)


class ReportValidation(unittest.TestCase):
    def setUp(self):
        self.block = {
            'properties': {'axis': ['x', 'y'], 'lit': ['false', 'true']},
            'states': [
                {'properties': {'axis': axis, 'lit': lit}, **({'default': True} if (axis, lit) == ('x', 'false') else {})}
                for axis in ('x', 'y') for lit in ('false', 'true')
            ],
        }

    def parse(self, block):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'blocks.json'
            path.write_text(json.dumps({'minecraft:test': block}), encoding='utf-8')
            return generator.snapshot_from_report(path)

    def test_complete_product(self):
        self.assertEqual(self.parse(self.block)['minecraft:test']['properties'], self.block['properties'])

    def test_duplicate_hides_missing_combination(self):
        self.block['states'][-1] = copy.deepcopy(self.block['states'][1])
        with self.assertRaises(SystemExit):
            self.parse(self.block)

    def test_unlisted_value_with_same_count(self):
        self.block['states'][-1]['properties']['axis'] = 'z'
        with self.assertRaises(SystemExit):
            self.parse(self.block)

    def test_missing_or_extra_property(self):
        for props in ({'axis': 'y'}, {'axis': 'y', 'lit': 'true', 'extra': 'x'}):
            self.block['states'][-1]['properties'] = props
            with self.assertRaises(SystemExit):
                self.parse(self.block)

    def test_exactly_one_default(self):
        self.block['states'][1]['default'] = True
        with self.assertRaises(SystemExit):
            self.parse(self.block)

    def test_no_properties(self):
        self.assertEqual(self.parse({'states': [{'default': True}]}), {'minecraft:test': {}})


if __name__ == '__main__':
    unittest.main()
