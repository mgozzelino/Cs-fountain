# Cs-fountain

A software that analyzes raw Cs-fountain frequency data, corrects for shifts and exports corrected data.   
\
Output data have a custom arbitrary sampling rate.


## Data type
The software assumes data in relative frequency (Inline Equation: $y$) and can handle one interleaved measurement (typically between high and low atom density).
  The file format for the frequency data is:
    *timestamp [MJD] (column 0)
    *y
