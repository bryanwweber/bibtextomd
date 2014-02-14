#! /usr/bin/python3
#######################################################################
#Bryan W. Weber, 27 Aug. 2013 13:46
#Take BibTeX bibliography and export citations in the format of my
#website, bryanwweber.com. The format of the output is kramdown, and
#is intended to be included in a file to be processed by Jekyll. The
#BibTeX file is expected to be from Mendeley, although Mendeley follows
#the standard conventions pretty well, so most BibTeX files should
#work. bibtexparser is Python 3 ONLY!
#
#v. 0.1.0 - initial release
#v. 0.1.1 - Fix escape character bug in annote field. Add help output
#           with option -h. 14-OCT-2013
#v. 0.2.0 - Add option to specify highlighted author name on the
#           command line input, -a. 04-NOV-2013
#v. 0.2.1 - Fix bug where no opening span tag was printed on the
#           university name line for the thesis. 04-NOV-2013
#v. 0.2.2 - Add shebang to the script so that it can be run directly
#           from the command line - no more `python3 bib.py -options`
#           needed, just `py bib.py -options` on Windows or `./bib.py
#           -options` on Unix type systems will do!
#v. 0.2.3 - Add better error printing. Define help message in one place
#           so it can be reused. Change option loopups to sets instead
#           of what they were before (tuples?).
#v. 0.2.4 - Add try:except for bibtexparser import to print an error if
#           bibtexparser is not installed. Change string formatting of
#           help string. 02-FEB-2014
#v. 0.2.5 - Fix newlines on Windows - only Unix style \n will be
#           written now. Print help if no options are specified on the
#           command line by the user. 14-FEB-2014
#######################################################################
#
#We need the BibTeX parser from the bibtexparser package on PyPI. If
#pip is installed, `pip install bibtexparser` will install the package.
#Code is tested with version 0.4, may not work with other versions.
#
try:
    from bibtexparser.bparser import BibTexParser
except ImportError:
    print("We need the BibTeX parser from the bibtexparser package on PyPI. "
          "If pip is installed, `pip install bibtexparser` will install the "
          "package. Code is tested with version 0.4, may not work with other "
          "versions.")
from datetime import datetime
import sys, getopt

