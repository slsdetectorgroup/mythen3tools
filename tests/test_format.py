import mythen3tools as m3
import numpy as np


def test_hexFormat():
    assert m3.hexFormat(500, 0) == "0x1f4"
    assert m3.hexFormat(500, 4) == "0x01f4"
    assert m3.hexFormat(500, 5) == "0x001f4"

    assert m3.hexFormat(np.uint64(1), 0) == "0x1"
    assert m3.hexFormat(np.int64(100), 4) == "0x0064"


def test_hexFormat_nox():
    assert m3.hexFormat_nox(500, 0) == "1f4"
    assert m3.hexFormat_nox(500, 4) == "01f4"
    assert m3.hexFormat_nox(500, 5) == "001f4"


def test_binFormat():
    assert m3.binFormat(123, 0) == "0b1111011"
    assert m3.binFormat(123, 1) == "0b1111011"
    assert m3.binFormat(123, 8) == "0b01111011"
    assert m3.binFormat(123, 10) == "0b0001111011"


def test_binFormat_nob():
    assert m3.binFormat_nob(123, 0) == "1111011"
    assert m3.binFormat_nob(123, 1) == "1111011"
    assert m3.binFormat_nob(123, 8) == "01111011"
    assert m3.binFormat_nob(123, 10) == "0001111011"


def test_decFormat():
    assert m3.decFormat(5, 0) == "5"
    assert m3.decFormat(53, 5) == "00053"
