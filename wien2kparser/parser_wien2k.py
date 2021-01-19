#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD.
# See https://nomad-lab.eu for further info.
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
#
from builtins import object
# import setup_paths
import numpy as np
import ase.io
import os
import sys

from nomadcore.simple_parser import mainFunction, AncillaryParser, CachingLevel
from nomadcore.simple_parser import SimpleMatcher as SM
from nomadcore.local_meta_info import loadJsonFile, InfoKindEl
from nomadcore.unit_conversion import unit_conversion
import wien2kparser.wien2k_parser_struct as wien2k_parser_struct
import wien2kparser.wien2k_parser_in0 as wien2k_parser_in0
import wien2kparser.wien2k_parser_in1 as wien2k_parser_in1
import wien2kparser.wien2k_parser_in2 as wien2k_parser_in2
import logging

from nomad.parsing.legacy import CoESimpleMatcherParser

################################################################
# This is the parser for the main output file (.scf) of WIEN2k.
################################################################

# Copyright 2016-2018 Daria M. Tomecka, Fawzi Mohamed
# Copyright 2020 Pavel Ondračka
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
        self.spinPol = None
        self.eTot = None
        self.forces = None

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
        fName = mainFile[:-4] + ".in1"
        if not os.path.exists(fName):
            fName = mainFile[:-4] + ".in1c"
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
        if not os.path.exists(fName):
            fName = mainFile[:-4] + ".in2c"
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
        fromR = unit_conversion.convert_unit_function("rydberg", "J")

        if self.eTot is not None:
            backend.addValue("energy_total", self.eTot)

        if self.forces is not None:
           backend.addArrayValues('atom_forces', self.forces)

        mainFile = self.parser.fIn.fIn.name

        eigvalKpoint=[]
        eigvalKpointMult=[]
        eigvalVal=[[]]

        # Read eigenvalues from the energy files
        # this can be either case.energy for non spinpolarized serial calculation
        # case.energyup and case.energydn for spinpolarized serial calculation
        # case.energy_x files for non spinpolarized parallel calculation
        # case.energyup_x and case.energydn_x for spinpolarized parallel calculation
        if self.spinPol == None:
            suffixes = ["", "up", "dn"]
        elif self.spinPol:
            suffixes = ["up", "dn"]
        else:
            suffixes = [""]
        spin = 0

        for suf in suffixes:
            for i in range(1000):
                paraIdx = ""
                if i != 0:
                    paraIdx = "_" + str(i)
                fName = mainFile[:-4] + ".energy" + suf + paraIdx
                if os.path.exists(fName) and os.stat(fName).st_size > 0:
                    with open(fName) as g:
                        if suf == "dn":
                            spin = 1
                            if len(eigvalVal) == 1:
                                eigvalVal.append([])
                        else:
                            spin = 0
                        eigvalToRead=0
                        for l in g:
                            if len(l) > 90:
                                continue
                            #there are no spaces sometime between the numbers but the format is fixed
                            if eigvalToRead == 0:
                                kx = float(l[0:19])
                                ky = float(l[19:38])
                                kz = float(l[38:57])
                                eigvalKpointInd = int(l[57:67])
                                if len(eigvalKpoint) == eigvalKpointInd - 1:
                                    eigvalKpoint.append([kx, ky, kz])
                                    eigvalKpointMult.append([int(float(l[79:84]))])
                                if len(eigvalVal[spin]) != eigvalKpointInd -1:
                                    break
                                    #raise Exception("Found old eigenvalues for the current k-point while reading from %s,\
                                    #        possible mixing of serial nad parallel runs?" % fName)
                                eigvalToRead = int(l[73:79])
                                eigvalVal[spin].append([])
                            else:
                                eigvalVal[spin][-1].append(fromR(float(l[12:31])))
                                eigvalToRead -= 1
                elif i > 0:
                    break
        if eigvalVal[0]: 
            eigvalGIndex = backend.openSection("section_eigenvalues")
            backend.addArrayValues("eigenvalues_values", np.asarray(eigvalVal))
            backend.addArrayValues("eigenvalues_kpoints", np.asarray(eigvalKpoint))
            backend.addArrayValues("eigenvalues_kpoints_multiplicity", np.asarray(eigvalKpointMult))
            backend.closeSection("section_eigenvalues",eigvalGIndex)

        #iterate over all dos files, for now just the total dos is supported
        spin = 0
        DOS = [[]]
        ene = []
        eneNorm = []
        for suf in suffixes:
            for n in range(1,50):
                fName = mainFile[:-4] + ".dos" + str(n) + suf
                if os.path.exists(fName):
                    #read the DOS file
                    with open(fName) as f:
                        if suf == "dn":
                            spin = 1
                            if len(DOS) == 1:
                                DOS.append([])
                        ene = []
                        eneNorm = []
                        Ef = 0.0
                        totDOScol = 0
                        for i,l in enumerate(f):
                            l = l.split()
                            if i == 1:
                                Ef = float(l[1])
                            if i == 2:
                                #find out which column is the total DOS
                                for j,w in enumerate(l):
                                    if "total-DOS" in w or "TOTAL" in w:
                                        totDOScol = j - 1
                                        break
                                # there is no total DOS column here
                                if totDOScol == 0:
                                    break
                            if i > 2:
                                ene.append(fromR(float(l[0])))
                                eneNorm.append(fromR(float(l[0]) - Ef))
                                DOS[spin].append(float(l[totDOScol]) / fromR(1.0))
                    # we found the total DOS, ignore the rest of files
                    if DOS[spin]:
                        break
                else:
                    break
        if DOS[0]:
            DOSGIndex = backend.openSection("section_dos")
            backend.addArrayValues("dos_energies", np.asarray(ene))
            backend.addArrayValues("dos_energies_normalized", np.asarray(eneNorm))
            backend.addArrayValues("dos_values", np.asarray(DOS))
            backend.addValue("dos_kind", "electronic")
            backend.addValue("number_of_dos_values", len(DOS[0]))
            backend.closeSection("section_dos",DOSGIndex)


    def onClose_section_system(self, backend, gIndex, section):

        #   atom labels
        atom_labels = section['x_wien2k_atom_name']
        if atom_labels is not None:
           backend.addArrayValues('atom_labels', np.asarray(atom_labels))

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

    def onClose_section_method(self, backend, gIndex, section):
        #Trigger called when section_method is closed.

        if self.spinPol is not None:
            if self.spinPol:
                backend.addValue("number_of_spin_channels", 2)
            else:
                backend.addValue("number_of_spin_channels", 1)

        mainFile = self.parser.fIn.fIn.name

        #read kpoints from the klist file
        klistFile = mainFile[:-4] + ".klist"
        if os.path.exists(klistFile):
            with open(klistFile) as f:
                kMeshWeights=[]
                weightsSum=0.0
                kMeshPoints=[]
                for l in f:
                    tmp = l.split()
                    if len(tmp) >= 6:
                        kMeshWeights.append(float(tmp[5]))
                        weightsSum += kMeshWeights[-1]
                        kMeshPoints.append([float(tmp[1])/float(tmp[4]), float(tmp[2])/float(tmp[4]), float(tmp[3])/float(tmp[4])])
                    elif tmp[0] == 'END': break
                kMeshWeights = [w/weightsSum for w in kMeshWeights]
                backend.addArrayValues("k_mesh_points", np.asarray(kMeshPoints))
                backend.addArrayValues("k_mesh_weights", np.asarray(kMeshWeights))

    def onClose_section_scf_iteration(self, backend, gIndex, section):
        #Trigger called when section_scf_iteration is closed.

        # count number of SCF iterations
        self.scfIterNr += 1

        sp = section["x_wien2k_spinpolarization"]
        if sp is not None:
            if "NON" in sp[0]:
                self.spinPol = False
            else:
                self.spinPol = True
        
        eTot = section["energy_total_scf_iteration"]
        if eTot is not None:
            self.eTot = eTot[0]

        # save the forces
        fx = section['x_wien2k_for_x_gl']
        fy = section['x_wien2k_for_y_gl']
        fz = section['x_wien2k_for_z_gl']
        if fx is not None and fy is not None and fz is not None:
            backend.addArrayValues('x_wien2k_for_x_gl', fx)
            backend.addArrayValues('x_wien2k_for_y_gl', fy)
            backend.addArrayValues('x_wien2k_for_z_gl', fz)
            # account for atom multiplicities
            self.forces=[]
            for i,a in enumerate(section['x_wien2k_atom_mult']):
                for _ in range(a):
                    self.forces.append([fx[i], fy[i], fz[i]])
            print (self.forces)


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
                      # older Wien2k versions used numerical identification for the potential
                      # newer Wien2k versions allow to specificy separatelly the functional for calculation of both exchange and correlation potential and energy separatelly
                      # the output can look like this, ":POT  : POTENTIAL OPTION EX_LDA EC_LDA VX_MBJ VC_LDA"
                      SM(r":POT\s*:\s*POTENTIAL OPTION\s*(?P<x_wien2k_potential_option>[0-9 \w]+)"),
                      SM(r":LAT\s*:\s*LATTICE CONSTANTS=\s*(?P<x_wien2k_lattice_const_a>[0-9.]+)\s*(?P<x_wien2k_lattice_const_b>[0-9.]+)\s*(?P<x_wien2k_lattice_const_c>[0-9.]+)"),
                      SM(r":VOL\s*:\s*UNIT CELL VOLUME\s*=\s*(?P<x_wien2k_unit_cell_volume_bohr3>[0-9.]+)"),
                      SM(r"\s*(?P<x_wien2k_spinpolarization>(NON-)?SPINPOLARIZED) CALCULATION\s*"),
                      SM(r":RKM  : MATRIX SIZE\s*(?P<x_wien2k_matrix_size>[0-9]+)\s*LOs:\s*(?P<x_wien2k_LOs>[0-9.]+)\s*RKM=\s*(?P<x_wien2k_rkm>[0-9.]+)\s*WEIGHT=\s*[0-9.]*\s*\w*:"),
                      SM(r":KPT\s*:\s*NUMBER\s*OF\s*K-POINTS:\s*(?P<x_wien2k_nr_kpts>[-+0-9.]+)"),
                      SM(r":GAP\s*:\s*(?P<x_wien2k_ene_gap__rydberg>[-+0-9.]+)\s*Ry\s*=\s*(?P<x_wien2k_ene_gap_eV>[-+0-9.]+)\s*eV\s*.*"),
                      SM(r":NOE\s*:\s*NUMBER\sOF\sELECTRONS\s*=\s*(?P<x_wien2k_noe>[0-9.]+)"),
                      SM(r":FER\s*:\sF E R M I - ENERGY\W\w*\W\w*M\W*=\s*(?P<energy_reference_fermi_iteration__rydberg>[-+0-9.]+)"),
                      SM(r":GMA\s*:\s*POTENTIAL\sAND\sCHARGE\sCUT-OFF\s*(?P<x_wien2k_cutoff>[0-9.]+)\s*Ry\W\W[0-9.]+"),
                      SM(r":POS[0-9]*:\s*ATOM\s*[-0-9.]+\s*X,Y,Z\s*=[-0-9. ]+MULT=\s*(?P<x_wien2k_atom_mult>[0-9]+)\s*ZZ=\s*[0-9.]+.*", repeats = True),
                      #FIXME: this is repeating interleaved with the previous matcher and likely need its own submatcher 
