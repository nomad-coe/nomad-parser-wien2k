from builtins import object
import setup_paths
from nomadcore.simple_parser import mainFunction, CachingLevel
from nomadcore.simple_parser import SimpleMatcher as SM
from nomadcore.local_meta_info import loadJsonFile, InfoKindEl
import os, sys, json, logging
import numpy as np


################################################################
# This is the subparser for the main WIEN2k input file (.struct)
################################################################


class Wien2kStructContext(object):
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

    def onClose_section_system(self, backend, gIndex, section):
        equiv_atoms = section["x_wien2k_section_equiv_atoms"]
        #logging.error("section: %s", section)
        labels = []
        pos = []
        for eqAtoms in equiv_atoms:
            label = eqAtoms["x_wien2k_atom_name"][0]
            x = eqAtoms["x_wien2k_atom_pos_x"]
            y = eqAtoms["x_wien2k_atom_pos_y"]
            z = eqAtoms["x_wien2k_atom_pos_z"]
            if len(x) != len(y) or len(x) != len(z):
                raise Exception("incorrect parsing, different number of x,y,z components")
            groupPos = [[x[i],y[i],z[i]] for i in range(len(x))]
            nAt = len(groupPos)
            labels += [label for i in range(nAt)]
            pos += groupPos
        backend.addValue("atom_labels", labels)
        backend.addValue("atom_positions", pos)
##OR
"""
        #   atom_positions
        atom_pos = []
        for i in ['x', 'y', 'z']:
            api = section['x_wien2k_atom_pos_' + i]
            if api is not None:
               atom_pos.append(api)
        if atom_pos:
            # need to transpose array since its shape is [number_of_atoms,3] in the metadata
           backend.addArrayValues('atom_positions', np.transpose(np.asarray(atom_pos)))

         #   atom labels
        atom_labels = section['x_wien2k_atom_name']
        if atom_labels is not None:
           backend.addArrayValues('atom_labels', np.asarray(atom_labels))
"""
# description of the input
def buildStructureMatchers():
    return SM(
    name = 'root',
    weak = True,
    startReStr = "",
    sections = ["section_run", "section_system"],
    subMatchers = [
        SM(name = 'systemName',
           startReStr = r"(?P<x_wien2k_system_nameIn>.*)"),
        SM(r"\w+\s*LATTICE,NONEQUIV\.ATOMS.\s*(?P<x_wien2k_nonequiv_atoms>[0-9]+)"),
        SM(r"(?P<x_wien2k_calc_mode>.*)"),
       # SM(r"\s*(?P<x_wien2k_unit_cell_param_a>[-+0-9.eEdD]+)\s*(?P<x_wien2k_unit_cell_param_b>[-+0-9.eEdD]+)\s*(?P<x_wien2k_unit_cell_param_c>[-+0-9.eEdD]+)\s*(?P<x_wien2k_angle_between_unit_axis_alfa>[-+0-9.eEdD]{9})\s*(?P<x_wien2k_angle_between_unit_axis_beta>[-+0-9.eEdD]{9})\s*(?P<x_wien2k_angle_between_unit_axis_gamma>[-+0-9.eEdD]+)"),
        SM(r"\s*(?P<x_wien2k_unit_cell_param_a>[-+0-9]*\.\d{0,6}){0,10}\s*(?P<x_wien2k_unit_cell_param_b>[-+0-9]*\.\d{0,6}){0,10}\s*(?P<x_wien2k_unit_cell_param_c>[-+0-9]*\.\d{0,6}){0,10}\s*(?P<x_wien2k_angle_between_unit_axis_alfa>[-+]?[0-9]*\.\d{0,6}){0,10}\s*(?P<x_wien2k_angle_between_unit_axis_beta>[-+]?[0-9]*\.\d{0,6}){0,10}\s*(?P<x_wien2k_angle_between_unit_axis_gamma>[-+]?[0-9]*\.\d*)"),
        SM(r"\s*ATOM\s*[-0-9]+:\s*X=(?P<x_wien2k_atom_pos_x>[-+0-9.eEdD]+)\s*Y=(?P<x_wien2k_atom_pos_y>[-+0-9.eEdD]+)\s*Z=(?P<x_wien2k_atom_pos_z>[-+0-9.eEdD]+)",
           repeats=True,
           sections=["x_wien2k_section_equiv_atoms"],
           subMatchers=[
               SM(r"\s*[-0-9]+:\s*X=(?P<x_wien2k_atom_pos_x>[-+0-9.eEdD]+)\s*Y=(?P<x_wien2k_atom_pos_y>[-+0-9.eEdD]+)\s*Z=(?P<x_wien2k_atom_pos_z>[-+0-9.eEdD]+)",
                  repeats=True
              ),
    #           SM(r"\s*(?P<atom>.{10})\s*NPT=\s*(?P<NPT>[0-9]+)\s*R0=(?P<r0>[0-9.]+)\s*RMT=\s*(?P<rmt>[0-9.]+)\s*Z:\s*(?P<z>[0-9.]+)",)
               SM(r"\s*(?P<x_wien2k_atom_name>^.+)\s*NPT=\s*(?P<x_wien2k_NPT>[0-9]+)\s*R0=(?P<x_wien2k_R0>[0-9.]+)\s*RMT=\s*(?P<x_wien2k_RMT>[0-9.]+)\s*Z:\s*(?P<x_wien2k_atomic_number_Z>[0-9.]+)",)
           ]
       )
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
                               'section_system': CachingLvl
                              }
    cachingLevelForMetaName["x_wien2k_system_nameIn"] = CachingLevel.ForwardAndCache
    cachingLevelForMetaName["x_wien2k_section_equiv_atoms"] = CachingLevel.ForwardAndCache
    cachingLevelForMetaName["atom_labels"] = CachingLevel.ForwardAndCache
    return cachingLevelForMetaName

# loading metadata from nomad-meta-info/meta_info/nomad_meta_info/fhi_aims.nomadmetainfo.json
