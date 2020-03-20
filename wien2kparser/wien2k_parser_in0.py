from builtins import object
from nomadcore.simple_parser import mainFunction, CachingLevel
from nomadcore.simple_parser import SimpleMatcher as SM
from nomadcore.local_meta_info import loadJsonFile, InfoKindEl
import os, sys, json, logging



################################################################
# This is the subparser for the WIEN2k input file (.in0)
################################################################

# Copyright 2016-2018 Daria M. Tomecka, Fawzi Mohamed
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__author__ = "Daria M. Tomecka"
__maintainer__ = "Daria M. Tomecka"
__email__ = "tomeckadm@gmail.com;"
__date__ = "15/05/2017"

class Wien2kIn0Context(object):
    """context for wien2k In0 parser"""

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

    def onClose_x_wien2k_section_XC(self, backend, gIndex, section):
        xc_index = section["x_wien2k_indxc"]   #[0]
        #logging.error("winsectxc: %s -> %s", section, xc_index)
        if not xc_index:
            xc_index = ["XC_PBE"]
        xc_map_legend = {

            '5': ['LDA_C_PW_RPA'],
            'XC_LDA': ['LDA_X_2D'],

            '13': ['GGA_X_PBE', 'GGA_C_PBE'],
            'XC_PBE':['GGA_X_PBE', 'GGA_C_PBE'],

            '19': ['GGA_X_PBE_SOL', 'GGA_C_PBE_SOL'],
            'XC_PBESOL': ['GGA_X_PBE_SOL', 'GGA_C_PBE_SOL'],

            '11': ['GGA_X_WC'],
            'XC_WC': ['GGA_X_WC'],

            '17': ['GGA_X_PW91'],
            'EC_PW91': ['GGA_X_PW91'],
            'VC_PW91': ['GGA_X_PW91'],

            '28': ['MGGA_X_TB09'],
            'XC_MBJ': ['MGGA_X_TB09'],

            '29': ['MGGA_C_REVTPSS, GGA_C_REGTPSS'],
            'XC_REVTPSS': ['MGGA_C_REVTPSS, GGA_C_REGTPSS'],

            '24': ['GGA_X_B88', 'GGA_C_LYP'],
            'EX_B88': ['GGA_X_B88'],
            'VX_B88': ['GGA_X_B88'],
            'EC_LYP': ['GGA_C_LYP'],
            'VC_LYP': ['GGA_C_LYP'],

            '18': ['HYB_GGA_XC_B3PW91'],
            'XC_B3PW91': ['HYB_GGA_XC_B3PW91'],

            '27': ['MGGA_X_TPSS','MGGA_C_TPSS'],
            'XC_TPSS': ['MGGA_X_TPSS','MGGA_C_TPSS'],

            '46':['GGA_X_HTBS'],
            'XC_HTBS': ['GGA_X_HTBS'],

            '47': ['HYB_GGA_XC_B3LYP'],
            'XC_B3LYP': ['HYB_GGA_XC_B3LYP'],


            #        51: ['-'],
            #        EX_SLDA:
            #        VX_SLDA:

            #        52: ['-'],
            #        EX_SPBE:
            #        VX_SPBE:

            #        53: ['-'],
            #        EX_SWC:
            #        VX_SWC:

            #        54: ['-'],
            #        EX_SPBESOL:
            #        VX_SPBESOL:

            #        55: ['-'],
            #        EX_SB88:
            #        VX_SB88:

            '6': ['HF_X'],
            'EX_LDA': ['HF_X'],
            'VX_LDA': ['HF_X']
        }

        # Push the functional string into the backend
        xc_map_legend = xc_map_legend.get(xc_index[0])
        if not xc_map_legend:
            raise Exception("Unhandled xc functional %s found" % xc_index)


        for xc_name in xc_map_legend:
            #  for xc_name in xc_map_legend[xc_index]:
            s = backend.openSection("section_XC_functionals")
            backend.addValue("XC_functional_name", xc_name)
            backend.closeSection("section_XC_functionals", s)

# description of the input
def buildIn0Matchers():
    return SM(
        name = 'root',
        weak = True,
        startReStr = "",
        sections = ["section_run", "section_method"],
        subMatchers = [
            #        SM(name = 'systemName',
            #          startReStr = r"(?P<x_wien2k_system_nameIn>.*)"),
            SM(r"(?P<x_wien2k_switch>\w*)\s*(?P<x_wien2k_indxc>\w*)\s*.*",sections = ['x_wien2k_section_XC']),
            SM(r"\s*(?P<x_wien2k_ifft_x>[0-9]+)\s*(?P<x_wien2k_ifft_y>[0-9]+)\s*(?P<x_wien2k_ifft_z>[0-9]+)\s*(?P<x_wien2k_ifft_factor>[0-9.]+)\s*(?P<x_wien2k_iprint>[0-9]+).*")
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
