from builtins import object
import setup_paths
from nomadcore.simple_parser import mainFunction, AncillaryParser, CachingLevel
from nomadcore.simple_parser import SimpleMatcher as SM
from nomadcore.local_meta_info import loadJsonFile, InfoKindEl
import os, sys, json
import wien2k_parser_struct, wien2k_parser_in0

class Wien2kContext(object):
    """context for wien2k parser"""

    def __init__(self):
        self.parser = None

    def initialize_values(self):
        """allows to reset values if the same superContext is used to parse different files"""
        self.metaInfoEnv = self.parser.parserBuilder.metaInfoEnv

    def startedParsing(self, path, parser):
        """called when parsing starts"""
        self.parser = parser
        # allows to reset values if the same superContext is used to parse different files
        self.initialize_values()

    def onClose_x_wien2k_header(self, backend, gIndex, section):
        backend.addValue("program_version",
                         section["x_wien2k_version"][0] + " " +
                         section["x_wien2k_release_date"][0])

    def onOpen_section_system(self, backend, gIndex, section):
        mainFile = self.parser.fIn.fIn.name
        fName = mainFile[:-4] + ".struct"
        if os.path.exists(fName):
            structSuperContext = wien2k_parser_struct.Wien2kStructContext()
            structParser = AncillaryParser(
                fileDescription = wien2k_parser_struct.buildStructureMatchers(),
                parser = self.parser,
                cachingLevelForMetaName = wien2k_parser_struct.get_cachingLevelForMetaName(self.metaInfoEnv, CachingLevel.PreOpenedIgnore),
                superContext = structSuperContext)

            with open(fName) as fIn:
                structParser.parseFile(fIn)

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

# description of the input
mainFileDescription = SM(
    name = 'root',
    weak = True,
    startReStr = "",
    subMatchers = [
        SM(name = 'newRun',
           startReStr = r"\s*:LABEL[0-9]+: using WIEN2k_(?:[0-9.]+) \(Release (?:[0-9/.]+)\) in ",
           repeats = True,
           required = True,
           forwardMatch = True,
           sections   = ['section_run', 'section_method', 'section_system', 'section_single_configuration_calculation'],
           subMatchers = [
               SM(
                   name = 'header',
                   startReStr = r"\s*:LABEL[0-9]+: using WIEN2k_(?P<x_wien2k_version>[0-9.]+) \(Release (?P<x_wien2k_release_date>[0-9/.]+)\) in ",
                   sections=["x_wien2k_header"],
                   fixedStartValues={'program_name': 'WIEN2k', 'program_basis_set_type': '(L)APW+lo' }
              ), SM(
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
                      SM(r":GAP  :\s*(?P<x_wien2k_ene_gap_Ry>[-+0-9.]+)\s*Ry\s*=\s*(?P<x_wien2k_ene_gap_eV>[-+0-9.]+)\s*eV\s*.*"),
                      SM(r":FER  : (\w*\s*)*-\s\w*\W\w*\WM\W*=\s*(?P<x_wien2k_fermi_ene>[-+0-9.]+)"),
                      SM(r":MMTOT: TOTAL MAGNETIC MOMENT IN CELL =\s*(?P<x_wien2k_mmtot>[-+0-9.]+)"),
                      SM(r":MMINT: MAGNETIC MOMENT IN INTERSTITIAL =\s*(?P<x_wien2k_mmint>[-+0-9.]+)"),
                      SM(r":MMI001: MAGNETIC MOMENT IN SPHERE 1 =\s*(?P<x_wien2k_mmi001>[-+0-9.]+)"),
                      SM(r":DTO(?P<x_wien2k_atom_nr>[-+0-9]+)[0-9]*:\sTOTAL\s*DIFFERENCE\s*CHARGE\W*\w*\s*IN\s*SPHERE\s*(?P<x_wien2k_sphere_nr>[-+0-9]+)\s*=\s*(?P<x_wien2k_tot_diff_charge>[-+0-9.]+)", repeats = True),
                      SM(r":CTO\s*:\s*\sTOTAL\s*INTERSTITIAL\s*CHARGE=\s*(?P<x_wien2k_tot_int_charge>[-+0-9.]+)"),
                      SM(r":CTO(?P<x_wien2k_atom_nr>[-+0-9]+)[0-9]*:\s*\sTOTAL\s*CHARGE\s*IN\s*SPHERE\s*(?P<x_wien2k_sphere_nr>[-+0-9]+)\s*=\s*(?P<x_wien2k_tot_charge_in_sphere>[-+0-9.]+)",repeats = True),
                      SM(r":ENE\s*:\s*\W*\w*\W*\s*TOTAL\s*ENERGY\s*IN\s*Ry\s*=\s*(?P<x_wien2k_total_ene>[-+0-9.]+)"),
                      SM(r":FOR[0-9]*:\s*(?P<x_wien2k_atom_nr>[0-9]+).ATOM\s*(?P<x_wien2k_for_abs>[0-9.]+)\s*(?P<x_wien2k_for_x>[-++0-9.]+)\s*(?P<x_wien2k_for_y>[-+0-9.]+)\s*(?P<x_wien2k_for_z>[-+0-9.]+)\s*partial\sforces", repeats = True),
                      SM(r":FGL[0-9]*:\s*(?P<x_wien2k_atom_nr>[0-9]+).ATOM\s*(?P<x_wien2k_for_x_gl>[-+0-9.]+)\s*(?P<x_wien2k_for_y_gl>[-+0-9.]+)\s*(?P<x_wien2k_for_z_gl>[-+0-9.]+)\s*partial\sforces", repeats = True)

                  ]
              )
           ]
       )
    ])

# loading metadata from nomad-meta-info/meta_info/nomad_meta_info/fhi_aims.nomadmetainfo.json

parserInfo = {
  "name": "Wien2k"
}

metaInfoPath = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"../../../../nomad-meta-info/meta_info/nomad_meta_info/wien2k.nomadmetainfo.json"))
metaInfoEnv, warnings = loadJsonFile(filePath = metaInfoPath, dependencyLoader = None, extraArgsHandling = InfoKindEl.ADD_EXTRA_ARGS, uri = None)

if __name__ == "__main__":
    superContext = Wien2kContext()
    mainFunction(mainFileDescription, metaInfoEnv, parserInfo, superContext = superContext)
