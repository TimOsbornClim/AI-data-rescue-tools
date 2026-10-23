# Table structure tools

Many AI data rescue approaches encode a particular table structure using a JSON file. For example, to tell AI what table to expect in the image, or to tell AI how to return the rescued data values in a particular table layout.

But JSON files of table structures are not easy to read by humans nor are they easy to create.

## show-table-structure.py

This creates .paths.txt and .tree.txt text displays of the table structure described by JSON files.

Currently it is set up to process any `results_<img-name>.json file in the current directory, and
produces the two output files for each other.  Here are samples are both:

results_CORFU_1853_01.paths.txt
```text
001 [depth=1] table_1 / Moon's Age.
002 [depth=1] table_1 / Day of the Week.
003 [depth=1] table_1 / Day of the Month.
004 [depth=3] table_1 / Observations taken at 9.30 A.M. (Local Time). / Barometer. / Barometer. No. Reading.
005 [depth=3] table_1 / Observations taken at 9.30 A.M. (Local Time). / Barometer. / Thermo-meter.
006 [depth=3] table_1 / Observations taken at 9.30 A.M. (Local Time). / Barometer. / Reading corrected for Index error and Capillary ac-tion, and reduced to temperature of 32°.
007 [depth=4] table_1 / Observations taken at 9.30 A.M. (Local Time). / Hygrometer. / Dry Bulb No. 4 / Correct-ed read-ing for Index error.
008 [depth=4] table_1 / Observations taken at 9.30 A.M. (Local Time). / Hygrometer. / Wet Bulb No. 5 / Correct-ed read-ing for Index error.
009 [depth=3] table_1 / Observations taken at 9.30 A.M. (Local Time). / Hygrometer. / Dew-point computed.
010 [depth=3] table_1 / Observations taken at 9.30 A.M. (Local Time). / Hygrometer. / Humi-dity 0-1.
011 [depth=3] table_1 / Observations taken at 9.30 A.M. (Local Time). / Wind. / Direction.
012 [depth=3] table_1 / Observations taken at 9.30 A.M. (Local Time). / Wind. / Force in lbs per square foot.
013 [depth=3] table_1 / Observations taken at 9.30 A.M. (Local Time). / Cloud. / 0-10.
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
```
