#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, argparse, subprocess, wrlgen

the_cylinder = wrlgen.Concretize(
    color=[0.5, 0.5, 0.5],
    shape=wrlgen.RawCylinder(10, 5),
    )

resulting_file = wrlgen.VmrlModel([
    wrlgen.Transform(
        translate = (0, 21, 0),
        objects=[
            the_cylinder,
            ]
        ),
    wrlgen.Transform(
        translate = (0, 14, 0),
        objects=[
            the_cylinder,
            ]
        ),
    wrlgen.Transform(
        translate = (0, 7, 0),
        objects=[
            the_cylinder,
            ]
        ),
    wrlgen.Transform(
        translate = (0, 0, 0),
        objects=[
            the_cylinder,
            ]
        ),
    ])

with open("icon-in.wrl", "w") as output_file_descr:
    output_file_descr.write(resulting_file)

subprocess.run([
    'view3dscene', 'icon-in.wrl',
    '--screenshot', '0', 'icon-out.png',
    ])
