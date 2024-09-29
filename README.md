# Wikipedia InfoBox Logos [<img alt="Wikipedia Logo" src="https://www.vectorlogo.zone/logos/wikipedia/wikipedia-icon.svg" height="96" align="right"/>](https://wikipedia.org/)

Extracts SVG logos from Wikipedia [InfoBoxes](https://en.wikipedia.org/wiki/Help:Infobox).

I already extract SVG logos from Wikipedia if they have "logo" in the file name, but that there are valid SVG logos.  This is
a way to get more of them.

## Getting the Data

The Wikipedia data is licensed [CC-BY-SA](https://en.wikipedia.org/wiki/Wikipedia:Database_download).

They provide regular [data dumps](https://meta.wikimedia.org/wiki/Data_dumps) which can be found on [dumps.wikimedia.org](https://dumps.wikimedia.org/enwiki/).  The [latest page](https://dumps.wikimedia.org/enwiki/latest/) has a raw listing but it is best to use the dated page ([example for 20240920](https://dumps.wikimedia.org/enwiki/20240920/)).

https://dumps.wikimedia.org/enwiki/20240920/enwiki-20240920-pages-articles-multistream1.xml-p1p41242.bz2
https://dumps.wikimedia.org/enwiki/20240920/enwiki-20240920-pages-articles1.xml-p1p41242.bz2 270.1 MB

## Parsing the Data

Parsing is non-trivial.


## Running

```
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install
```

## Credits

[![Git](https://www.vectorlogo.zone/logos/git-scm/git-scm-ar21.svg)](https://git-scm.com/ "Version control")
[![Github](https://www.vectorlogo.zone/logos/github/github-ar21.svg)](https://github.com/ "Code hosting")
[![Python](https://www.vectorlogo.zone/logos/python/python-ar21.svg)](https://www.python.org/ "data load script")

* [earwig/mwparserfromhell](https://github.com/earwig/mwparserfromhell)
