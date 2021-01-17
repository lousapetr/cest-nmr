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

1.  `./rename_cest.sh` - automatically finds correct chemical shifts corresponding to each spectrum using `SFO1` from `acqus` and `zCAR` from `fid.com`. The original order of spectra is encoded as last 3 decimal digits of the shift (the first reference spectrum is therefore labeled as `XX.YY001_ppm.ucsf`, where `XX.YY` is the calculated chemical shift.

### Spectra analysis
In this section, we will use the process UCSF spectra, check them in Sparky and output lists of peak intensities.

1. Open `Sparky`, from it open the first spectrum in `UCSF/` using `fo` (the one with smallest last decimals - usually `*001_ppm.ucsf`, sometimes `*000_ppm.ucsf`). Set the contours (using `ct` or `vC` commands).

2. Load the assignment - see section *Assignment loading*

3. Save (`fs`) spectrum and close Sparky (`qt`)

4. `./make_sparky_project.sh` - creates a Sparky project containing all relevant spectra.

5. Run `sparky Sparky/Projects/project.proj`. All spectra, except the first one, are hidden, you can see the list using `PV` command.

6. Run `ha` command from Sparky. This will create one peak list with peak intensities (heights) for each spectrum. The intensities are taken from the coordinates of peaks in the first spectrum - `ha` works like a pin, piercing through the stack of spectra. The lists will be located in `Sparky/Lists/`

7. Save project (`js`) and continue by *Noise estimation* (or close Sparky (`qt`)).

##### Noise estimation

1. Start with the project opened in Sparky.

2. In the *first* spectrum, pick as many peaks as reasonable. To do this:
    1. lower contours to be slightly above Noise
    2. change cursor to *Find/add peaks* (`F8`)
    3. "Box" whole spectrum - lots of peaks will be autopicked

3. Run `hn` command, change settings or leave the defaults.

4. Hit `Determine noise` to create a defined number of random peaks, write their coordinates and intensities to files in `Sparky/Lists_noise`, and calculate the overall noise level for each spectrum based on given method.
    - 'Naive' - Standard deviation of heights in each spectra, no fanciness, original method.
    - 'Iterative' - Iteratively calculate standard deviation and filter out peaks with amplitude larger than 6*sigma (such a height has probability around 1e-9 to exist under Gauss distribution).
    - 'Median abs.dev.' - _Median absolute deviation_, [wiki](https://en.wikipedia.org/wiki/Median_absolute_deviation) Calculate median of absolute values of deviations from median of original data. `MAD = median(abs(x - median(x)))`

5. If you want to see the peak locations, hit `Show peaks`. Warning: After this, the peaks get real, rerun of the noise determination is not possible (new peaks will try to avoid all the previous noise peaks, leaving no space to put them).

6. Close Sparky without saving (you do not want to save the lots of unassigned random peaks).

7. Run `./calculate_noise.sh` - adds (or updates) additional column into peaklists in `Sparky/Lists`. The values for each spectrum correspond to the standard deviation of intensities of the randomly generated peaks.
