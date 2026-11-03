"""Guard automatic sizing and coverage as the configured stack grows."""
import copy
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import build_tech_carousel as builder
from tech_stack import header_picture


class TechCarousel(TestCase):
    def test_header_never_selects_a_static_source_for_system_motion_preferences(self):
        markup = header_picture()
        self.assertNotIn('prefers-reduced-motion', markup)
        self.assertNotIn('-reduced.svg', markup)
        self.assertIn('profile-header-mobile.svg', markup)
        self.assertIn('profile-header-light.svg', markup)

    def test_new_long_label_expands_slot_without_clipping(self):
        spec = copy.deepcopy(builder.STACK)
        before, _ = builder.layout(spec)
        spec['technologies'].append({'id': 'new-tool', 'name': 'A newly learned development technology'})
        slot, period = builder.layout(spec)
        self.assertGreater(slot, before)
        self.assertEqual(period, len(spec['technologies']) * slot)

    def test_one_item_still_covers_viewport_at_both_loop_endpoints(self):
        spec = copy.deepcopy(builder.STACK)
        spec['technologies'] = spec['technologies'][:1]
        with TemporaryDirectory() as temporary, patch.object(builder, 'MEDIA', Path(temporary)), patch.object(builder, 'STACK', spec):
            name, record = builder.carousel()
            doc = ET.parse(Path(temporary) / f'{name}.svg')
        ns = {'s': 'http://www.w3.org/2000/svg'}
        positions = [float(el.attrib['x']) for el in doc.findall('.//s:use', ns)]
        period = record['period']
        self.assertEqual(positions, [i * period for i in range(len(positions))])
        for offset in (-period, 0):
            self.assertLessEqual(positions[0] + offset, 0)
            self.assertGreaterEqual(positions[-1] + offset + period, record['width'])

    def test_invalid_ids_and_empty_stack_fail_before_writing(self):
        spec = copy.deepcopy(builder.STACK)
        spec['technologies'].append(spec['technologies'][0])
        with self.assertRaisesRegex(ValueError, 'unique'): builder.layout(spec)
        spec['technologies'] = []
        with self.assertRaisesRegex(ValueError, 'at least one'): builder.layout(spec)
