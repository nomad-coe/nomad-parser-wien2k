from builtins import object
# import setup_paths
import numpy as np
import ase.io
import os
import sys

from nomadcore.simple_parser import mainFunction, AncillaryParser, CachingLevel
from nomadcore.simple_parser import SimpleMatcher as SM
from nomadcore.local_meta_info import loadJsonFile, InfoKindEl
import wien2kparser.wien2k_parser_struct as wien2k_parser_struct
import wien2kparser.wien2k_parser_in0 as wien2k_parser_in0
import wien2kparser.wien2k_parser_in1c as wien2k_parser_in1c
import wien2kparser.wien2k_parser_in2c as wien2k_parser_in2c
import wien2kparser.wien2k_parser_in1 as wien2k_parser_in1
import wien2kparser.wien2k_parser_in2 as wien2k_parser_in2
import logging

from nomad.parsing.legacy import CoESimpleMatcherParser

################################################################
# This is the parser for the main output file (.scf) of WIEN2k.
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


class Wien2kContext(object):
    """context for wien2k parser"""

    def __init__(self):
        self.parser = None

    def initialize_values(self):
        """allows to reset values if the same superContext is used to parse different files"""
        self.metaInfoEnv = self.parser.parserBuilder.metaInfoEnv
        self.rootSecMethodIndex = None
        self.secMethodIndex = None
        self.secSystemIndex = None
        self.scfIterNr = 0

    def startedParsing(self, path, parser):
        """called when parsing starts"""
        self.parser = parser
        # allows to reset values if the same superContext is used to parse different files
        self.initialize_values()

    def onClose_x_wien2k_header(self, backend, gIndex, section):
        version_check = section["x_wien2k_version"]
#        riprova = section["x_wien2k_release_date"][0]
#        print("prova=",prova," riprova=",riprova)
        if version_check:
            backend.addValue("program_version",
                             section["x_wien2k_version"][0] + " " +
                             section["x_wien2k_release_date"][0])
        else:
            backend.addValue("program_version", "Before_wien2k11")

    def onOpen_section_system(self, backend, gIndex, section):
        self.secSystemIndex = gIndex

    def onOpen_section_method(self, backend, gIndex, section):

        mainFile = self.parser.fIn.fIn.name
        fName = mainFile[:-4] + ".in0"
        if os.path.exists(fName):
            subSuperContext = wien2k_parser_in0.Wien2kIn0Context()
            subParser = AncillaryParser(
                fileDescription = wien2k_parser_in0.buildIn0Matchers(),
                parser = self.parser,
                cachingLevelForMetaName = wien2k_parser_in0.get_cachingLevelForMetaName(self.metaInfoEnv, CachingLevel.PreOpenedIgnore),
                superContext = subSuperContext)
            with open(fName) as fIn:
                subParser.parseFile(fIn)


        mainFile = self.parser.fIn.fIn.name
        fName = mainFile[:-4] + ".in1c"
        if os.path.exists(fName):
            subSuperContext = wien2k_parser_in1c.Wien2kIn1cContext()
            subParser = AncillaryParser(
                fileDescription = wien2k_parser_in1c.buildIn1cMatchers(),
                parser = self.parser,
                cachingLevelForMetaName = wien2k_parser_in1c.get_cachingLevelForMetaName(self.metaInfoEnv, CachingLevel.PreOpenedIgnore),
                superContext = subSuperContext)
            with open(fName) as fIn:
                subParser.parseFile(fIn)

        mainFile = self.parser.fIn.fIn.name
        fName = mainFile[:-4] + ".in2c"
        if os.path.exists(fName):
            subSuperContext = wien2k_parser_in2c.Wien2kIn2cContext()
            subParser = AncillaryParser(
                fileDescription = wien2k_parser_in2c.buildIn2cMatchers(),
                parser = self.parser,
                cachingLevelForMetaName = wien2k_parser_in2c.get_cachingLevelForMetaName(self.metaInfoEnv, CachingLevel.PreOpenedIgnore),
                superContext = subSuperContext)
            with open(fName) as fIn:
                subParser.parseFile(fIn)

        mainFile = self.parser.fIn.fIn.name
        fName = mainFile[:-4] + ".in1"
        if os.path.exists(fName):
            subSuperContext = wien2k_parser_in1.Wien2kIn1Context()
            subParser = AncillaryParser(
                fileDescription = wien2k_parser_in1.buildIn1Matchers(),
                parser = self.parser,
                cachingLevelForMetaName = wien2k_parser_in1.get_cachingLevelForMetaName(self.metaInfoEnv, CachingLevel.PreOpenedIgnore),
                superContext = subSuperContext)
            with open(fName) as fIn:
                subParser.parseFile(fIn)


        mainFile = self.parser.fIn.fIn.name
        fName = mainFile[:-4] + ".in2"
        if os.path.exists(fName):
            subSuperContext = wien2k_parser_in2.Wien2kIn2Context()
            subParser = AncillaryParser(
                fileDescription = wien2k_parser_in2.buildIn2Matchers(),
                parser = self.parser,
                cachingLevelForMetaName = wien2k_parser_in2.get_cachingLevelForMetaName(self.metaInfoEnv, CachingLevel.PreOpenedIgnore),
                superContext = subSuperContext)
            with open(fName) as fIn:
                subParser.parseFile(fIn)

        #if self.secMethodIndex is None:
        if self.rootSecMethodIndex is None:
            self.rootSecMethodIndex = gIndex
        self.secMethodIndex = gIndex
