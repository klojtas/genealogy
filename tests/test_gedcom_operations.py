import pytest
import os
from genealogy.gedcom_handler import Gedcom

def test_create_empty_gedcom(tmp_path):
    filepath = tmp_path / "empty.ged"
    Gedcom.create_empty_gedcom(str(filepath))
    assert filepath.exists()
    with open(filepath, 'r') as f:
        content = f.read()
        assert "0 HEAD" in content
        assert "0 TRLR" in content

def test_update_individual_name(tmp_path):
    # Create a dummy GEDCOM file for testing
    gedcom_content = """0 HEAD
1 CHAR UTF-8
1 GEDC
2 VERS 5.5.1
1 SUBM @SUBM@
0 @SUBM@ SUBM
1 NAME Test Submitter
0 @I1@ INDI
1 NAME John /Doe/
1 SEX M
0 TRLR
"""
    filepath = tmp_path / "test_update.ged"
    with open(filepath, 'w') as f:
        f.write(gedcom_content)

    gedcom = Gedcom(str(filepath))
    gedcom.update_individual_name("@I1@", "Jonathan /Doe/")

    with open(filepath, 'r') as f:
        content = f.read()
        assert "1 NAME Jonathan /Doe/" in content
        assert "1 NAME John /Doe/" not in content

def test_add_individual(tmp_path):
    gedcom_content = """0 HEAD
1 CHAR UTF-8
1 GEDC
2 VERS 5.5.1
1 SUBM @SUBM@
0 @SUBM@ SUBM
1 NAME Test Submitter
0 TRLR
"""
    filepath = tmp_path / "test_add.ged"
    with open(filepath, 'w') as f:
        f.write(gedcom_content)

    gedcom = Gedcom(str(filepath))
    gedcom.add_individual("Jane /Doe/", "F")

    with open(filepath, 'r') as f:
        content = f.read()
        assert "0 @I1@ INDI" in content
        assert "1 NAME Jane /Doe/" in content
        assert "1 SEX F" in content

def test_delete_individual(tmp_path):
    gedcom_content = """0 HEAD
1 CHAR UTF-8
1 GEDC
2 VERS 5.5.1
1 SUBM @SUBM@
0 @SUBM@ SUBM
1 NAME Test Submitter
0 @I1@ INDI
1 NAME John /Doe/
1 SEX M
0 @I2@ INDI
1 NAME Jane /Doe/
1 SEX F
0 TRLR
"""
    filepath = tmp_path / "test_delete.ged"
    with open(filepath, 'w') as f:
        f.write(gedcom_content)

    gedcom = Gedcom(str(filepath))
    gedcom.delete_individual("@I1@")

    with open(filepath, 'r') as f:
        content = f.read()
        assert "0 @I1@ INDI" not in content
        assert "1 NAME John /Doe/" not in content
        assert "0 @I2@ INDI" in content
        assert "1 NAME Jane /Doe/" in content