#                     SM(r":CHA(?P<x_wien2k_atom_nr>[-+0-9]+):\s*TOTAL\s*\w*\s*CHARGE INSIDE SPHERE\s*(?P<x_wien2k_sphere_nr>[-+0-9]+)\s*=\s*(?P<x_wien2k_tot_val_charge_sphere>[0-9.]+)",repeats = True),
#                      SM(r":CHA\s*:\s*TOTAL\s*\w*\s*CHARGE INSIDE\s*\w*\s*CELL\s=\s*(?P<x_wien2k_tot_val_charge_cell>[-+0-9.]+)"),
                      SM(r":SUM\s*:\s*SUM OF EIGENVALUES\s*=\s*(?P<energy_sum_eigenvalues_scf_iteration__rydberg>[-+0-9.]+)"),
                      SM(r":RTO(?P<x_wien2k_atom_nr>[-+0-9]+)\s*:\s*[0-9]+\s*(?P<x_wien2k_density_at_nucleus_valence>[-+0-9.]+)\s*(?P<x_wien2k_density_at_nucleus_semicore>[-+0-9.]+)\s*(?P<x_wien2k_density_at_nucleus_core>[-+0-9.]+)\s*(?P<x_wien2k_density_at_nucleus_tot>[0-9.]+)",repeats = True),
                      #FIXME: followig matchers work just for cases without spin polarization
                      SM(r":NTO\s*:\s*\sTOTAL\s*INTERSTITIAL\s*CHARGE=\s*(?P<x_wien2k_tot_int_charge_nm>[-+0-9.]+)"),
                      SM(r":NTO(?P<x_wien2k_atom_nr>[-+0-9]+)[0-9]*:\s*\sTOTAL\s*CHARGE\s*IN\s*SPHERE\s*(?P<x_wien2k_sphere_nr>[-+0-9]+)\s*=\s*(?P<x_wien2k_tot_charge_in_sphere_nm>[-+0-9.]+)",repeats = True),
                      SM(r":DTO(?P<x_wien2k_atom_nr>[-+0-9]+)[0-9]*:\sTOTAL\s*DIFFERENCE\s*CHARGE\W*\w*\s*IN\s*SPHERE\s*(?P<x_wien2k_sphere_nr>[-+0-9]+)\s*=\s*(?P<x_wien2k_tot_diff_charge>[-+0-9.]+)", repeats = True),
                      SM(r":DIS\s*:\s*CHARGE\sDISTANCE\s*\W*[0-9.]+\sfor\satom\s*[0-9]*\sspin\s[0-9]*\W\s*(?P<x_wien2k_charge_distance>[0-9.]+)"),
                      SM(r":CTO\s*:\s*\sTOTAL\s*INTERSTITIAL\s*CHARGE=\s*(?P<x_wien2k_tot_int_charge>[-+0-9.]+)"),
                      SM(r":CTO(?P<x_wien2k_atom_nr>[-+0-9]+)[0-9]*:\s*\sTOTAL\s*CHARGE\s*IN\s*SPHERE\s*(?P<x_wien2k_sphere_nr>[-+0-9]+)\s*=\s*(?P<x_wien2k_tot_charge_in_sphere>[-+0-9.]+)",repeats = True),
