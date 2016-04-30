import sys
from bibtextomd.bib import main as bib_main


def main(args=None):
    """The main routine."""
    if args is None:
        args = sys.argv[1:]

    bib_main(args)

if __name__ == "__main__":
    main()
