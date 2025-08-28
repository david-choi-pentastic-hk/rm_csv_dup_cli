# CSV DeDup CLI

## Abstract
A CLI program that removes duplicated entries in a CSV file.

## How to Launch
`python3 rm_csv_dup.py`

## Help
See `python3 rm_csv_dup.py --help`

## Remarks
This program is very stupid right now.
It only sees findings with the same prefices and suffices as similar findings.
Also, you can only accept or reject a merge.
You cannot slightly modify the merged contents before placing them into the result table.