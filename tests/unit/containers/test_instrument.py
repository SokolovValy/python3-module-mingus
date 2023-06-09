# -*- coding: utf-8 -*-
from __future__ import absolute_import

import unittest

from mingus.containers.instrument import Instrument, Piano, Guitar
from mingus.containers.note_container import NoteContainer


class test_Instrument(unittest.TestCase):
    def setUp(self):
        self.i = Instrument()
        self.p = Piano()
        self.g = Guitar()
        self.notes = NoteContainer(["A", "B", "C", "D", "E"])
        self.noteslow = NoteContainer(["C-0", "D-0", "E-0"])
        self.noteshigh = NoteContainer(["A-12", "B-12", "C-12", "D-12", "E-12"])

    def test_note_in_range(self):
        for x in self.notes:
            self.assertTrue(self.i.note_in_range(x))
            self.assertTrue(self.p.note_in_range(x))
            self.assertTrue(self.g.note_in_range(x))
        for x in self.noteslow + self.noteshigh:
            self.assertEqual(
                False,
                self.p.note_in_range(x),
                "%s should not be able to be played by a Piano" % x,
            )
            self.assertEqual(
                False,
                self.g.note_in_range(x),
                "%s should not be able to be played by a Guitar" % x,
            )

    def test_can_play_notes(self):
        self.assertTrue(self.i.can_play_notes(self.notes))
        self.assertTrue(self.p.can_play_notes(self.notes))
        self.assertTrue(self.g.can_play_notes(self.notes))
        self.assertEqual(False, self.p.can_play_notes(self.noteslow))
        self.assertEqual(False, self.g.can_play_notes(self.noteslow))
        self.assertEqual(False, self.p.can_play_notes(self.noteshigh))
        self.assertEqual(False, self.g.can_play_notes(self.noteshigh))
        self.assertEqual(
            False,
            self.g.can_play_notes(NoteContainer(["A", "B", "C", "D", "E", "F", "G"])),
        )
