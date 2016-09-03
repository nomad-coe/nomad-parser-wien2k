from builtins import object
import setup_paths
from nomadcore.simple_parser import mainFunction, CachingLevel
from nomadcore.simple_parser import SimpleMatcher as SM
from nomadcore.local_meta_info import loadJsonFile, InfoKindEl
import os, sys, json

class Wien2kIn2cContext(object):
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
def buildIn2cMatchers():
    return SM(
    name = 'root',
    weak = True,
    startReStr = "",
        sections = ["section_run", "section_method"],
    subMatchers = [
        SM(r"\s*(?P<x_wien2k_in2c_switch>[A-Z]+)\s*.*"),
        SM(r"\s*(?P<x_wien2k_in2c_emin>[-+0-9.]+)\s*(?P<x_wien2k_in2c_ne>[-+0-9.]+)\s*(?P<x_wien2k_in2c_espermin>[-+0-9.]+)\s*(?P<x_wien2k_in2c_esper0>[-+0-9.]+)\s*.*"),
        SM(r"\s*(?P<smearing_kind>[A-Z]+)\s*\s*(?P<smearing_width>[-+0-9.]+)\s*.*"),
        SM(r"\s*(?P<x_wien2k_in2c_gmax>[-+0-9.]+)\s*GMAX")
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
