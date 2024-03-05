# MergeCSV

Ideally if you want to merge CSV files, all files have the same delimiter and headers so you can just skip the first line and insert one file after another. Unfortunately this is not always the case.
Some files could have different delimiter, have an extra column or have column name mismatch.
MergeCSV will merge will merge the files, makes sure all headers are present in the output file and uses one delimiter.
The input files can be ASCII of UTF-8 with or without BOM, the output file will be UTF-8 with BOM.
All headers from the input files will be in the output file.

## Usage

### Basic usage

This  will search for `.csv` files in the `data` directory, and merge them to `mergedfile.csv`.
The delimiter will be the most used delimiter in the input files.

```sh
python mergecsv.py
```

### Advanced usage

This will:

- take all `.txt` files inside `data` and look for `.csv` files inside `data2` directory
- merge the input files to `new_merged_file.csv`
- the delimiter will be `,` independently of the delimiter used in the input files
- replace header1 with Header, and header3 with header4
- log will be more verbose

```sh
python mergecsv.py data/*.txt data2 -o new_merged_file.csv -d , -r header1=Header header3=header4 -v
```

Header replacement is useful if some files have the same data under different names. For example case mismatch mistyping. ex. *file1.csv* => Header1, *file2.csv* => header1

## Issues

- Header replacement can cause problems if both headers are present in the same file
- Header replacement can cause problems if a header is replaced multiple times. ex. `-r header1=header2 header1=header3`

## Examples

### Example 1

*file1.csv*

|Header1|Header2|Header3|
|-------|-------|-------|
|a|b|12|
|q|w|65|

*file2.csv*

|Header1|Header2|Header4|
|-------|-------|-------|
|asdf|34gq|645|
|qwer|sd65fg|456|

`python mergecsv.py file*.csv`

*mergedfile.csv*

|Header1|Header2|Header3|Header4|
|-------|-------|-------|-------|
|a|b|12||
|q|w|65||
|asdf|34gq||645|
|qwer|sd65fg||456|

### Example 2

*file1.csv*

|Header1|Header2|Header3|
|-------|-------|-------|
|a|b|12|
|q|w|65|

*file2.csv*

|Header1|Header2|Header4|
|-------|-------|-------|
|asdf|34gq|645|
|qwer|sd65fg|456|

`python mergecsv.py file*.csv -r Header4=Header3 Header1=NewHeader`

*mergedfile.csv*
|NewHeader|Header2|Header3|
|-------|-------|-------|
|a|b|12|
|q|w|65|
|asdf|34gq|645|
|qwer|sd65fg|456|
