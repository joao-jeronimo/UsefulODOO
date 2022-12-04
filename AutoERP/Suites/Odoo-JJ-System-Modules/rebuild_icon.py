#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, argparse, subprocess, wrlgen

resulting_file = wrlgen.VmrlModel([
    wrlgen.Transform(
        translate = (0, 21, 0),
        objects=["""
        Shape {
            appearance Appearance { material Material {diffuseColor 0.5 0.5 0.5} }
            geometry Cylinder {
                radius 10
                height 5
                }
        }
        """]
        ),
    wrlgen.Transform(
        translate = (0, 14, 0),
        objects=["""
        Shape {
            appearance Appearance { material Material {diffuseColor 0.5 0.5 0.5} }
            geometry Cylinder {
                radius 10
                height 5
                }
        }
        """]
        ),
    wrlgen.Transform(
        translate = (0, 7, 0),
        objects=["""
        Shape {
            appearance Appearance { material Material {diffuseColor 0.5 0.5 0.5} }
            geometry Cylinder {
                radius 10
                height 5
                }
        }
        """]
        ),
    wrlgen.Transform(
        translate = (0, 0, 0),
        objects=["""
        Shape {
            appearance Appearance { material Material {diffuseColor 0.5 0.5 0.5} }
            geometry Cylinder {
                radius 10
                height 5
                }
        }
        """]
        ),
    ])

with open("icon-in.wrl", "w") as output_file_descr:
    output_file_descr.write(resulting_file)

subprocess.run([
    'view3dscene', 'icon-in.wrl',
    '--screenshot', '0', 'icon-out.png',
    ])
