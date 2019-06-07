#!/usr/bin/env python3
from selenium import webdriver
import time
import os.path
import xml.etree.ElementTree as ET
import shutil
import subprocess
from bs4 import BeautifulSoup
import os
import sys


def mkfilename(s):
    fn = ""
    for x in s:
        if x.isalnum() or x == " ":
            fn += x
        else:
            fn += "_"
    return fn

def fix_links(fn):
    modified = False
    doc = open(fn, 'r').read()
    soup = BeautifulSoup(doc, 'lxml')
    for link in soup.find_all("a"):
        href = link.get('href')
        if href is None:
            continue
        
        if '?' in href:
            href = href.split('?')[0]
        
        if not href.startswith('/t3Portal/document'):
            continue
        
        new_path = os.path.basename(href)
        if href != new_path:
            link['href'] = new_path
            modified = True
    
    if modified:
        print("Writing ", fn)
        with open(fn, 'w') as fh:
            fh.write(soup.prettify())

def download_ewd(driver, ewd):
    SYSTEMS = ["system", "routing", "overall"]

    for s in SYSTEMS:
        fn = os.path.join(ewd, s, "index.xml")
        d = os.path.join(ewd, s)
        if not os.path.exists(d):
            os.makedirs(d)

        if os.path.exists(fn):
            continue

        url = "https://techinfo.toyota.com/t3Portal/external/en/ewdappu/" + ewd + "/ewd/contents/" + s + "/title.xml"
        print("Loading", url)
        driver.get(url)
        print("Saving...")
        xml_src = driver.execute_script('return document.getElementById("webkit-xml-viewer-source-xml").innerHTML')
        with open(fn, 'w') as fh:
            fh.write(xml_src)

    for s in SYSTEMS:
        idx = os.path.join(ewd, s, "index.xml")
        print(idx)
        tree = ET.parse(idx)
        root = tree.getroot()
        for child in root:
            name = child.findall('name')[0].text
            fig = child.findall('fig')[0].text
            fn = os.path.join(ewd, s, mkfilename(fig + " " + name) + ".pdf")

            if os.path.exists(fn):
                continue

            print("Downloading ", name, "...")
            url = "https://techinfo.toyota.com/t3Portal/external/en/ewdappu/" + ewd + "/ewd/contents/" + s + "/pdf/" + fig + ".pdf"
            driver.get(url)
            # this will have downloaded the file, or not
            temp_dl_path = os.path.join("download", fig + ".pdf.crdownload")
            while os.path.exists(temp_dl_path):
                time.sleep(0.2)
            dl_path = os.path.join("download", fig + ".pdf")
            if not os.path.exists(dl_path):
                time.sleep(1)
            if not os.path.exists(dl_path):
                print("Didn't download ", url, "!")
                continue
            shutil.move(dl_path, fn)
            print("Done ", name)

def toc_parse_items(base, items):
    if len(items) == 0:
        return ""
    
    wrap = "<ul>"

    for i in items:
        wrap += "<li>"
        name = i.findall("name")[0].text
        wrap += name

        if "href" in i.attrib and i.attrib["href"] != "":
            # it has a link, parse it
            bn = os.path.splitext(os.path.basename(i.attrib["href"]))[0]
            html_path = os.path.join(base, "html", bn + ".html")
            pdf_path = os.path.join(base, "pdf", bn + ".pdf")

            if os.path.exists(html_path):
                wrap += " [<a href=\"html/" + bn + ".html\">HTML</a>] "
            if os.path.exists(pdf_path):
                wrap += " [<a href=\"pdf/" + bn + ".pdf\">PDF</a>] "

        wrap += toc_parse_items(base, i.findall("item"))
        wrap += "</li>"

    wrap += "</ul>"
    return wrap

def build_toc_index(base):
    if not os.path.exists(base):
        return False
    toc_path = os.path.join(base, "toc.xml")
    if not os.path.exists(toc_path):
        print("toc.xml missing in ", base)
        return False

    print("Building TOC index from ", toc_path, "...")
    
    tree = ET.parse(toc_path)
    root = tree.getroot()

    body = toc_parse_items(base, root.findall("item"))
    index_out = os.path.join(base, "index.html")
    with open(index_out, "w") as fh:
        fh.write("<!doctype html>\n")
        fh.write("<html><head><title>" + base + "</title></head><body>")
        fh.write(body)
        fh.write("</body></html>")