#        self.secMethodIndex["single_configuration_to_calculation_method_ref"] = gIndex


    def onClose_section_single_configuration_calculation(self, backend, gIndex, section):
       # write number of SCF iterations
        backend.addValue('number_of_scf_iterations', self.scfIterNr)
        # write the references to section_method and section_system
        backend.addValue('single_configuration_to_calculation_method_ref', self.secMethodIndex)
        backend.addValue('single_configuration_calculation_to_system_ref', self.secSystemIndex)


    def onClose_section_system(self, backend, gIndex, section):

        #backend.addValue("smearing_kind", x_fleur_smearing_kind)
        smearing_kind = section['x_wien2k_smearing_kind']
        if smearing_kind is not None:
        #    value = ''
            backend.addValue('x_wien2k_smearing_kind', value)


        smearing_width = section['x_wien2k_smearing_width']
        if smearing_width is not None:
        #    value = ''
            backend.addValue('x_wien2k_smearing_width', value)

        #   atom labels
        atom_labels = section['x_wien2k_atom_name']
        if atom_labels is not None:
           backend.addArrayValues('atom_labels', np.asarray(atom_labels))

        # atom force
        atom_force = []
        for i in ['x', 'y', 'z']:
            api = section['x_wien2k_for_' + i]
            if api is not None:
               atom_force.append(api)
        if atom_force:
            # need to transpose array since its shape is [number_of_atoms,3] in\the metadata
           backend.addArrayValues('atom_forces', np.transpose(np.asarray(atom_force)))

        # Parse the structure file
        mainFile = self.parser.fIn.fIn.name
        fName = mainFile[:-4] + ".struct"
        if os.path.exists(fName):

            # ASE does not support reading file object for WIEN2k structure files.
            try:
                atoms = ase.io.read(fName, format="struct")
            except Exception:
                logging.error("Could not read/parse the WIEN2k structure file.")
            else:
                pos = atoms.get_positions() * 1E-10
                symbols = atoms.get_chemical_symbols()
                cell = atoms.get_cell() * 1E-10
                pbc = atoms.get_pbc()
                backend.addArrayValues('lattice_vectors', cell)
                backend.addArrayValues("configuration_periodic_dimensions", pbc)
                backend.addValue("atom_labels", symbols)
                backend.addArrayValues('atom_positions', pos)

            with open(fName, "r") as fin:
                structSuperContext = wien2k_parser_struct.Wien2kStructContext()
                structParser = AncillaryParser(
                    fileDescription = wien2k_parser_struct.buildStructureMatchers(),
                    parser = self.parser,
                    cachingLevelForMetaName = wien2k_parser_struct.get_cachingLevelForMetaName(self.metaInfoEnv, CachingLevel.PreOpenedIgnore),
                    superContext = structSuperContext)
                structParser.parseFile(fin)

    def onClose_section_scf_iteration(self, backend, gIndex, section):
        #Trigger called when section_scf_iteration is closed.

        # count number of SCF iterations
        self.scfIterNr += 1

