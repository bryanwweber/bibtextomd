#! /usr/bin/python3
# System imports
from datetime import datetime
import argparse
import warnings

# Package imports
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode

# Set the formatting identifiers. Since we're using kramdown, we
# don't have to use the HTML tags.
em = '_'
strong = '**'

# Set some HTML tags to go around each part of the reference.
open_span = '<span>'
close_span = '</span>'


# First is to define a function to format the names we get from BibTeX,
# since this task will be the same for every paper type.
def reorder(names, faname):
    """Format the string of author names and return a string.

    Adapated from one of the `customization` functions in
    `bibtexparser`.
    INPUT:
    names -- string of names to be formatted. The names from BibTeX are
             formatted in the style "Last, First Middle and Last, First
             Middle and Last, First Middle" and this is the expected
             style here.
    faname -- string of the initialized name of the author to whom
              formatting will be applied
    OUTPUT:
    nameout -- string of formatted names. The current format is
               "F.M. Last, F.M. Last, and F.M. Last".

    """
    # Set the format tag for the website's owner, to highlight where on
    # the author list the website owner is. Default is **
    my_name_format_tag = '**'

    # Convert the input string to a list by splitting the string at the
    # "and " and strip out any remaining whitespace.
    nameslist = [i.strip() for i in names.replace('\n', ' ').split("and ")]

    # Initialize a list to store the names after they've been tidied
    # up.
    tidynames = []

    # Loop through each name in the list.
    for namestring in nameslist:
        # Strip whitespace from the string
        namestring = namestring.strip()

        # If, for some reason, we've gotten a blank name, skip it
        if len(namestring) < 1:
            continue

        # Split the `namestring` at the comma, but only perform the
        # split once.
        namesplit = namestring.rsplit(',', 1)

        # In the expected format, the first element of the split
        # namestring is the last name. Strip any whitespace and {}.
        last = namesplit[0].strip().strip('{}')

        # There could be many first/middle names, so we collect them in
        # a list. All of the first/middle names are stored in the
        # second element of namesplit seperated by whitespace. Split
        # the first/middle names at the whitespace then strip out any
        # remaining whitespace and any periods (the periods will be
        # added in the proper place later).
        firsts = [i.strip().strip('.') for i in namesplit[1].split()]

        # For the case of hyphenated first names, we need to split at
        # the hyphen as well. Possible bug: this only works if the
        # first first name is the hyphenated one, and this replaces all
        # of the first names with the names split at the hyphen. We'd
        # like to handle multiple hyphens or a hyphenated name with an
        # initial more intelligently.
        if '-' in firsts[0]:
            firsts = firsts[0].split('-')

        # Now that all the first name edge cases are sorted out, we
        # want to initialize all the first names. Set the variable
        # initials to an empty string to we can add to it. Then loop
        # through each of the items in the list of first names. Take
        # the first element of each item and append a period, but no
        # space.
        initials = ''
        for item in firsts:
            initials += item[0] + '.'

        # Stick all of the parts of the name together in `tidynames`
        tidynames.append(initials + ' ' + last)

    # Find the case of the website author and set the format for that
    # name
    if faname is not None:
        try:
            i = tidynames.index(faname)
            tidynames[i] = my_name_format_tag + tidynames[i] + my_name_format_tag
        except ValueError:
            warnings.warn("Couldn't find {} in the names list. Sorry!".format(faname))

    # Handle the various cases of number of authors and how they should
    # be joined. Convert the elements of `tidynames` to a string.
    if len(tidynames) > 2:
        tidynames[-1] = 'and ' + tidynames[-1]
        nameout = ', '.join(tidynames)
    elif len(tidynames) == 2:
        tidynames[-1] = 'and ' + tidynames[-1]
        nameout = ' '.join(tidynames)
    else:
        # If `tidynames` only has one name, we only need to convert it
        # to a string. The first way that came to mind was to join the
        # list to an empty string.
        nameout = ''.join(tidynames)

    # Return `nameout`, the string of formatted authors
    return nameout


