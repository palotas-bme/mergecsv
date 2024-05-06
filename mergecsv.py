#!/usr/bin/env python

import glob
import csv
import os
import argparse
from typing import List
import logging
import re
import sys

def merge_csv(csv_path: List, out_file: str, delimiter: str, replacer: dict, include_filenames: bool = False):
    FILENAME_FIELD = "filename"

    csv_files = []
    for path in csv_path:
        if os.path.isfile(path):
            csv_files.append(path)
        else:
            csv_files.extend(glob.glob(os.path.join(path, "*.csv")))
    if len(csv_files) < 1:
        logging.error("No input files found")
        sys.exit(1)
    fieldnames = [FILENAME_FIELD] if include_filenames else []
    dialects = {}
    delimiter_counter = {}
    replace_counter = set()

    for csv_file in csv_files:
        with open(csv_file, "r", encoding="utf-8-sig", newline="") as f:
            header = f.readline()
            dialects[csv_file] = csv.Sniffer().sniff(header)
            delimiter_counter[dialects[csv_file].delimiter] = delimiter_counter.get(dialects[csv_file].delimiter, 0) + 1
            f.seek(0)
            reader = csv.reader(f, dialect=dialects[csv_file])
            header = next(reader)
            logging.info("Reading %s", csv_file)
            for h in header:
                if h in replacer:
                    logging.debug("Replacing header %s with %s", h, replacer[h])
                    replace_counter.add(h)
                    h = replacer[h]
                if h not in fieldnames:
                    fieldnames.append(h)

    with open(out_file, "w", encoding="utf-8-sig", newline="") as f:
        if delimiter is None:
            delimiter = max(delimiter_counter, key=lambda k: delimiter_counter[k])
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)
        writer.writeheader()
        for csv_file in csv_files:
            with open(csv_file, "r", encoding="utf-8-sig", newline="") as f_in:
                reader = csv.DictReader(f_in, dialect=dialects[csv_file])
                for i, f in enumerate(reader.fieldnames):
                    if f in replacer:
                        reader.fieldnames[i] = replacer[f]
                logging.info("Writing %s", csv_file)
                for line in reader:
                    if include_filenames:
                        line[FILENAME_FIELD] = csv_file
                    writer.writerow(line)
    logging.info("Merged %d files to %s, replaced %s headers", len(csv_files), out_file, len(replace_counter))
    if delimiter == "\t":
        delimiter = "TAB"
    logging.debug("Delimiter in the merged file: %s", delimiter)


parser = argparse.ArgumentParser(prog="Merge CSV", description="""
Merge CSV files together.
Input file encoding can be UTF-8 with or without BOM. The output will be bw UTF-8 with BOM.
The headers will be combined. The output will contain all header fields from the input files.
""", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("path", default=["data"], help="Path of the csv files.", nargs="*")
parser.add_argument("-o", "--out", default="mergedfile.csv", help="Name of the merged csv file.")
parser.add_argument("-d", "--delimiter", default=None,
                    help="""Delimiter of the out file. If not given,
                            the delimiter that is most used in the input files is used. (t equals TAB)""")
parser.add_argument("-r", "--replace-header", dest="replace",
                    help="(experimental) Replace header with another. header1=header2 will replace all header1 with header2. Multiple can be added.",
                    default=[], nargs="*")
parser.add_argument("-v", "--verbose", action="store_true", help="Print more things what is happening")
parser.add_argument("-i", "--include-filenames",
                    dest="include_filename", action="store_true", help="Include the input filename in the first column for each row")

args = parser.parse_args()

if args.verbose:
    logging.basicConfig(format="%(message)s", level=logging.DEBUG)
else:
    logging.basicConfig(format="%(message)s", level=logging.INFO)


if args.delimiter == "t":
    args.delimiter = "\t"
if args.delimiter is not None and len(args.delimiter) != 1:
    logging.error("Invalid delimiter: '%s'. Delimiter must be one character", args.delimiter)
    sys.exit(1)

header_replacer = {}
if len(args.replace) > 0:
    replace_test = [re.match("(?!^[^=]+=[^=]+$)", x) for x in args.replace]
    if None not in replace_test:
        logging.error("Invalid replace pattern(s): %s", (", ").join([x.string for x in replace_test if x is not None]))
        sys.exit(1)
    header_replacer = dict([x.split("=") for x in args.replace])

merge_csv(args.path, args.out, args.delimiter, header_replacer, args.include_filename)
