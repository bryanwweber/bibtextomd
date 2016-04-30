"""
Testing module for bib.py
"""
import pytest
from bibtextomd.bib import main, reorder, load_bibtex, journal_article


def test_single_author_good():
    names = 'Author, First A.'
    n = reorder(names, 'F.A. Author')
    assert n == '**F.A. Author**'


def test_two_authors_good():
    names = 'Author, First A. and Name, Second N.'
    n = reorder(names, 'F.A. Author')
    assert n == '**F.A. Author** and S.N. Name'


def test_three_authors_good():
    names = 'Author, First A. and Name, Second N. and Name, Unicode C.'
    n = reorder(names, 'F.A. Author')
    assert n == '**F.A. Author**, S.N. Name, and U.C. Name'


def test_unicode_good():
    names = 'Namé, Unicode C.'
    n = reorder(names, 'U.C. Namé')
    assert n == '**U.C. Namé**'


def test_missing_name():
    names = 'Author, First A.'
    with pytest.warns(UserWarning):
        reorder(names, 'Missing Author')


def test_no_highlighted_name():
    names = 'Author, First A.'
    n = reorder(names, None)
    assert n == 'F.A. Author'


def test_hyphenated_name():
    names = 'Name, Hypen-Ated'
    n = reorder(names, None)
    assert n == 'H.A. Name'


@pytest.fixture
def load_bibtex_for_test():
    return load_bibtex('tests/refs.bib')


def test_journal_article(load_bibtex_for_test):
    sort_dict = load_bibtex_for_test
    ref = sort_dict["article"][0]
    reference = journal_article(ref, None)
    reference_blessed = (
        "\n{:.paper}\n"
        "<span>A study of the best ways to make up a name</span>{:.papertitle}"
        "  \n<span>F.A. Author, S.B. Sécond, and T.C. Third</span>{:.authors}"
        "  \n<span>_Journal Of Made Up Names_, Aug. 2013</span>{:.journal}"
        "  \n<span>**DOI:** [10.0000/made-up-doi](http://dx.doi.org/10.0000/made-up-doi)</span>"
        "{:.doi}  \n"
        )
    assert reference == reference_blessed
