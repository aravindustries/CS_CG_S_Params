"""
=======================================================
PROGRAM:        PmT_CS_CG_Sparams.py
AUTHOR:         Arav Sharma
DATE:           2024-09-20
DESCRIPTION:    Manufacturers generally only provide common-source 
                s-parameters, but a common-gate configuration is 
                often advantageous for oscillator/LNA designs. This 
                program processes large s-parameter files in multiple 
                formats from the manufacturers website and produces
                a file containing common-gate s-parameters, while
                accounting for a source-degeneration inductor

USAGE:          Download s-parameter file from manufacturer (.s2p, 
                .txt, etc) and upload to the program. Next, enter
                source-degeneration inductor value (nH) and 
                destination file. Hit "process" button to 
                produce the output file

VERSION:        v2.0
LICENSE:        MIT
=======================================================
"""
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox

# Function to remove header from data for parsing
def parseSparamFile(filename, col):
    data = []
    with open(filename, 'r') as f:
            for line in f:
                # Skip lines starting with '!' or lines without numeric data
                if line.startswith('!') or line.startswith('#'):
                    continue
                 # Try parsing the line; skip if it's not numeric
                try:
                     parsed_line = list(map(float, line.split()))
                     if len(parsed_line) == col:
                         data.append(parsed_line)
                except ValueError:
                     # Skip lines that can't be converted to floats
                     continue
    return data

# Main loop to convert s-parameters using element-wise matrix operations
def calcCommGateParam(Z0, M, L, col, data):
     s = np.zeros((len(data), col))
     len_data = len(data)
     for i in range(len_data):
         s11s = data[i, 1] * np.exp(1j * data[i, 2] * np.pi / 180)
         s21s = data[i, 3] * np.exp(1j * data[i, 4] * np.pi / 180)
         s12s = data[i, 5] * np.exp(1j * data[i, 6] * np.pi / 180)
         s22s = data[i, 7] * np.exp(1j * data[i, 8] * np.pi / 180)

         del6 = (1 + s11s) * (1 + s22s) - s12s * s21s
         y11s = ((1 - s11s) * (1 + s22s) + s12s * s21s) / del6
         y12s = -2 * s12s / del6
         y21s = -2 * s21s / del6
         y22s = ((1 + s11s) * (1 - s22s) + s12s * s21s) / del6

         y11g = y11s + y12s + y21s + y22s
         y12g = -(y12s + y22s)
         y21g = -(y21s + y22s)
         y22g = y22s

         del2 = (1 + y11g) * (1 + y22g) - y12g * y21g
         s11 = ((1 - y11g) * (1 + y22g) + y12g * y21g) / del2
         s12 = -2 * y12g / del2
         s21 = -2 * y21g / del2
         s22 = ((1 + y11g) * (1 - y22g) + y12g * y21g) / del2

         del5 = (1 - s11) * (1 - s22) - s12 * s21
         Z11 = Z0 * ((1 + s11) * (1 - s22) + s12 * s21) / del5
         Z12 = Z0 * (2 * s12) / del5
         Z21 = Z0 * (2 * s21) / del5
         Z22 = Z0 * ((1 + s22) * (1 - s11) + s12 * s21) / del5

         Zind = 1j * 2 * np.pi * data[i, 0] * M * L
         Z11o = Z11 + Zind
         Z12o = Z12 + Zind
         Z21o = Z21 + Zind
         Z22o = Z22 + Zind

         z11o = Z11o / Z0
         z12o = Z12o / Z0
         z21o = Z21o / Z0
         z22o = Z22o / Z0

         del4 = (z11o + 1) * (z22o + 1) - z12o * z21o
         s11i = ((z11o - 1) * (z22o + 1) - z12o * z21o) / del4
         s12i = 2 * z12o / del4
         s21i = 2 * z21o / del4
         s22i = ((z11o + 1) * (z22o - 1) - z12o * z21o) / del4

         s[i, 0] = data[i, 0]
         s[i, 1] = np.abs(s11i)
         s[i, 2] = np.angle(s11i, deg=True)
         s[i, 3] = np.abs(s21i)
         s[i, 4] = np.angle(s21i, deg=True)
         s[i, 5] = np.abs(s12i)
         s[i, 6] = np.angle(s12i, deg=True)
         s[i, 7] = np.abs(s22i)
         s[i, 8] = np.angle(s22i, deg=True)
     return s

# Call functions to parse input file and produce CG s-parameters
def process_file(input_file, inductance, output_file):
    try:
        Z0 = 50
        col = 9
        M = 1e6
        L = inductance * 1e-9
        
        spdat = np.array(parseSparamFile(input_file, col))

        s = calcCommGateParam(Z0, M, L, col, spdat)

        np.savetxt(output_file, s, fmt='%g')
        messagebox.showinfo("Success", f"File processed and saved as '{output_file}'")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Creates "Browse" functionality for input file
def select_file():
    file_path = filedialog.askopenfilename(title="Select Input File", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)

# Handle the "Process" button click
def process_button_click():
    input_file = file_entry.get()
    inductance = inductance_entry.get()
    output_file = output_entry.get()
    
    if not input_file:
        messagebox.showerror("Error", "Please select an input file.")
        return
    
    if not output_file:
        messagebox.showerror("Error", "Please enter an output file name.")
        return
    
    try:
        inductance_value = float(inductance)
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid inductance value.")
        return
    
    process_file(input_file, inductance_value, output_file)

# Generates main window
root = tk.Tk()
root.title("Common Source to Common Gate Converter")

# File selection
file_label = tk.Label(root, text="Input File:")
file_label.grid(row=0, column=0, padx=10, pady=10)

file_entry = tk.Entry(root, width=40)
file_entry.grid(row=0, column=1, padx=10, pady=10)

file_button = tk.Button(root, text="Browse", command=select_file)
file_button.grid(row=0, column=2, padx=10, pady=10)

# Inductance entry
inductance_label = tk.Label(root, text="Inductance (nH):")
inductance_label.grid(row=1, column=0, padx=10, pady=10)

inductance_entry = tk.Entry(root)
inductance_entry.grid(row=1, column=1, padx=10, pady=10)

# Output file name entry
output_label = tk.Label(root, text="Output File Name:")
output_label.grid(row=2, column=0, padx=10, pady=10)

output_entry = tk.Entry(root)
output_entry.grid(row=2, column=1, padx=10, pady=10)

# Process button
process_button = tk.Button(root, text="Process", command=process_button_click)
process_button.grid(row=3, column=1, padx=10, pady=20)

root.mainloop()
