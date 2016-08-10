from builtins import object
import setup_paths
from nomadcore.simple_parser import mainFunction, CachingLevel
from nomadcore.simple_parser import SimpleMatcher as SM
from nomadcore.local_meta_info import loadJsonFile, InfoKindEl
import os, sys, json

class Wien2kIn1cContext(object):
    """context for wien2k struct parser"""

    def __init__(self):
        self.parser = None

    def initialize_values(self):
        """allows to reset values if the same superContext is used to parse different files"""
        pass

    def startedParsing(self, path, parser):
        """called when parsing starts"""
        self.parser = parser
        # allows to reset values if the same superContext is used to parse different files
        self.initialize_values()


# description of the input
def buildIn1cMatchers():
    return SM(
    name = 'root',
    weak = True,
    startReStr = "",
        sections = ["section_run", "section_method"],
    subMatchers = [
#        SM(name = 'systemName',
#          startReStr = r"(?P<x_wien2k_system_nameIn>.*)"),
        SM(r"\s*(?P<x_wien2k_wf_switch>[\w*]+)\s*EF=[-+.0-9]*\s*\W*WFFIL, WFPRI, ENFIL, SUPWF\W"),
        SM(r"\s*(?P<x_wien2k_rkmax>[0-9.]+)\s*[0-9]+\s*[0-9]+\s*\WR-..\WK-...; MAX \w*.*")
#        SM(r"(?P<x_wien2k_calc_mode>.*)"),
#        SM(r"\s*(?P<x_wien2k_unit_cell_param_a>[-+0-9]*\.\d{0,6}){0,10}\s*(?P<x_wien2k_unit_cell_param_b>[-+0-9]*\.\d{0,6}){0,10}\s*(?P<x_wien2k_unit_cell_param_c>[-+0-9]*\.\d{0,6}){0,10}\s*(?P<x_wien2k_angle_between_unit_axis_alfa>[-+]?[0-9]*\.\d{0,6}){0,10}\s*(?P<x_wien2k_angle_between_unit_axis_beta>[-+]?[0-9]*\.\d{0,6}){0,10}\s*(?P<x_wien2k_angle_between_unit_axis_gamma>[-+]?[0-9]*\.\d*)"),
#        SM(r"\s*ATOM\s*[-0-9]+:\s*X=(?P<x_wien2k_atom_pos_x>[-+0-9.eEdD]+)\s*Y=(?P<x_wien2k_atom_pos_y>[-+0-9.eEdD]+)\s*Z=(?P<x_wien2k_atom_pos_z>[-+0-9.eEdD]+)",
#           repeats=True,
#           sections=["x_wien2k_section_equiv_atoms"],
#           subMatchers=[
#               SM(r"\s*[-0-9]+:\s*X=(?P<x_wien2k_atom_pos_x>[-+0-9.eEdD]+)\s*Y=(?P<x_wien2k_atom_pos_y>[-+0-9.eEdD]+)\s*Z=(?P<x_wien2k_atom_pos_z>[-+0-9.eEdD]+)",
#                  repeats=True
#              ),
#               SM(r"\s*(?P<x_wien2k_atom_name>^.+)\s*NPT=\s*(?P<x_wien2k_NPT>[0-9]+)\s*R0=(?P<x_wien2k_R0>[0-9.]+)\s*RMT=\s*(?P<x_wien2k_RMT>[0-9.]+)\s*Z:\s*(?P<x_wien2k_atomic_number_Z>[0-9.]+)",)
#           ]
#       )
    ])

def get_cachingLevelForMetaName(metaInfoEnv, CachingLvl):
    """Sets the caching level for the metadata.

    Args:
        metaInfoEnv: metadata which is an object of the class InfoKindEnv in nomadcore.local_meta_info.py.
        CachingLvl: Sets the CachingLevel for the sections k_band, run, and single_configuration_calculation.
            This allows to run the parser without opening new sections.

    Returns:
        Dictionary with metaname as key and caching level as value.
    """
    # manually adjust caching of metadata
    cachingLevelForMetaName = {
                               'section_run': CachingLvl,
                               'section_method': CachingLvl
                              }
    return cachingLevelForMetaName

# loading metadata from nomad-meta-info/meta_info/nomad_meta_info/fhi_aims.nomadmetainfo.json