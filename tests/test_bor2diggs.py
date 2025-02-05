from pytest_cases import pytest_fixture_plus

import pydiggs
import bor2diggs

from . import INPUT_BOR_FILES
from . import INPUT_FILES_DIR
from .utils import assert_same_files


@pytest_fixture_plus(
    scope="function",
    params=INPUT_BOR_FILES,
    ids=[p.relative_to(INPUT_FILES_DIR).as_posix() for p in INPUT_BOR_FILES],
)
def bor_filename(request):
    if request.param.as_posix().lower().endswith(".bor"):
        yield request.param


def test_diggs_export(bor_filename, tmp_path):
    output_filename = tmp_path / "output.diggs.xml"
    output_filename.write_text(bor2diggs.convert_to_diggs(bor_filename))
    assert_same_files(output_filename, bor_filename.with_suffix(".diggs.xml"))


def test_diggs_validation(bor_filename, tmp_path):
    output_filename = tmp_path / "output.diggs.xml"
    output_filename.write_text(bor2diggs.convert_to_diggs(bor_filename))
    validation = pydiggs.validator(output_filename)

    __import__("pdb").set_trace()
    # Schema validation (using default DIGGS Schema v2.6)
    validation.schema_check()

    # Dictionary validation (using default DIGGS Dictionary)
    validation.dictionary_check()

    assert_same_files(output_filename, bor_filename.with_suffix(".diggs.xml"))
