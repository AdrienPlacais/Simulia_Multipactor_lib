"""This library holds several modules to treat data from Simulia softwares.

In particular: CST Particle Studio and SPARK3D. It was designed for multipactor
studies.

"""

import importlib.metadata

from simultipac.util.log_manager import set_up_logging

__version__ = importlib.metadata.version("simultipac")

set_up_logging("Simultipac")
