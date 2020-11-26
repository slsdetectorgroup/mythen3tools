import patterntools as pt
import numpy as np


def test_hexFormat():
    assert pt.hexFormat(500, 0) == "0x1f4"
    assert pt.hexFormat(500, 4) == "0x01f4"
    assert pt.hexFormat(500, 5) == "0x001f4"

    assert pt.hexFormat(np.uint64(1), 0) == "0x1"
    assert pt.hexFormat(np.int64(100), 4) == "0x0064"


def test_hexFormat_nox():
    assert pt.hexFormat_nox(500, 0) == "1f4"
    assert pt.hexFormat_nox(500, 4) == "01f4"
    assert pt.hexFormat_nox(500, 5) == "001f4"


def test_binFormat():
    assert pt.binFormat(123, 0) == "0b1111011"
    assert pt.binFormat(123, 1) == "0b1111011"
    assert pt.binFormat(123, 8) == "0b01111011"
    assert pt.binFormat(123, 10) == "0b0001111011"


def test_binFormat_nob():
    assert pt.binFormat_nob(123, 0) == "1111011"
    assert pt.binFormat_nob(123, 1) == "1111011"
    assert pt.binFormat_nob(123, 8) == "01111011"
    assert pt.binFormat_nob(123, 10) == "0001111011"


def test_decFormat():
    assert pt.decFormat(5, 0) == "5"
    assert pt.decFormat(53, 5) == "00053"


def test_hex_formatting():
    assert pt.to_hex(5, width = 4) == '0x0005'