#
#First is to define a function to format the names we get from BibTeX,
#since this task will be the same for every paper type. The current
#format is "F.M. Last, F.M. Last, and F.M. Last".
#
def reorder(names, faname='F.A. Author'):
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
              default: 'F.A. Author'
    OUTPUT:
    nameout -- string of formatted names.

    """
    #
    #Set the format tag for the website's owner, to highlight where on
    #the author list the website owner is. Default is **
    #
    myNameFormatTag = '**'
    #
    #Convert the input string to a list by splitting the string at the
    #" and " and strip out any remaining whitespace.
    #
    nameslist = [i.strip() for i in names.replace('\n', ' ').split(" and ")]
    #
    #Initialize a list to store the names after they've been tidied up.
    #
    tidynames = []
    #
    #Loop through each name in the list.
    #
    for namestring in nameslist:
        #
        #Strip whitespace from the string
        #
        namestring = namestring.strip()
        #
        #If, for some reason, we've gotten a blank name, skip it
        #
        if len(namestring) < 1:
            continue
        #
        #Split the `namestring` at the comma, but only perform the
        #split once.
        #
        namesplit = namestring.split(',', 1)
        #
        #In the expected format, the first element of the split
        #namestring is the last name. Strip any whitespace.
        #
        last = namesplit[0].strip()
        #
        #There could be many first/middle names, so we collect them in
        #a list. All of the first/middle names are stored in the second
        #element of namesplit seperated by whitespace. Split the first/
        #middle names at the whitespace then strip out any remaining
        #whitespace and any periods (the periods will be added in the
        #proper place later).
        #
        firsts = [i.strip().strip('.') for i in namesplit[1].split()]
        #
        #Handle the case of juniors.
        #
        if last in ['jnr', 'jr', 'junior']:
            last = firsts.pop()
        #
        #Handle the case of "from" in the name
        #
        for item in firsts:
            if item in ['ben', 'van', 'der', 'de', 'la', 'le']:
                last = firsts.pop() + ' ' + last
        #
        #For the case of hyphenated first names, we need to split at
        #the hyphen as well. Possible bug: this only works if the first
        #first name is the hyphenated one, and this replaces all of the
        #first names with the names split at the hyphen. We'd like to
        #handle multiple hyphens or a hyphenated name with an initial
        #more intelligently.
        #
        if '-' in firsts[0]:
            firsts = firsts[0].split('-')
        #
        #Now that all the first name edge cases are sorted out, we want
        #to initialize all the first names. Set the variable initials
        #to an empty string to we can add to it. Then loop through each
        #of the items in the list of first names. Take the first
        #element of each item and append a period, but no space.
        #
        initials = ''
        for item in firsts:
            initials = initials + item[0] + '.'
        #
        #Stick all of the parts of the name together in `tidynames`
        #
        tidynames.append(initials + ' ' + last)
    #
    #Find the case of the website author and set the format for that
    #name
    #
    try:
        i = tidynames.index(faname)
        tidynames[i] = myNameFormatTag + tidynames[i] + myNameFormatTag
    except ValueError:
        print("Couldn't find ",faname,"in the names list. Sorry!")
    #
    #Handle the various cases of number of authors and how they should
    #be joined. Convert the elements of `tidynames` to a string.
    #
    if len(tidynames) > 2:
        tidynames[-1] = 'and ' + tidynames[-1]
        nameout = ', '.join(tidynames)
    elif len(tidynames) == 2:
        tidynames[-1] = 'and ' + tidynames[-1]
        nameout = ' '.join(tidynames)
    else:
        #
        #If `tidynames` only has one name, we only need to convert it
        #to a string. The first way that came to mind was to join the
        #list to an empty string.
        #
        nameout = ''.join(tidynames)
    #print(nameout)
    #
    #Return `nameout`, the string of formatted authors
    #
    return nameout

def main(argv):
    bibFileName = 'refs.bib'
    outputFileName = 'pubs.md'
    faname = 'F.A. Author'
    help = ("Usage:\n"
    "-h, --help: Print this help dialog and exit\n"
    "-b filename, --bibfile=filename: Set the filename of the"
    "BibTeX reference file. Default: refs.bib\n"
    "-o filename, --output=filename: Set the filename of the"
    "kramdown output. Default: pubs.md\n"
    "-a 'author', --author='f.a. name': Set the name of the author"
    "to be highlighted. Default: 'F.A. Author'")
    try:
        opts, args = getopt.getopt(argv, "hb:o:a:",
                                   ["help", "bibfile=", "output=",
                                   "author="])
    except getopt.GetoptError as e:
        print("You did not enter an option properly. Please try again.")
        print(e)
        print(help)
        sys.exit(2)

    # If the user doesn't input any options, print the help.
    if not opts:
        print(help)
        sys.exit(0)

    for opt, arg in opts:
        if opt in {"-h", "--help"}:
            print(help)
            sys.exit()
        elif opt in {"-b", "--bibfile"}:
            bibFileName = arg
        elif opt in {"-o", "--output"}:
            outputFileName = arg
        elif opt in {"-a", "--author"}:
            faname = arg
    #
    #Set the formatting identifiers. Since we're using kramdown, we
    #don't have to use the HTML tags.
    #
    em = '_'
    st = '**'
    #
    #Set some HTML tags to go around each part of the reference.
    #
    openSpan = '<span>'
    closeSpan = '</span>'
    #
    #Open and parse the BibTeX file in `bibFileName` using
    #`bibtexparser`
    #
    with open(bibFileName,'r') as bibFile:
        bp = BibTexParser(bibFile)
    #
    #Get a dictionary of dictionaries of key, value pairs from the
    #BibTeX file. The structure is {ID:{authors:...},ID:{authors:...}}.
    #
    refsdict = bp.get_entry_dict()
    #
    #Create a list of all the types of documents found in the BibTeX
    #file, typically `article`, `inproceedings`, and `phdthesis`.
    #Dedupe the list.
    #
    types = []
    for k,ref in refsdict.items():
        types.append(ref["type"])
    types  = set(types)
    #
    #For each of the types of reference, we need to sort each by month
    #then year. We store the dictionary representing each reference in
    #a sorted list for each type of reference. Then we store each of
    #these sorted lists in a dictionary whose key is the type of
    #reference and value is the list of dictionaries.
    #
    sortDict = {}
    for type in types:
        temp = sorted([val for key, val in refsdict.items()
                      if val["type"] == type], key=lambda l:
                      datetime.strptime(l["month"],'%b').month, reverse=True)
        sortDict[type] = sorted(temp, key=lambda k: k["year"], reverse=True)
    #
    #Open the output file with utf-8 encoding and write mode.
    #
    with open(outputFileName, encoding='utf-8', mode='w',
              newline='') as outFile:
        #
        #Start with journal articles. Print the header to the screen
        #and output file.
        #
        print('Journal Articles\n---\n')
        outFile.write('Journal Articles\n---\n')
        #
        #To get the year numbering correct, we have to set a dummy
        #value for pubyear (usage described below).
        #
        pubyear = ''
        #
        #Loop through all the references in the article type. The logic
        #in this loop (and the loops for the other reference types) is
        #not amenable to generalization due to different information
        #for each reference type. Therefore, its easiest to write out
        #the logic for each loop instead of writing the logic into a
        #function and calling that.
        #
        for ref in sortDict["article"]:
            #
            #Get the string of author names in the proper format from
            #the `reorder` function. Get some other information. Hack
            #the journal title to remove the '\' before '&' in
            #'Energy & Fuels' because Mendeley inserts an extra '\'
            #into the BibTeX.
            #
            authors = reorder(ref["author"],faname)
            title = ref["title"]
            journal = ref["journal"]
            if '\&' in journal:
                words = journal.strip().split('\&')
                journal = words[0] + '&' + words[1]
            doi = ref["doi"]
            #
            #Get the publication year. If the year of the current
            #reference is not equal to the year of the previous
            #reference, we need to print the year out and set `pubyear`
            #equal to `year`.
            #
            year = ref["year"]
            if year != pubyear:
                pubyear = year
                stri = '\n{:.year}\n###' + year + '\n'
                print(stri)
                outFile.write(stri)
            #
            #Start building the string containing the formatted
            #reference. Each bit should be surrounded by a span. The
            #{:.XYZ} is the kramdown notation to add that class to the
            #HTML tag. Each line should be ended with two spaces before
            #the newline so that kramdown inserts an HTML <br> there.
            #
            string = ('\n{:.paper}\n' +
                      openSpan + title + closeSpan + '{:.papertitle}  \n' +
                      openSpan + authors + closeSpan + '{:.authors}  \n' +
                      openSpan + em + journal + em + ', '
                      )
            #
            #Not all journal articles will have vol., no., and pp.
            #because some may be "In Press".
            #
            if "volume" in ref:
                string = string + 'vol. ' + ref["volume"] + ', '

            if "number" in ref:
                string = string + 'no. ' + ref["number"] + ', '

            if "pages" in ref:
                string = string + 'pp. ' + ref["pages"] + ', '

            string = (string + ref["month"].title() + '. ' +
                      year + closeSpan + '{:.journal}  \n')

            if "doi" in ref:
                string = (string + openSpan + st + 'DOI:' + st + ' [' +
                          ref["doi"] + '](http://dx.doi.org/' + ref["doi"]
                          + ')' + closeSpan + '{:.doi}  \n'
                          )
            #
            #Extra comments, such as links to files, should be stored as
            #"Notes" for each reference in Mendeley. Mendeley will export
            #this field with the tag "annote" in BibTeX.
            #
            if "annote" in ref:
                string = (string + openSpan + ref["annote"].replace('\\','') +
                           closeSpan + '{:.comment}  \n'
                         )
            print(string)
            outFile.write(string)
        #
        #Next are conference papers and posters. Print the header to
        #the screen and the output file.
        #
        print('Conference Publications and Posters\n---\n')
        outFile.write('\nConference Publications and Posters\n---\n')
        #
        #Same trick for the pubyear as for the journal articles.
        #
        pubyear = ''
        #
        #Loop through the references in the `inproceedings` type.
        #
        for ref in sortDict["inproceedings"]:
            authors = reorder(ref["author"],faname)
            title = ref["title"]
            conf = ref["booktitle"]
            year = ref["year"]
            if year != pubyear:
                pubyear = year
                stri = '\n{:.year}\n###' + year + '\n'
                print(stri)
                outFile.write(stri)
            #
            #Start building the reference string.
            #
            string = ('\n{:.paper}\n' +
                      openSpan + title + closeSpan + '{:.papertitle}  \n' +
                      openSpan + authors + closeSpan + '{:.authors}  \n' +
                      openSpan
                     )
            #
            #Since Mendeley doesn't allow customization of BibTeX
            #output, we hack the "pages" field to contain the paper
            #number for the conference paper. Not all of this type of
            #reference will have this, so we check for it.
            #
            if "pages" in ref:
                paperno = ref["pages"]
                string = string + paperno + ', '
            #
            #Insert the conference title, stored in the "booktitle"
            #field.
            #
            string = string + conf + ', '
            if "organization" in ref:
                string = string + ref["organization"] + ', '
            if "address" in ref:
                string = string + ref["address"] + ', '

            string = (string + ref["month"].title() + '. ' + year + closeSpan
                      + '{:.journal}  \n'
                     )

            if "doi" in ref:
                string = (string + openSpan + st + 'DOI:' + st + ' [' +
                          ref["doi"] + '](http://dx.doi.org/' + ref["doi"]
                          + ')' + closeSpan + '{:.doi}  \n'
                         )
            #
            #Extra comments, such as links to files, should be stored as
            #"Notes" for each reference in Mendeley. Mendeley will export
            #this field with the tag "annote" in BibTeX.
            #
            if "annote" in ref:
                string = (string + openSpan + ref["annote"].replace('\\','') +
                          closeSpan + '{:.comment}  \n'
                         )
            print(string)
            outFile.write(string)
        #
        #Finally are the theses and dissertations. Same logic as for
        #the other reference types.
        #
        print("Master's Thesis\n---\n")
        outFile.write("\nMaster's Thesis\n---\n")
        pubyear = '2200'
        for ref in sortDict["phdthesis"]:
            authors = reorder(ref["author"],faname)
            title = ref["title"]
            year = ref["year"]
            if year != pubyear:
                pubyear = year
                stri = '\n{:.year}\n###' + year + '\n'
                print(stri)
                outFile.write(stri)

            string = ('\n{:.paper}\n' +
                      openSpan + title + closeSpan + '{:.papertitle}  \n' +
                      openSpan + authors + closeSpan + '{:.authors}  \n' +
                      openSpan )
            if "school" in ref:
                string = string + ref["school"] + ', '
            if "month" in ref:
                string = string + ref["month"].title() + '. '

            string = string + year + closeSpan + '{:.journal}  \n'

            if "annote" in ref:
                string = (string + openSpan + ref["annote"].replace('\\','') +
                          closeSpan + '{:.comment}  \n'
                         )
            print(string)
            outFile.write(string)

if __name__ == "__main__":
    main(sys.argv[1:])
