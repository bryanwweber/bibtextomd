<a name="v0.4.2"></a>
# v0.4.2 (14-MAY-2016)

- Fix printing the same year mulitple times
- Fix "and" in the middle of names
- Remove "me-specific" customization

<a name="v0.4.1"></a>
# v0.4.1 (01-MAY-2016)

- Add Appveyor testing

<a name="v0.4.0"></a>
# v0.4.0 (30-APR-2016)

- Major rewrite to make it a package and update the code.
- Add tests and integrating with Travis

<a name="v0.3.0"></a>
# v0.3.0 (28-JUN-2014)

- Switch to argparse instead of getopt for command line option parsing. Clean up whitespace at end of lines.

<a name="v0.2.6"></a>
# v0.2.6 (26-FEB-2014)

- Fix parsing of latex-style unicode characters `(\'{e})` and names with {}.

<a name="v0.2.5"></a>
# v0.2.5 (14-FEB-2014)

- Fix newlines on Windows - only Unix style `\n` will be written now. Print help if no options are specified on the command line by the user.

<a name="v0.2.4"></a>
# v0.2.4 (02-FEB-2014)

- Add try:except for bibtexparser import to print an error if bibtexparser is not installed. Change string formatting of help string.

<a name="v0.2.3"></a>
# v0.2.3

- Add better error printing. Define help message in one place so it can be reused. Change option lookups to sets instead of what they were before (tuples?).

<a name="v0.2.2"></a>
# v0.2.2

- Add shebang to the script so that it can be run directly from the command line - no more `python3 bib.py -options` needed, just `py bib.py -options` on Windows or `./bib.py -options` on Unix type systems will do!

<a name="v0.2.1"></a>
# v0.2.1 (O4-NOV-2013)

- Fix bug where no opening span tag was printed on the university name line for the thesis.

<a name="v0.2.0"></a>
# v0.2.0 (04-NOV-2013)

- Add option to specify highlighted author name on the command line input, -a.

<a name="v0.1.1"></a>
# v0.1.1 (14-OCT-2013)

- Fix escape character bug in annote field. Add help output
with option -h.

<a name="v0.1.0"></a>
# v0.1.0
- initial release