def download_manual(driver, t, id):
    if not os.path.exists(os.path.join(id, "html")):
        os.makedirs(os.path.join(id, "html"))
    if not os.path.exists(os.path.join(id, "pdf")):
        os.makedirs(os.path.join(id, "pdf"))
    toc_path = os.path.join(id, "toc.xml")
    if not os.path.exists(toc_path):
        print("Downloading the TOC for", id)
        url = "https://techinfo.toyota.com/t3Portal/external/en/" + t + "/" + id + "/toc.xml"
        driver.get(url)
        xml_src = driver.execute_script('return document.getElementById("webkit-xml-viewer-source-xml").innerHTML')
        with open(toc_path, 'w') as fh:
            fh.write(xml_src)

    tree = ET.parse(toc_path)
    root = tree.getroot()
    n = 0
    c = 0

    for i in root.iter("item"):
        if not 'href' in i.attrib or i.attrib['href'] == '':
            continue
        c += 1

    for i in root.iter("item"):
        if not 'href' in i.attrib or i.attrib['href'] == '':
            continue
        href = i.attrib['href']
        url = "https://techinfo.toyota.com" + href
        n += 1
        
        print("Downloading", href, " (", n, "/", c, ")...")
        # all are html files, load them all up one at a time and then save them
        f_parts = href.split('/')
        f_p = os.path.join(id, "html", f_parts[len(f_parts)-1])
        pdf_p = os.path.join(id, "pdf", f_parts[len(f_parts)-1][:-5] + ".pdf")

        if os.path.exists(f_p) and not os.path.exists(pdf_p):
            # make the pdf
            make_pdf(f_p, pdf_p)

        if os.path.exists(f_p) or os.path.exists(pdf_p):
            continue
        driver.get(url)

        if "location='/t3Portal" in driver.page_source:
            print("\tPDF redirect found!")
            
            while True:
                time.sleep(0.2)
                incomplete = False
                for f in os.listdir("download"):
                    if f.endswith(".crdownload"):
                        incomplete = True
                        break
                if not incomplete:
                    break
                else:
                    print("Waiting for incomplete download!")
                    time.sleep(0.2)

            # list out all downloads in folder and try to match them!
            dest_file = None
            while len(os.listdir("download")) < 1:
                time.sleep(0.2)

            for f in os.listdir("download"):
                print(f)
                if f in driver.page_source:
                    dest_file = f
                    break
            
            if dest_file is None:
                print("\tCould not find matching download!")
                input("wait")
                continue
            
            shutil.move(os.path.join("download", dest_file), pdf_p)
            print("\tDone")
        else:
            print("\tInjecting scripts...")
            # we want to inject jQuery now
            driver.execute_script("""var s=window.document.createElement('script');\
            s.src='https://cdnjs.cloudflare.com/ajax/libs/jquery/3.4.1/jquery.min.js';\
            window.document.head.appendChild(s);""")

            # remove the toyota footer
            src = None
            try :
                src = driver.execute_script(open("injected.js", "r").read())
            except:
                time.sleep(1)
                src = driver.execute_script(open("injected.js", "r").read())

            with open(f_p, 'w') as fh:
                fh.write(src)

            fix_links(f_p)

            print("\tDone")
    
    build_toc_index(id)

def make_pdf(src, dest):
    print("Creating PDF from", src, "to", dest)
    subprocess.run(["/usr/bin/chromium", "--print-to-pdf=" + dest, "--no-gpu", "--headless", "file://" + os.path.abspath(src)])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("You must pass the documents you wish to download as arguments to this script!")
        sys.exit(1)
    
    EWDS = []
    REPAIR_MANUALS = []
    COLLISION_MANUALS = []

    for arg in sys.argv[1:]:
        if arg.startswith('EM'):
            EWDS.append(arg)
        elif arg.startswith('RM'):
            REPAIR_MANUALS.append(arg)
        elif arg.startswith('BM'):
            COLLISION_MANUALS.append(arg)
        else:
            print("Unknown document type for '" + arg + "'!")
            sys.exit(1)
    
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("user-data-dir=./user-data")

    shutil.rmtree("download", True)
    os.makedirs("download")

    driver = webdriver.Chrome("./chromedriver", options=chrome_options)

    driver.get("https://techinfo.toyota.com")
    input("Please login and press enter to continue...")

    # for each in ewd download
    print("Downloading electrical wiring diagrams...")
    for ewd in EWDS:
        download_ewd(driver, ewd)

    # download all collision manuals
    print("Downloading collision repair manuals...")
    for cr in COLLISION_MANUALS:
        download_manual(driver, "cr", cr)

    # download all repair manuals
    print("Downloading repair manuals...")
    for rm in REPAIR_MANUALS:
        download_manual(driver, "rm", rm)

    driver.close()