#                      SM(r":NEC(?P<x_wien2k_necnr>[-+0-9]+)\s*:\s*NUCLEAR AND ELECTRONIC CHARGE\s*(?P<x_wien2k_nuclear_charge>[-+0-9.]+)\s*(?P<x_wien2k_electronic_charge>[0-9.]+)",repeats = True),
                      SM(r":MMINT:\s*MAGNETIC MOMENT IN INTERSTITIAL\s*=\s*(?P<x_wien2k_mmint>[-+0-9.]+)"),
                      #FIXME: read for all spheres
                      SM(r":MMI001:\s*MAGNETIC MOMENT IN SPHERE\s*1\s*=\s*(?P<x_wien2k_mmi001>[-+0-9.]+)"),
                      # its not clear if the old and new MMTOT (total magnetic moment in cell vs spin magnetic moment in cell) are the same thing?
                      SM(r":MMTOT:\s*(TOTAL|SPIN) MAGNETIC MOMENT IN CELL\s*=\s*(?P<x_wien2k_mmtot>[-+0-9.]+)"),
                      SM(r":ENE\s*:\s*\W*\w*\W*\s*TOTAL\s*ENERGY\s*IN\s*Ry\s*=\s*(?P<energy_total_scf_iteration__rydberg>[-+0-9.]+)"),
                      SM(r":FOR[0-9]*:\s*(?P<x_wien2k_atom_nr>[0-9]+).ATOM\s*(?P<x_wien2k_for_abs>[0-9.]+)\s*(?P<x_wien2k_for_x>[-++0-9.]+)\s*(?P<x_wien2k_for_y>[-+0-9.]+)\s*(?P<x_wien2k_for_z>[-+0-9.]+)\s*partial\sforces", repeats = True),
                      SM(r":FGL[0-9]*:\s*(?P<x_wien2k_atom_nr>[0-9]+).ATOM\s*(?P<x_wien2k_for_x_gl__mrydberg_bohr_1>[-+0-9.]+)\s*(?P<x_wien2k_for_y_gl__mrydberg_bohr_1>[-+0-9.]+)\s*(?P<x_wien2k_for_z_gl__mrydberg_bohr_1>[-+0-9.]+)\s*total\sforces", repeats = True),
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
