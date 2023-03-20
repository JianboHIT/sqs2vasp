#!/usr/bin/env python3
# Convert bestsqs.out generated by mcsqs (ATAT) to POSCAR file (POSCAR.sqs) for VASP
#
#     python3 sqs2vasp.py [ sqsfile (default: bestsqs.out) ]
# 
# (POSCAR.sqs will be generated)


import sys
import numpy as np


file_str = sys.argv[1] if len(sys.argv) > 1 else 'bestsqs.out'
file_pos = 'POSCAR.sqs'

with open(file_str, 'r') as f:
    line = f.readline().strip().split()
    coor = [float(x) for x in line]
    if len(coor) == 6:
        a, b, c, af, bt, gm = coor
        af, bt, gm = np.deg2rad([af, bt, gm])
        cy = (np.cos(af)-np.cos(bt)*np.cos(gm))/np.sin(gm)
        vect = [[1, 0, 0],
                [np.cos(gm), np.sin(gm), 0],
                [np.cos(bt), cy, np.sqrt(np.sin(bt)**2 - cy**2)]]
        coor = np.diag([a, b, c]) @ np.array(vect)
    elif len(coor) == 3:
        coor = [coor,]
        for _ in range(2):
            line = f.readline().strip().split()
            coor.append([float(x) for x in line])
        coor = np.array(coor)
    else:
        raise IOError('Unable to open lattice file')

    basic = []
    for _ in range(3):
        line = f.readline().strip().split()
        basic.append([float(x) for x in line])
    basic = np.array(basic) @ coor
    
    xyzs = []
    elmts = []
    labels = []
    for line in f:
        if len(line.strip()) == 0:
            continue
        x, y, z, label = line.strip().split(maxsplit=3)
        xyz = np.array([float(x), float(y), float(z)]) @ coor
        elmt = label.split(sep=',')[0].split(sep='=')[0].strip()
        if elmt in elmts:
            index = elmts.index(elmt)
            xyzs[index].append(xyz)
            labels[index].append(label)
        else:
            elmts.append(elmt)
            xyzs.append([xyz,])
            labels.append([label,])

with open(file_pos, 'w') as f:
    header = 'Generated by sqs2vasp.py'
    f.write(header + '\n')
    f.write('  1.000000\n')
    for ib in basic:
        line = '  {:>22.16f}{:>22.16f}{:>22.16f}\n'.format(*ib)
        f.write(line)
    dsp = '{:>5s}'*len(elmts) + '\n'
    f.write(dsp.format(*elmts))
    dsp = '  ' + '{:>5d}'*len(elmts) + '\n'
    f.write(dsp.format(*[len(x) for x in xyzs]))
    f.write('Cartesian\n')
    dsp = '  {:>22.16f}{:>22.16f}{:>22.16f}    {:s}\n'
    for ixyzs, ilabels in zip(xyzs, labels):
        for ixyz, ilabel in zip(ixyzs, ilabels):
            f.write(dsp.format(*ixyz, ilabel))

