# TIS Document Ripper

This script allows you to rip electrical wiring diagrams, collision/body repair manuals, and repair manuals from
Toyota's TIS.

### CZ notes: June 2022

Install dependencies (bs4, selenium) in conda environment. Activate (e.g., `conda activate scrape`)

1\. Check Google Chrome for version, then given version download matching ChromeDriver from http://chromedriver.chromium.org/downloads (e.g., chromedriver_mac64.zip) and unzip the binary into this directory.

2\. Generate user profile in this directory on MacOS by running:

```
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --user-data-dir=./user-data
```

Verify that you now have a folder `./user-data`

3\. Do initial "rip." `./rip.py RM30B0U` --> this will open TIS in Chrome and prompt a login. After this, return to Terminal and press enter.

4\. The initial rip creates and HTML ToC. After the initial rip is completed, run the code again `./rip.py RM30B0U` and it will find the HTML files and instead generate PDFs for all files and add to the ToC as well.

NOTE: Some older vehicles (e.g., 2008 Corolla) have body repair manuals that start with BRM and do not use the same document ID as the RM or EM.

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