#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  2 16:43:52 2023

@author: placais

TODO functions to edit the proper key
TODO easily allow for Corona, Videos
"""
import xml.etree.ElementTree as ET


class spark_xml():
    """A class to handle the .xml files from SPARK3D."""

    def __init__(self, file: str) -> None:
        """
        Constructor.

        Parameters
        ----------
        file : str
            Full path to the .xml file.

        """
        tree = ET.parse(file)
        self.spark = tree.getroot()

        # Add a VideoMultipactorConfig key if needed, or change Multipactor to
        # corona
        self.keys = ["Project", "Model", "Configurations", "EMConfigGroup",
                     "MultipactorConfig"]

    def get_config(self, *args: int) -> ET.Element:
        """
        Return the Config corresponding to the inputs.

        Parameters
        ----------
        *args : int
            Int corresponding to self.keys, in the same order.

        Raises
        ------
        IOError
            *args matched no existing configuration. If it matched several,
            either the .xml is wrong, either this code is wrong!

        Returns
        -------
        ET.Element
            Configuration in the form of an ElementTree Element.

        """
        path = [f"{key}[{val}]" for key, val in zip(self.keys, args)]
        elt = self.spark.findall('/'.join(path))
        if len(elt) != 1:
            raise IOError("More than one or no configuration was found.")
        return elt[0]


if __name__ == "__main__":
    file = "/home/placais/Documents/Simulation/work_spark3d/tesla/Project.xml"
    xml = spark_xml(file)

    # As already defined
    D_CONF = {"project": 1, "model": 1, "confs": 1, "em_conf": 1,
              "discharge_conf": 1, "video": -1}
    # Need only values
    conf = xml.get_config(*D_CONF.values())
    print(conf)
