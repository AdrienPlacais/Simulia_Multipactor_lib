#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  2 16:43:52 2023

@author: placais

TODO easily allow for Corona, Videos
"""
import numpy as np
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
        self.file = file
        self.tree = ET.parse(file)
        self.spark = self.tree.getroot()

        # Add a VideoMultipactorConfig key if needed, or change Multipactor to
        # corona
        self.keys = ["Project", "Model", "Configurations", "EMConfigGroup",
                     "MultipactorConfig"]
        # Used to match the D_CONF keys with the ElemenTree names
        self.convert = {"Project": "project", "Model": "model",
                        "Configurations": "confs", "EMConfigGroup": "em_conf",
                        "MultipactorConfig": "discharge_conf"}

    def get_config(self, **kwargs: int) -> ET.Element:
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
        # Handle the different key names from D_CONF (kwargs) and self.keys
        keys_good_order = [self.convert[key] for key in self.keys]
        args = [kwargs[key] for key in keys_good_order]

        path = [f"{key}[{val}]" for key, val in zip(self.keys, args)]
        elt = self.spark.findall('/'.join(path))
        if len(elt) != 1:
            raise IOError("More than one or no configuration was found.")
        return elt[0]

    def edit(self, conf: ET.Element, save: bool = False, info: bool = True,
             **kwargs: str | float | int) -> None:
        """
        Modify the xml.

        Parameters
        ----------
        conf : ET.Element
            Configuration to be modified.
        save : bool, optional
            To save the updated .xml file (previous file will be overwritten.
            The default is False.
        info : bool, optional
            To output some information on what was changed. The default is
            True.
        **kwargs : str | float | int
            Dict of values to change. Keys must be in <MultipactorConfig>, eg
            'initialNumberElectrons'. To modify inner keys, you must use the
            full path, eg 'sweepPoints' will not work but
            'PowerSweep/sweepPoints' will. You must ensure that the type of the
            values matches what SPARK3D expects.

        """
        if info:
            print(f"\nModifying {conf.find('name').text}...")
        for key, new_value in kwargs.items():
            s_old_value = conf.find(key).text

            s_new_val = str(new_value)
            conf.find(key).text = s_new_val
            if info:
                print(f"Changed {key}: {s_old_value} to {s_new_val}")

        if save:
            self.tree.write(self.file)
            print(f"\nxml saved in {self.file}")


def fmt_array(p_s: np.ndarray) -> str:
    """
    Helper to give Spark3D a list of powers with the proper format.

    Parameters
    ----------
    p_s : np.ndarray
        Array of powers.

    Returns
    -------
    str
        List of floats as understood by SPARK3D.

    """
    s_p_s = str(tuple(p_s))
    return s_p_s.replace(', ', ';')


if __name__ == "__main__":
    file = \
        "/home/placais/Documents/Simulation/work_spark3d/tesla/my_Project.xml"
    xml = spark_xml(file)

    # As already defined
    D_CONF = {"project": 1, "model": 1, "confs": 1, "em_conf": 1,
              "discharge_conf": 1, "video": -1}
    conf = xml.get_config(**D_CONF)

    power = np.linspace(1e-2, 1e2, 10)
    s_power = fmt_array(power)

    D_EDIT = {"initialNumberElectrons": int(2e4),
              "pathRelativePrecision": 0.1,
              "PowerSweep/sweepPoints": s_power,
              }
    # Warning, save=True will overwrite previous .xml.
    xml.edit(conf, save=False, **D_EDIT)
