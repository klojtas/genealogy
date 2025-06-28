import pytest
from genealogy.gedcom_handler import Gedcom

def test_gedcom_parsing():
    gedcom = Gedcom(r'c:\01 Projects\genealogy\test.ged')
    assert len(gedcom.individuals) == 2
    assert gedcom.individuals[0].name == "John /Doe/"
    assert gedcom.individuals[1].name == "Jane /Doe/"
