"""Define helper function to load CST data."""

import logging
import os
from pathlib import Path
from pprint import pformat
from typing import Any

import numpy as np


def get_id(folderpath: Path) -> int:
    """Get the ID of the simulation stored in :file:`folderpath`.

    Parameters
    ----------
    folderpath : Path
        A :file:`mmdd-xxxxxxx` folder.

    """
    try:
        id = int(str(folderpath).split("-")[-1])
    except:
        raise ValueError(
            "An error occured when extracting the simulation ID of "
            f"{folderpath = }"
        )
    return id


def mmdd_xxxxxxx_folder_to_dict(
    folderpath: Path, delimiter: str = "\t"
) -> dict[str, Any]:
    """Put all results from a CST :file:`mmdd-xxxxxxx` folder to a dict.

    The expected structure should look like::

        | mmdd-xxxxxxx
        | ├── 'Adimensional e.txt'
        | ├── 'Adimensional h.txt'
        | ├── 'E_acc in MV per m.txt'
        | ├──  Parameters.txt
        | ├── 'ParticleInfo [PIC]'
        | │   ├── 'Emitted Secondaries.txt'
        | │   └── 'Particle vs. Time.txt'
        | ├── 'TD Number of mesh cells.txt'
        | └── 'TD Total solver time.txt'

    Corresponding output will look like:

    .. code-blok:: python

        dic = {
            'Adimensional e': 4.2,
            'Adimensional h': 2.0,
            'E_acc in MV per m': 4.9,
            'Parameters': {'f': 1e9, 'Period': '1 / f'},
            'Emitted Secondaries': np.array([0, 2, 3]),
            'Particle vs. Time': np.array([100, 102, 105]),
            'TD Number of mesh cells': 4.2,
            'TD Total solver time': 4.2,
        }

    .. note::
        We skip hidden files, as well as all files in a folder containing the
        keyword ``"3d"``.

    Parameters
    ----------
    folderpath : Path
        Path to a :file:`mmdd-xxxxxxx` folder, holding the results of a
        single simulation among a parametric simulation export.
    delimiter : str, optional
        Delimiter between two columns. The default is a tab character.

    Returns
    -------
    dic : dict[str, Any]
        Holds the data of the folder. The keys are the name of the files. It
        will look like:

    """
    dic = {}

    for root, _, files in os.walk(folderpath):
        if os.path.split(root)[-1] == "3d":
            logging.info(
                f"Files in {root} were skipped because 3D files are not "
                "supported yet."
            )
            logging.debug(f"List of skipped files:\n{pformat(files)}")
            continue

        for file in files:
            full_path = Path(root, file)
            file = full_path.stem

            if file[0] == ".":
                logging.debug(f"Skipped {file} because is is hidden.")
                continue

            if file == "Parameters":
                dic[file] = _parameters_file_to_dict(full_path)
                continue
            data = np.loadtxt(full_path, delimiter=delimiter)

            if data.shape == ():
                data = float(data)
            dic[file] = data

    return dic


def _parameters_file_to_dict(filepath: Path) -> dict[str, float | str]:
    """Put the :file:`Parameters.txt` content in a dictionary.

    .. todo::
        Detect integer values.

    .. todo::
        Evaluate simple expressions. A parameter defined as '1/2' will be a
        string instead of 0.5 (float)...

    Parameters
    ----------
    filepath : Path
        Path to the file.

    Returns
    -------
    parameters : dict[str, float | str]
        Holds the name of the Parameter as a key, and the corresponding value
        as a value.

    """
    parameters = {}
    with open(filepath) as file:
        for line in file:
            line = line.split("=")
            parameters[line[0]] = line[1].strip()

    for key, val in parameters.items():
        try:
            parameters[key] = float(val)
        except ValueError:
            logging.debug(
                f"Could not convert {val = } from {key = } to float. Don't "
                "worry."
            )
            continue

    return parameters
