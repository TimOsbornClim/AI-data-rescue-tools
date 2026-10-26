# Table structure tools

Many AI data rescue approaches encode a particular table structure using a JSON file. For example, to tell AI what table to expect in the image, or to tell AI how to return the rescued data values in a particular table layout.

But JSON files of table structures are not easy to read by humans nor are they easy to create.

## Suggested workflow using the tools below

1. Give an image of a data table to AI and ask it to identify the table structure (or more than one
if the image contains multiple tables) and return it in a JSON file.

2. This can be repeated to obtain AI-generated JSON table structures (schema) for a selection of images to test if they have similar layouts.

3. Use show-table-structure.py to convert the JSON files into viewable .paths and .tree files.

4. View these files to check if they match the actual table structure.

5. If they do not match perfectly, then edit the .paths file so it is correct,

6. Use mk-table-schema.py to create a JSON schema from the edited .paths file. This will warn about any neighbouring column headings that are slightly different, in case they are supposed to be the same but a typo has been introduced in one of them.

7. This curated JSON schema can be used for multiple images that use the same table structure. 



## show-table-structure.py

This creates .paths.txt and .tree.txt text displays of the table structure described by JSON files.

Currently it is set up to process any `results_<img-name>.json file in the current directory, and
produces the two output files for each other.

The .paths files use " || " as the field separator (note the spaces around them) as this is unlikely to appear in a genuine column heading (whereas other options such as a "/" or ">" might do).

Here are samples are both:

results_CORFU_1853_01.paths.txt
```text
001 [depth=1] table_1 || Moon's Age.
002 [depth=1] table_1 || Day of the Week.
003 [depth=1] table_1 || Day of the Month.
004 [depth=3] table_1 || Observations taken at 9.30 A.M. (Local Time). || Barometer. || Barometer. No. Reading.
005 [depth=3] table_1 || Observations taken at 9.30 A.M. (Local Time). || Barometer. || Thermo-meter.
006 [depth=3] table_1 || Observations taken at 9.30 A.M. (Local Time). || Barometer. || Reading corrected for Index error and Capillary ac-tion, and reduced to temperature of 32°.
007 [depth=4] table_1 || Observations taken at 9.30 A.M. (Local Time). || Hygrometer. || Dry Bulb No. 4 || Correct-ed read-ing for Index error.
008 [depth=4] table_1 || Observations taken at 9.30 A.M. (Local Time). || Hygrometer. || Wet Bulb No. 5 || Correct-ed read-ing for Index error.
009 [depth=3] table_1 || Observations taken at 9.30 A.M. (Local Time). || Hygrometer. || Dew-point computed.
010 [depth=3] table_1 || Observations taken at 9.30 A.M. (Local Time). || Hygrometer. || Humi-dity 0-1.
011 [depth=3] table_1 || Observations taken at 9.30 A.M. (Local Time). || Wind. || Direction.
012 [depth=3] table_1 || Observations taken at 9.30 A.M. (Local Time). || Wind. || Force in lbs per square foot.
013 [depth=3] table_1 || Observations taken at 9.30 A.M. (Local Time). || Cloud. || 0-10.
014 [depth=4] table_1 || Observations taken at 9.30 A.M. (Local Time). || Self-Registering Thermometers. || Dry. || Max. in Sun's rays. No. 1
015 [depth=4] table_1 || Observations taken at 9.30 A.M. (Local Time). || Self-Registering Thermometers. || Dry. || Min. on Grass. No. 2
```

results_CORFU_1853_01.tree.txt
```text
table_1
├── Moon's Age. [001]
├── Day of the Week. [002]
├── Day of the Month. [003]
├── Observations taken at 9.30 A.M. (Local Time).
│   ├── Barometer.
│   │   ├── Barometer. No. Reading. [004]
│   │   ├── Thermo-meter. [005]
│   │   └── Reading corrected for Index error and Capillary ac-tion, and reduced to temperature of 32°. [006]
│   ├── Hygrometer.
│   │   ├── Dry Bulb No. 4
│   │   │   └── Correct-ed read-ing for Index error. [007]
│   │   ├── Wet Bulb No. 5
│   │   │   └── Correct-ed read-ing for Index error. [008]
│   │   ├── Dew-point computed. [009]
│   │   └── Humi-dity 0-1. [010]
│   ├── Wind.
│   │   ├── Direction. [011]
│   │   └── Force in lbs per square foot. [012]
│   └── Cloud.
│       └── 0-10. [013]
├── Observations taken at 9.30 A.M. (Local Time).
│   ├── Self-Registering Thermometers.
│   │   ├── Dry.
│   │   │   ├── Max. in Sun's rays. No. 1 [014]
│   │   │   ├── Min. on Grass. No. 2 [015]
```



## mk-table-schema.py

This creates a JSON table structure schema file from a .paths.txt file.

The .paths files require " || " as the field separator (note the spaces around them), as produced by `show-table-structure.py`. When editing these files, ensure the same field separator (including spaces) is used.

The code warns if the indicated "depth" doesn't match the number of branches e.g. if the .paths.txt file contains this line:

`024 [depth=4] table_1 || Observations taken at 9.30 A.M. (Local Time). || Rain in previous 24 hours. || On Ground.`

then the following warning will be given (because the "table_1" is an indicator for which table, not a column hierarchy within the table which has only a depth=3 for this example):

```text
RROR: Depth mismatch
Line 24
Recorded depth = 4
Actual depth   = 3
Column number  = 24
Path           = table_1 || Observations taken at 9.30 A.M. (Local Time). || Rain in previous 24 hours. || On Ground.
```


The code also warns about any neighbouring column headings that are slightly different, in case they are supposed to be the same but a typo has been introduced in one of them. If they are different, they will be put in different branches of the tree so it is important that inadvertent typos don't cause that to happen. For example:

```text
Created: table_CORFU_185209-185508.paths.json

Possible near-duplicate headings:

--------------------------------
Parent location:
    table_1

    'Observations taken at 9.30 A.M. (Local Time).'
    'Observations taken at 3.30 P.M. (Local Time).'

Similarity: 0.956
```


The code also lists a warning if any complete paths (i.e. all the branch and leaf headings) are identical, whether they are in adjacent lines or not. This is not necessarily wrong, but the warning is useful because it means that the position of the columns within the table is necessary to provide the context needed to distinguish identically labelled columns.


Currently the file to process is hard-coded in these lines:

```python
process_file(
    Path("results_CORFU_1852_09.paths.txt")
)
```


