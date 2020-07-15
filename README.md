---
title: CEST and CPMG processing manual
author: lousapetr
date: July 2020
---

# CEST and CPMG processing

## Prerequisites

Before you start, make sure you have these programs (packages) installed
or activated from modules:

-   `nmrpipe`
-   `sparky-nmrfam`
-   `gnuplot`
-   `octave`

Clone the repository (or download the ZIP archive) from GitHub - click on **Code** and select **Download ZIP** from the drop-down menu.

https://github.com/lousapetr/cest-nmr.git

It contains all the scripts
referenced below and needed for the processing of CEST and CPMG data.
All the scripts are documented below and have comments inside that
should help with understanding of their function.

### Raw data format
The processing assumes the raw data in Bruker format - the main working directory will be the EXPNO directory containing `ser`, `acqu*s` and `v*list` files. Most of the scripts (unless specified otherwise) should be run from within this directory.

## Standard CEST processing

Copy the contents of following folders into your working directory:
-   `common`
-   `cest`

As a shortcut, you can use following, if the scripts are in your `~/bin`:
```
cp -r ~/bin/cest-nmr/common/* ~/bin/cest-nmr/cest/* .
```


### Data processing

First, we process the raw Bruker data into a set of UCSF spectra.

1.  `./xcar3` - fill the asked information about buffer conditions to obtain correct carrier frequencies

2.  `bruker` (preferably use `bruker -nopseudo3D -noscale` to avoid warnings and nonsense values) - use the carriers from previous step and save

3. `./fid.com` - run it, converts the raw `ser` into `nmrpipe` format

    Now you should have a set of preprocessed data in `fid/` folder. Let's continue.

1.  `nmrDraw` - the data in `fid/` should open automatically, find the first row and phase it

2.  open `process_spectra.sh` - open it and put the found phase to the first row into variable `PHASE_x0`, close it and run it

    Now, you have the planes separated into a bunch of spectra located in `FT2\_spectra/*.ft2` (nmrDraw format) and `UCSF/*ucsf` (Sparky format).
    You can check and possibly correct the phasing by opening the first spectrum using `nmrDraw FT2_spectra/1.ft2`. Remember that the phase in this case is just relative to the original one (if you get now phase correction 1.2, add this number to the previous value that you have already in `process_spectra.sh`).
    In the next step, we rename the spectra.

1.  `./rename_cest.sh` - automatically finds correct chemical shifts corresponding to each spectrum, the first spectrum gets shifted by -5 ppm to make it recognizable, the new files are only soft-links to the original spectra

## Calibration of CEST
