"""
Testing module for bib.py
"""
import os
import pytest
from bibtextomd.bib import main, reorder, load_bibtex, journal_article, in_proceedings, thesis


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


def test_and_in_name():
    names = 'Cooler, Brandywine W.'
    n = reorder(names, None)
    assert n == 'B.W. Cooler'


def test_no_highlighted_name():
    names = 'Author, First A.'
    n = reorder(names, None)
    assert n == 'F.A. Author'


def test_hyphenated_name():
    names = 'Name, Hypen-Ated'
    n = reorder(names, None)
    assert n == 'H.A. Name'


def test_empty_name():
    names = 'Name, First A. and and Name, Second A.'
    n = reorder(names, None)
    assert n == 'F.A. Name and S.A. Name'


def test_junior_name():
    names = 'Name, Jr, First A. and Name, Second A.'
    n = reorder(names, None)
    assert n == 'F.A. Name, Jr and S.A. Name'


def test_from_name():
    names = 'van Name, First A.'
    n = reorder(names, None)
    assert n == 'F.A. van Name'


@pytest.fixture
def load_bibtex_for_test():
    return load_bibtex('tests/refs.bib')


def test_journal_article(load_bibtex_for_test):
    articles = load_bibtex_for_test["article"]
    for a in articles:
        if a['ID'] == 'Author2013':
            ref = a
    reference = journal_article(ref, None)
    reference_blessed = (
        "\n{:.paper}\n"
        "<span>A study of the best ways to make up a name</span>{:.papertitle}  \n"
        "<span>F.A. Author, S.B. Sécond, and T.C. Third</span>{:.authors}  \n"
        "<span>_Journal Of Made Up Names & Words_, Aug. 2013</span>{:.journal}  \n"
        "<span>**DOI:** [10.0000/made-up-doi](https://dx.doi.org/10.0000/made-up-doi)</span>"
        "{:.doi}  \n"
        )
    assert reference == reference_blessed


def test_journal_article_2(load_bibtex_for_test):
    articles = load_bibtex_for_test["article"]
    for a in articles:
        if a['ID'] == 'Author2011':
            ref = a
    reference = journal_article(ref, None)
    reference_blessed = (
        "\n{:.paper}\n"
        "<span>A follow up study on made up names</span>{:.papertitle}  \n"
        "<span>F.A. Author</span>{:.authors}  \n"
        "<span>_Journal of Made Up Names_, vol. 2, no. 4, pp. 1100--1232, May 2011</span>"
        "{:.journal}  \n"
        "<span>**DOI:** [10.0000/made-up-doi](https://dx.doi.org/10.0000/made-up-doi)</span>"
        "{:.doi}  \n"
        "<span>The files can be found at the following link</span>{:.comment}  \n"
        )
    assert reference == reference_blessed


def test_in_proceedings(load_bibtex_for_test):
    ref = load_bibtex_for_test["inproceedings"][1]
    reference = in_proceedings(ref, None)
    reference_blessed = (
        "\n{:.paper}\n"
        "<span>How to properly cite media</span>{:.papertitle}  \n"
        "<span>S.B. Second, T.C. Third, S. Fourth-Fifth, and F.A. Author</span>{:.authors}  \n"
        "<span>Paper 2A12, 1st International Conference on BibTeX, University, Anytown, CA, "
        "May 2013</span>{:.journal}  \n"
        "<span>The files for this paper can be found at the following link</span>{:.comment}  \n"
        )
    assert reference == reference_blessed


def test_in_proceedings_2(load_bibtex_for_test):
    ref = load_bibtex_for_test["inproceedings"][0]
    reference = in_proceedings(ref, None)
    reference_blessed = (
        "\n{:.paper}\n"
        "<span>How to properly cite media</span>{:.papertitle}  \n"
        "<span>S.B. Second, T.C. Third, S. Fourth-Fifth, and F.A. Author</span>{:.authors}  \n"
        "<span>Paper 2A12, 5th International Conference on BibTeX, University, Anytown, CA, "
        "Jun. 2016</span>{:.journal}  \n"
        "<span>**DOI:** [10.1000/conference-doi](https://dx.doi.org/10.1000/conference-doi)</span>"
        "{:.doi}  \n"
        )
    assert reference == reference_blessed


def test_thesis(load_bibtex_for_test):
    ref = load_bibtex_for_test["phdthesis"][0]
    reference = thesis(ref, None)
    reference_blessed = (
        "\n{:.paper}\n"
        "<span>The worst sources of name generation</span>{:.papertitle}  \n"
        "<span>F.A. Author</span>{:.authors}  \n"
        "<span>College, Aug. 2014</span>{:.journal}  \n"
        "<span>Files at the following link</span>{:.comment}  \n"
        )
    assert reference == reference_blessed


def test_main():
    args = '-b tests/refs.bib -o tests/pubs.md'.split()
    main(args)
    with open('tests/pubs.md', 'r') as pubs, open('tests/pubs_blessed.md', 'r') as blessed:
        assert pubs.read() == blessed.read()
    if os.path.exists('tests/pubs.md'):
        os.remove('tests/pubs.md')
