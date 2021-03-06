# -*- coding: utf-8 -*-
"""
Created on Sun May 13 16:23:28 2018

@author: marks
"""

BASIC_LATIN = [chr(c) for c in range(0x00, 0x0080)]
LATIN_1_SUPPLEMENT = [chr(c) for c in range(0x0080, 0x0100)]
LATIN_EXTENDED_A = [chr(c) for c in range(0x0100, 0x0180)]
LATIN_EXTENDED_B = [chr(c) for c in range(0x0180, 0x0250)]
SPACING_MODIFIER_LETTERS = [chr(c) for c in range(0x02B0, 0x0300)]
LATIN_EXTENDED_ADDITIONAL = [chr(c) for c in range(0x1E00, 0x1F00)]
LATIN_EXTENDED_C = [chr(c) for c in range(0x2C60, 0x2C80)]
LATIN_EXTENDED_D = [chr(c) for c in range(0xA720, 0xA800)]
LATIN_EXTENDED_E = [chr(c) for c in range(0xAB30, 0xAB70)]
IPA_EXTENSIONS = [chr(c) for c in range(0x0250, 0x02B00)]
PHONETIC_EXTENSIONS = [chr(c) for c in range(0x1D00, 0x1D80)]
PHONETIC_EXTENSIONS_SUPPLEMENT = [chr(c) for c in range(0x1D80, 0x1DC0)]
SUPERSCRIPTS_AND_SUBSCRIPTS = [chr(c) for c in range(0x1D80, 0x1DC0)]
LETTERLIKE_SYMBOLS = [chr(c) for c in range(0x2070, 0x20A0)]
NUMBER_FORMS = [chr(c) for c in range(0x2150, 0x2190)]
ARABIC_MARKS = list()
ARABIC_MARKS.extend([chr(c) for c in range(0x064B, 0x0660)])
ARABIC_MARKS.extend([chr(c) for c in range(0x06D6, 0x06DD)])
ARABIC_MARKS.extend([chr(c) for c in range(0x06DF, 0x06E5)])
ARABIC_MARKS.extend([chr(c) for c in range(0x06EA, 0x06EE)])
ARABIC_MARKS.extend([chr(c) for c in range(0x08E4, 0x08FF)])