# description of the input
mainFileDescription = SM(
    name = 'root',
    weak = True,
    startReStr = "",
    sections   = ['section_run','x_wien2k_header'],
    subMatchers = [
        SM(r"\s*:LABEL[0-9]+: using WIEN2k_(?P<x_wien2k_version>[0-9.]+) \(Release (?P<x_wien2k_release_date>[0-9/.]+)\) in "),
        SM(name = 'newRun',
#           subMatchers=[
#           SM(r"\s*:LABEL[0-9]+: using WIEN2k_(?P<x_wien2k_version>[0-9.]+) \(Release (?P<x_wien2k_release_date>[0-9/.]+)\) in ")
#           ],
           startReStr = r"\s*:ITE[0-9]+:\s*[0-9]+.\s*ITERATION",
           repeats = True,
           required = True,
           forwardMatch = True,
           sections   = ['section_method', 'section_system', 'section_single_configuration_calculation'],
           fixedStartValues={'program_name': 'WIEN2k', 'program_basis_set_type': '(L)APW+lo' }, #, 'program_version': 'Before WIEN2k_11'},
           subMatchers = [
               SM(
                  name = "scf iteration",
                  startReStr = r"\s*:ITE(?P<x_wien2k_iteration_number>[0-9]+):\s*[0-9]*. ITERATION",
                  sections=["section_scf_iteration"],
                  repeats = True,
                  subMatchers=[
                      SM(r":NATO\s*:\s*(?P<x_wien2k_nr_of_independent_atoms>[0-9]+)\s*INDEPENDENT AND\s*(?P<x_wien2k_total_atoms>[0-9]+)\s*TOTAL ATOMS IN UNITCELL"),
                      SM(r"\s*SUBSTANCE: (?P<x_wien2k_system_name>.*)"),
                      SM(r":POT\s*:\s*POTENTIAL OPTION\s*(?P<x_wien2k_potential_option>[0-9]+)"),
                      SM(r":LAT\s*:\s*LATTICE CONSTANTS=\s*(?P<x_wien2k_lattice_const_a>[0-9.]+)\s*(?P<x_wien2k_lattice_const_b>[0-9.]+)\s*(?P<x_wien2k_lattice_const_c>[0-9.]+)"),
                      SM(r":VOL\s*:\s*UNIT CELL VOLUME\s*=\s*(?P<x_wien2k_unit_cell_volume_bohr3>[0-9.]+)"),
                      SM(r":RKM  : MATRIX SIZE (?P<x_wien2k_matrix_size>[0-9]+)\s*LOs:\s*(?P<x_wien2k_LOs>[0-9.]+)\s*RKM=\s*(?P<x_wien2k_rkm>[0-9.]+)\s*WEIGHT=\s*[0-9.]*\s*\w*:"),
                      SM(r":KPT\s*:\s*NUMBER\s*OF\s*K-POINTS:\s*(?P<x_wien2k_nr_kpts>[-+0-9.]+)"),
                      #SM(r":GMA\s*:\s*POTENTIAL\sAND\sCHARGE\sCUT-OFF\s*(?P<x_wien2k_cutoff>[0-9.]+)\s*Ry\*\*[0-9.]+"),
                      SM(r":GMA\s*:\s*POTENTIAL\sAND\sCHARGE\sCUT-OFF\s*(?P<x_wien2k_cutoff>[0-9.]+)\s*Ry\W\W[0-9.]+"),
                      SM(r":GAP\s*:\s*(?P<x_wien2k_ene_gap__rydberg>[-+0-9.]+)\s*Ry\s*=\s*(?P<x_wien2k_ene_gap_eV>[-+0-9.]+)\s*eV\s*.*"),
                      SM(r":NOE\s*:\s*NUMBER\sOF\sELECTRONS\s*=\s*(?P<x_wien2k_noe>[0-9.]+)"),
                      SM(r":FER\s*:\s(\w*\s*)*-\s\w*\W\w*\WM\W*=\s*(?P<x_wien2k_fermi_ene__rydberg>[-+0-9.]+)"),
                      SM(r":GMA\s*:\s*POTENTIAL\sAND\sCHARGE\sCUT-OFF\s*[0-9.]+\s*Ry\W\W[0-9.]+"),
                      SM(r":CHA(?P<x_wien2k_atom_nr>[-+0-9]+):\s*TOTAL\s*\w*\s*CHARGE INSIDE SPHERE\s*(?P<x_wien2k_sphere_nr>[-+0-9]+)\s*=\s*(?P<x_wien2k_tot_val_charge_sphere>[0-9.]+)",repeats = True),
                      SM(r":CHA\s*:\s*TOTAL\s*\w*\s*CHARGE INSIDE\s*\w*\s*CELL\s=\s*(?P<x_wien2k_tot_val_charge_cell>[-+0-9.]+)"),
                      SM(r":MMTOT: TOTAL MAGNETIC MOMENT IN CELL =\s*(?P<x_wien2k_mmtot>[-+0-9.]+)"),
                      SM(r":MMINT: MAGNETIC MOMENT IN INTERSTITIAL =\s*(?P<x_wien2k_mmint>[-+0-9.]+)"),
                      SM(r":MMI001: MAGNETIC MOMENT IN SPHERE 1 =\s*(?P<x_wien2k_mmi001>[-+0-9.]+)"),
                      SM(r":RTO(?P<x_wien2k_atom_nr>[-+0-9]+)\s*:\s*[0-9]+\s*(?P<x_wien2k_density_at_nucleus_valence>[-+0-9.]+)\s*(?P<x_wien2k_density_at_nucleus_semicore>[-+0-9.]+)\s*(?P<x_wien2k_density_at_nucleus_core>[-+0-9.]+)\s*(?P<x_wien2k_density_at_nucleus_tot>[0-9.]+)",repeats = True),
                      SM(r":NTO\s*:\s*\sTOTAL\s*INTERSTITIAL\s*CHARGE=\s*(?P<x_wien2k_tot_int_charge_nm>[-+0-9.]+)"),
                      SM(r":NTO(?P<x_wien2k_atom_nr>[-+0-9]+)[0-9]*:\s*\sTOTAL\s*CHARGE\s*IN\s*SPHERE\s*(?P<x_wien2k_sphere_nr>[-+0-9]+)\s*=\s*(?P<x_wien2k_tot_charge_in_sphere_nm>[-+0-9.]+)",repeats = True),
                      SM(r":DTO(?P<x_wien2k_atom_nr>[-+0-9]+)[0-9]*:\sTOTAL\s*DIFFERENCE\s*CHARGE\W*\w*\s*IN\s*SPHERE\s*(?P<x_wien2k_sphere_nr>[-+0-9]+)\s*=\s*(?P<x_wien2k_tot_diff_charge>[-+0-9.]+)", repeats = True),
                      SM(r":DIS\s*:\s*CHARGE\sDISTANCE\s*\W*[0-9.]+\sfor\satom\s*[0-9]*\sspin\s[0-9]*\W\s*(?P<x_wien2k_charge_distance>[0-9.]+)"),
                      SM(r":CTO\s*:\s*\sTOTAL\s*INTERSTITIAL\s*CHARGE=\s*(?P<x_wien2k_tot_int_charge>[-+0-9.]+)"),
                      SM(r":CTO(?P<x_wien2k_atom_nr>[-+0-9]+)[0-9]*:\s*\sTOTAL\s*CHARGE\s*IN\s*SPHERE\s*(?P<x_wien2k_sphere_nr>[-+0-9]+)\s*=\s*(?P<x_wien2k_tot_charge_in_sphere>[-+0-9.]+)",repeats = True),
#                      SM(r":NEC(?P<x_wien2k_necnr>[-+0-9]+)\s*:\s*NUCLEAR AND ELECTRONIC CHARGE\s*(?P<x_wien2k_nuclear_charge>[-+0-9.]+)\s*(?P<x_wien2k_electronic_charge>[0-9.]+)",repeats = True),
                      SM(r":ENE\s*:\s*\W*\w*\W*\s*TOTAL\s*ENERGY\s*IN\s*Ry\s*=\s*(?P<x_wien2k_energy_total__rydberg>[-+0-9.]+)"),
                      SM(r":FOR[0-9]*:\s*(?P<x_wien2k_atom_nr>[0-9]+).ATOM\s*(?P<x_wien2k_for_abs>[0-9.]+)\s*(?P<x_wien2k_for_x>[-++0-9.]+)\s*(?P<x_wien2k_for_y>[-+0-9.]+)\s*(?P<x_wien2k_for_z>[-+0-9.]+)\s*partial\sforces", repeats = True),
                      SM(r":FGL[0-9]*:\s*(?P<x_wien2k_atom_nr>[0-9]+).ATOM\s*(?P<x_wien2k_for_x_gl>[-+0-9.]+)\s*(?P<x_wien2k_for_y_gl>[-+0-9.]+)\s*(?P<x_wien2k_for_z_gl>[-+0-9.]+)\s*partial\sforces", repeats = True)
                  ]
              )
           ]
       )
    ])


class Wien2kParser(CoESimpleMatcherParser):

    def metainfo_env(self):
        from .metainfo import m_env
        return m_env

    def create_super_context(self):
        return Wien2kContext()

    def create_simple_matcher(self):
        return mainFileDescription

    def create_parser_description(self):
        return {
            "name": "Wien2k",
            "version": "1.0"
        }

    def create_caching_levels(self):
        return {
            "XC_functional_name": CachingLevel.ForwardAndCache,
            "energy_total": CachingLevel.ForwardAndCache
        }
