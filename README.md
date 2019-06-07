# TIS Document Ripper

This script allows you to rip electrical wiring diagrams, collision/body repair manuals, and repair manuals from
Toyota's TIS.

## Setup

This script requires that you download ChromeDriver from http://chromedriver.chromium.org/downloads and place the
executable in this directory. You will also need to initialize a new Chrome user profile at ./user-data and configure
some settings manually:

```
chrome --user-data-dir=./user-data
```

You should set the Download directory to ./download, and disable the built-in PDF viewer.

You will also need to install the pip dependencies:

```
pip install -r requirements.txt
```

## Usage

```
./rip.py EM12345 RM12345 BM12345 BM98765 RM01935 EM37590
```

All manuals will be downloaded to their own directories.

## Finding document IDs

The easiest way to find the document IDs is to search for your vehicle in TIS and look at the URLs for the documents.
EWDs start with "EM", body repair manuals start with "BM", and repair manuals start with "RM".

## Output

RM and BM will both have indexes generated for them, and PDFs will be generated for HTML pages. All images are embedded
in the pages so there are no external dependencies for a single page. All inter-page links are corrected so that they
continue to work in the HTML versions of the pages, but be aware that links in PDFs can behave inconsistently at times.

Electrical diagrams are downloaded for the `system`, `overall`, and `routing` categories, as they are the most useful
(and they come in convenient PDF form).