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
    BIN_PATH = "/opt/cst/CST_Studio_Suite_2023/SPARK3D/./spark3d"

    def __init__(self, project_path: str, file_name: str,
                 output_path: str = None) -> None:
        """Constructor."""
        self.project_path = project_path
        self.file_name = file_name

        self.input = os.path.join(project_path, file_name)
        assert os.path.isfile(self.input)
        if output_path is None:
            self.output_path = os.path.join(project_path, 'results')

    def run(self, configuration: str) -> None:
        """Launch the project."""
        cmd = self._get_cmd(configuration)

        printc("Spark3D.run info:", f"running SPARK3D with command {cmd}")
        try:
            with Popen(cmd, shell=True, env=os.environ, stdout=PIPE,
                       stderr=PIPE, universal_newlines=True) as proc:
                for line in proc.stdout:
                    print(line, end='')
            printc("Spark3D.run info:", "run finished with return code",
                   f"{proc.returncode}.")

        except OSError as e:
            printc("Spark3D.run error:", e)

    def _get_cmd(self, configuration: str) -> str:
        """Create the command for the project."""
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
            cmd.append(f"{configuration}={self._get_config()}")

            for key, value in spkx_kwargs.items():
                cmd.append(key + "=" + str(value))
            return ' '.join(cmd)

        return IOError(f'configuration {configuration} was not recognized.')

    def _get_config(self) -> str:
        """Get the configuration."""
        # TODO make these real arguments
        mode = 'Multipactor'
        project, model, config, em_config, discharge_config = 1, 1, 1, 1, 4
        args = (discharge_config, )

        d_mode = {
            "Multipactor":
                lambda *args: f"/MultipactorConfig:{args[0]}//",
            "Video Multipactor":
                lambda *args: f"/MultipactorConfig:{args[0]}"
                              + f"/VideoMultipactorConfig:{args[1]}//",
            "Corona":
                lambda *args: f"/CoronaConfig:{args[0]}//",
            "Video Corona":
                lambda *args: f"/CoronaConfig:{args[0]}"
                              + f"/VideoCoronaConfig:{args[1]}//",
        }
        if mode not in d_mode:
            raise IOError('Invalid mode.')

        out = [f"Project:{project}",
               f"/Model:{model}",
               f"/Configurations:{config}",
               f"/EMConfigGroup:{em_config}"]
        out.append(d_mode[mode](*args))
        return ''.join(out)

if __name__ == "__main__":
    # Absolute path of the project
    PROJECT = "/home/placais/Documents/Simulation/work_spark3d/tesla"
    FILE = 'TESLA_2.spkx'

    # Run the Spark3D Simulation
    spk = Spark3D(PROJECT, FILE)
    # CONFIG = "--list"
    # CONFIG = "--validate"
    CONFIG = "--config"
    spk.run(CONFIG)