def journal_article(ref, faname):
    # Get the string of author names in the proper format from
    # the `reorder` function. Get some other information. Hack
    # the journal title to remove the '\' before '&' in
    # 'Energy & Fuels' because Mendeley inserts an extra '\'
    # into the BibTeX.
    authors = reorder(ref["author"], faname)
    title = ref["title"]
    journal = ref["journal"]
    if '\&' in journal:
        words = journal.strip().split('\&')
        journal = words[0] + '&' + words[1]

    # Start building the string containing the formatted
    # reference. Each bit should be surrounded by a span. The
    # {:.XYZ} is the kramdown notation to add that class to the
    # HTML tag. Each line should be ended with two spaces
    # before the newline so that kramdown inserts an HTML <br>
    # there.
    reference = (
        '\n{{:.paper}}\n{open}{title}{close}{{:.papertitle}}  \n'
        '{open}{authors}{close}{{:.authors}}  \n'
        '{open}{em}{journal}{em}, '.format(
            open=open_span, close=close_span, title=title, authors=authors, em=em,
            journal=journal,
            )
        )

    # Not all journal articles will have vol., no., and pp.
    # because some may be "In Press".
    if "volume" in ref:
        reference += 'vol. ' + ref["volume"] + ', '

    if "number" in ref:
        reference += 'no. ' + ref["number"] + ', '

    if "pages" in ref:
        reference += 'pp. ' + ref["pages"] + ', '

    month = ref["month"].title()
    year = ref["year"]
    if month == "May":
        month += ' '
    else:
        month += '. '

    reference += (
        '{month}{year}{close}{{:.journal}}  \n'.format(
            month=month, year=year, close=close_span,
            )
        )

    if "doi" in ref:
        reference += (
            '{open}{strong}DOI:{strong} [{doi}]'
            '(https://dx.doi.org/{doi}){close}{{:.doi}}  \n'.format(
                open=open_span, close=close_span, strong=strong,
                doi=ref["doi"],
                )
            )

    # Extra comments, such as links to files, should be stored
    # as "Notes" for each reference in Mendeley. Mendeley will
    # export this field with the tag "annote" in BibTeX.
    if "annote" in ref:
        reference += (
            '{open}{annote}{close}{{:.comment}}  \n'.format(
                open=open_span, close=close_span,
                annote=ref["annote"].replace('\\', ''),
                )
            )
    return reference


def in_proceedings(ref, faname):
    authors = reorder(ref["author"], faname)
    title = ref["title"]
    year = ref["year"]

    # Start building the reference string.
    reference = (
        '\n{{:.paper}}\n{open}{title}{close}{{:.papertitle}}  \n'
        '{open}{authors}{close}{{:.authors}}  \n'
        '{open}'.format(
            open=open_span, close=close_span, title=title, authors=authors,
            )
        )

    # Since Mendeley doesn't allow customization of BibTeX
    # output, we hack the "pages" field to contain the paper
    # number for the conference paper. Not all of this type of
    # reference will have this, so we check for it.
    if "pages" in ref:
        paperno = ref["pages"]
        reference += paperno + ', '

    # Insert the conference title, stored in the "booktitle"
    # field.
    conf = ref["booktitle"]
    reference += conf + ', '
    if "organization" in ref:
        reference += ref["organization"] + ', '
    if "address" in ref:
        reference += ref["address"] + ', '

    month = ref["month"].title()
    if month == "May":
        month += ' '
    else:
        month += '. '

    reference += (
        '{month}{year}{close}{{:.journal}}  \n'.format(
            month=month, year=year, close=close_span,
            )
        )

    if "doi" in ref:
        reference += (
            '{open}{strong}DOI:{strong} [{doi}]'
            '(https://dx.doi.org/{doi}){close}{{:.doi}}  \n'.format(
                open=open_span, strong=strong, doi=ref["doi"],
                close=close_span,
                )
            )

    # Extra comments, such as links to files, should be stored
    # as "Notes" for each reference in Mendeley. Mendeley will
    # export this field with the tag "annote" in BibTeX.
    if "annote" in ref:
        reference += (
            '{open}{annote}{close}{{:.comment}}  \n'.format(
                open=open_span, annote=ref["annote"].replace('\\', ''),
                close=close_span,
                )
            )
    return reference


def phd_thesis(ref, faname):
    authors = reorder(ref["author"], faname)
    title = ref["title"]
    year = ref["year"]

    reference = (
        '\n{{:.paper}}\n{open}{title}{close}{{:.papertitle}}  \n'
        '{open}{authors}{close}{{:.authors}}  \n'
        '{open}'.format(
            open=open_span, close=close_span, title=title, authors=authors,
            )
        )
    if "school" in ref:
        reference += ref["school"] + ', '
    if "month" in ref:
        month = ref["month"].title()
        if month == "May":
            month += ' '
        else:
            month += '. '
        reference += month

    reference += year + close_span + '{:.journal}  \n'

    if "annote" in ref:
        reference += (
            '{open}{annote}{close}{{:.comment}}  \n'.format(
                open=open_span, annote=ref["annote"].replace('\\', ''),
                close=close_span,
                )
            )
    return reference


