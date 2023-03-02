#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  2 16:43:52 2023

@author: placais
"""
import xml.etree.ElementTree as ET


def _id(x):
    return f"{x.find('Id').text}, {x.find('name').text}"


def show_configs(file):
    """Show the different configurations in the xml file provided."""
    tree = ET.parse(file)
    root = tree.getroot()
    for proj in root.iter('Project'):
        print(f"1, {proj.tag}")

        for mod in proj.iter('Model'):
            # Select proper Id, print Id and name
            print(f"\t{_id(mod)}")

            for con in mod.iter('Configurations'):
                print(f"\t\t{_id(con)}")

                for em_con in con.iter('EMConfigGroup'):
                    print("\t"*3 + f"{_id(em_con)}")

                    for dis_con in em_con.iter('MultipactorConfig'):
                        print("\t"*4 + f"{_id(dis_con)}")


def get_config(file, D_CONF):
    """Return the Element corresponding to the inputs."""
    return None


if __name__ == "__main__":
    file = "/home/placais/Documents/Simulation/work_spark3d/tesla/Project.xml"
    show_configs(file)
    project = 1
    model = 1
    confs = 1
    em_conf = 1
    discharge_conf = 1
