# Common Gate to Common Source S-Parameter Converter
Python application to convert common source to common gate s-parameters

## Description
Manufacturers generally only provide common-source s-parameters, but a common-gate configuration is often advantageous for oscillator/LNA designs. 
This program processes large s-parameter files in multiple formats from the manufacturers website and produces a file containing common-gate s-parameters, while accounting for a source-degeneration inductor

## Usage
Download s-parameter file from manufacturer (.s2p, .txt, etc) and upload to the program. Next, enter source-degeneration inductor value (nH) and destination file. Hit "process" button to produce the output file