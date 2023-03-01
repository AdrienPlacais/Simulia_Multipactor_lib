#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 11:29:06 2023

@author: placais
fork from J. Hillairet
"""
import os
from subprocess import PIPE, Popen
# import numpy as np
# import pandas as pd

from helper import printc


class Spark3D():
    """Spark3D simulation object."""
    SPARK_PATH = "/opt/cst/CST_Studio_Suite_2023/SPARK3D"
    BIN_PATH = os.path.join(SPARK_PATH, "./spark3d")

    def __init__(self, project_path: str, file_name: str,
                 output_path: str = None) -> None:
        """Constructor."""
        self.project_path = project_path
        self.file_name = file_name
        self.input = os.path.join(project_path, file_name)

        if output_path is None:
            tmp = os.path.splitext(file_name)[0]
            self.output_path = os.path.join(self.project_path, tmp)

        # The default results file should be the following
        # self.results_file = os.path.join(output_path, 'general_results.txt')

        self.results_path = None
        # created by self._get_results_dir in self.run (path depends on the
        # configuration)

        self._check_paths_exist()

    def _check_paths_exist(self) -> None:
        """Verify if the required folders and files do exist."""
        for path in [self.project_path]:
            assert os.path.exists(path), f"{path} does not exist."
        for file in [self.input]:
            assert os.path.isfile(file), f"{file} does not exist."

    def run(self, configuration: str, d_conf: dict) -> None:
        """Launch the project."""
        cmd = self._get_cmd(configuration, d_conf)

        printc("Spark3D.run info:", f"running SPARK3D with command\n{cmd}")
        try:
            env = os.environ
            with Popen(cmd, shell=True, env=env, stdout=PIPE,
                       stderr=PIPE, universal_newlines=True) as proc:
                for line in proc.stdout:
                    print(line, end='')
            printc("Spark3D.run info:", "run finished with return code",
                   f"{proc.returncode}.")

        except OSError as err:
            printc("Spark3D.run error:", err)

    def _get_cmd(self, configuration: str, d_conf) -> str:
        """Create the command for the project."""
        mode = 'Multipactor'
        cmd = [self.BIN_PATH, f"--input={self.input}"]

        spkx_kwargs = {
            '--output': self.output_path,
        }

        # No argument required, just validate the integrity of the file or list
        # the valid configurations
        if configuration in ('--validate', '--list'):
            cmd.append(configuration)
            return ' '.join(cmd)

        if configuration == '--config':
            my_configuration = self._get_config(mode, **d_conf)
            self.results_path = os.path.join(
                self.output_path, self._get_results_dir(mode, **d_conf))
            cmd.append(f"{configuration}={my_configuration}")

            for key, value in spkx_kwargs.items():
                cmd.append(key + "=" + str(value))
            return ' '.join(cmd)

        return IOError(f'configuration {configuration} was not recognized.')

    def _get_config(self, mode: str, project: int = 1, model: int = 1,
                    confs: int = 1, em_conf: int = 1, discharge_conf: int = 1,
                    video: int = 1) -> str:
        """Get the configuration."""
        out = [f"Project:{project}", f"/Model:{model}",
               f"/Configurations:{confs}", f"/EMConfigGroup:{em_conf}"]

        d_mode = {
            "Multipactor": f"/MultipactorConfig:{discharge_conf}//",
            "Video Multipactor": f"/MultipactorConfig:{discharge_conf}"
                                 + f"/VideoMultipactorConfig:{video}//",
            "Corona": f"/CoronaConfig:{discharge_conf}//",
            "Video Corona": f"/CoronaConfig:{discharge_conf}"
                            + f"/VideoCoronaConfig:{video}//",
        }
        if mode not in d_mode:
            raise IOError('Invalid mode.')
        out.append(d_mode[mode])
        return ''.join(out)

    # TODO: check dirs for Corona and Videos
    def _get_results_dir(self, mode: str, project: int = 1, model: int = 1,
                         confs: int = 1, em_conf: int = 1,
                         discharge_conf: int = 1, video: int = 1) -> str:
        """Get the results directory."""
        out = ["Results", f"@Mod{model}", f"@ConfGr{confs}",
               f"@EMConfGr{em_conf}"]

        d_mode = {"Multipactor": [f"@MuConf{discharge_conf}"],
                  "Video Multipactor": [f"@MuConf{discharge_conf}",
                                        f"@Video{video}"],
                  "Corona": [f"@CoConf{discharge_conf}"],
                  "Video Corona":  [f"@CoConf{discharge_conf}",
                                    f"@Video{video}"],
        }
        out.extend(d_mode[mode])
        path = os.path.join(*out)
        return path

if __name__ == "__main__":
    # Absolute path of the project
    # PROJECT = "/home/placais/Documents/Simulation/work_spark3d/tesla"
    # FILE = 'TESLA_2.spkx'
    PROJECT = "/home/placais/Documents/Simulation/work_spark3d"
    FILE = "coax_filter_correct_name.spkx"
    # WARNING! No spaces, parenthesis are allowed

    # Run the Spark3D Simulation
    spk = Spark3D(PROJECT, FILE)
    # CONFIG = "--list"
    # CONFIG = "--validate"
    CONFIG = "--config"
    D_CONF = {"project": 1, "model": 1, "confs": 1, "em_conf": 1,
              "discharge_conf": 1, "video": -1}

    spk.run(CONFIG, D_CONF)