def load_bibtex(bib_file_name):
    # Open and parse the BibTeX file in `bib_file_name` using
    # `bibtexparser`
    with open(bib_file_name, 'r') as bib_file:
        bp = BibTexParser(bib_file.read(), customization=convert_to_unicode)

    # Get a dictionary of dictionaries of key, value pairs from the
    # BibTeX file. The structure is
    # {ID:{authors:...},ID:{authors:...}}.
    refsdict = bp.get_entry_dict()

    # Create a list of all the types of documents found in the BibTeX
    # file, typically `article`, `inproceedings`, and `phdthesis`.
    # Dedupe the list.
    entry_types = []
    for k, ref in refsdict.items():
        entry_types.append(ref["ENTRYTYPE"])
    entry_types = set(entry_types)

    # For each of the types of reference, we need to sort each by month
    # then year. We store the dictionary representing each reference in
    # a sorted list for each type of reference. Then we store each of
    # these sorted lists in a dictionary whose key is the type of
    # reference and value is the list of dictionaries.
    sort_dict = {}
    for t in entry_types:
        temp = sorted([val for key, val in refsdict.items()
                      if val["ENTRYTYPE"] == t], key=lambda l:
                      datetime.strptime(l["month"], '%b').month, reverse=True)
        sort_dict[t] = sorted(temp, key=lambda k: k["year"], reverse=True)

    return sort_dict


def main(argv):
    arg_parser = argparse.ArgumentParser(
        description=(
            "Convert a BibTeX file to kramdown output with optional author highlighting."
            ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
    arg_parser.add_argument(
        "-b", "--bibfile",
        help="Set the filename of the BibTeX reference file.",
        default="refs.bib",
        type=str,
        )
    arg_parser.add_argument(
        "-o", "--output",
        help="Set the filename of the kramdown output.",
        default="pubs.md",
        type=str,
        )
    arg_parser.add_argument(
        "-a", "--author",
        help="Set the name of the author to be highlighted.",
        type=str,
        )

    args = arg_parser.parse_args(argv)
    bib_file_name = args.bibfile
    output_file_name = args.output
    faname = args.author

    sort_dict = load_bibtex(bib_file_name)

    # Open the output file with utf-8 encoding, write mode, and Unix
    # newlines.
    with open(output_file_name, encoding='utf-8', mode='w',
              newline='') as out_file:

        # Start with journal articles.
        out_file.write('Journal Articles\n---\n')

        # To get the year numbering correct, we have to set a dummy
        # value for pubyear (usage described below).
        pubyear = ''

        # Loop through all the references in the article type. The
        # logic in this loop (and the loops for the other reference
        # types) is not amenable to generalization due to different
        # information for each reference type. Therefore, its easiest
        # to write out the logic for each loop instead of writing the
        # logic into a function and calling that.
        for ref in sort_dict["article"]:
            # Get the publication year. If the year of the current
            # reference is not equal to the year of the previous
            # reference, we need to set `pubyear` equal to `year`.
            year = ref["year"]
            if year != pubyear:
                pubyear = year
            write_year = '\n{{:.year}}\n### {}\n'.format(year)
            out_file.write(write_year)

            out_file.write(journal_article(ref, faname))

        # Next are conference papers and posters.
        out_file.write('\nConference Publications and Posters\n---\n')

        # Same trick for the pubyear as for the journal articles.
        pubyear = ''

        # Loop through the references in the `inproceedings` type.
        for ref in sort_dict["inproceedings"]:
            year = ref["year"]
            if year != pubyear:
                pubyear = year
                write_year = '\n{{:.year}}\n### {}\n'.format(year)
                out_file.write(write_year)

            out_file.write(in_proceedings(ref, faname))

        # Finally are the theses and dissertations. Same general logic
        # as for the other reference types.
        pubyear = ''
        for ref in sort_dict["phdthesis"]:
            year = ref["year"]
            if year != pubyear:
                pubyear = year
                write_year = '{{:.year}}\n### {}\n'.format(year)

            reference = phd_thesis(ref, faname)

                out_file.write(write_year)
                out_file.write(reference)
