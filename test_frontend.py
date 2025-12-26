import execjs

js_code = """
function isLetters(str) {
  return /^[A-Za-z]+$/.test(str);
}

function isDigits(str) {
  return /^[0-9]+$/.test(str);
}

function runValidation(mode, value1, value2) {

  // IBAN validation
  if (mode === "IBAN") {
    if (value1.length !== 22) {
      return [false, "Error: IBAN must be exactly 22 characters long."];
    }

    var countryCode = value1.slice(0, 2);
    var rest = value1.slice(2);

    if (!isLetters(countryCode)) {
      return [false, "Error: The first two characters of an IBAN must be letters."];
    }

    if (!isDigits(rest)) {
      return [false, "Error: Characters 3-22 of an IBAN must be digits."];
    }
  }

  // KNR / BLZ validation
  if (mode === "KNRBLZ") {
    if (value1.length !== 10 || !isDigits(value1)) {
      return [false, "Error: KNR must be exactly 10 digits."];
    }

    if (value2.length !== 8 || !isDigits(value2)) {
      return [false, "Error: BLZ must be exactly 8 digits."];
    }
  }

  return [true, ""];
}
"""

ctx = execjs.compile(js_code)

#IBAN TESTS

def test_valid_iban():
    ok, msg = ctx.call(
        "runValidation",
        "IBAN",
        "DE44500105171234567890",
        ""
    )
    assert ok is True
    assert msg == ""

#mips does this test by itself so js should not
def test_valid_iban():
    ok, msg = ctx.call(
        "runValidation",
        "IBAN",
        "de44500105171234567890",
        ""
    )
    assert ok is True
    assert msg == ""


def test_invalid_iban_length():
    ok, msg = ctx.call(
        "runValidation",
        "IBAN",
        "DE123",
        ""
    )
    assert ok is False
    assert "22 characters" in msg


def test_invalid_iban_country_code():
    ok, msg = ctx.call(
        "runValidation",
        "IBAN",
        "D144500105171234567890",
        ""
    )
    assert ok is False
    assert "first two characters" in msg


def test_invalid_iban_digits():
    ok, msg = ctx.call(
        "runValidation",
        "IBAN",
        "DE44A00105171234567890",
        ""
    )
    assert ok is False
    assert "3-22" in msg


#KNR/BLZ tests

def test_valid_knr_blz():
    ok, msg = ctx.call(
        "runValidation",
        "KNRBLZ",
        "1234567890",
        "50010517"
    )
    assert ok is True
    assert msg == ""


def test_invalid_knr():
    ok, msg = ctx.call(
        "runValidation",
        "KNRBLZ",
        "12345",
        "50010517"
    )
    assert ok is False
    assert "KNR must be exactly 10 digits" in msg


def test_invalid_blz():
    ok, msg = ctx.call(
        "runValidation",
        "KNRBLZ",
        "1234567890",
        "5001"
    )
    assert ok is False
    assert "BLZ must be exactly 8 digits" in msg