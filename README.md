# Cs-fountain

A software that analyzes raw Cs-fountain frequency data, corrects for shifts and exports corrected data.   
\
Output data have a custom arbitrary sampling rate.


## Data type
The software assumes data in relative frequency ($y$) and can handle one interleaved measurement (typically between high and low atom density).

  The file format for the frequency data is:  
  
  - timestamp [MJD] (column 0)
  - $y$ (column 1)
  - Time of flight (TOF) signal, "left" F=4 population (column 4)
  - Time of flight (TOF) signal, "left" F=3 population (column 5)
  - Time of flight (TOF) signal, "right" F=4 population (column 7)
  - Time of flight (TOF) signal, "right" F=3 population (column 8)

Column 2 and 6 are accessory and not used. TOF signals correspond to the 4 clock signals necessary to extract the error signal and are used to infer the atom number at each shot. "left" corresponds to negative frequency modulation, and "right" to positive frequency modulation across the central Ramsey fringe.

Frequency files **must** have "Lock1.txt" (optionally "Lock2.txt" for differential measurements) as suffix and extension.

  The data analysis also assumes a second data file in which the magnetic field is measured on a sensitive transition (in the default case the Majorana transitions $|F=3,m_F=0 \rangle \longrightarrow |F=3, m_F=\pm 1 \rangle$) 

In this case the file format is:  
  - timestamp [MJD] (column 0)
  - transition frequency [Hz]
  - uncertainty [Hz]

  
## Scripts workflow and output
![flow](images/flow.png)
