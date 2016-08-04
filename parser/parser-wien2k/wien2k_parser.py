from builtins import object
import setup_paths
from nomadcore.simple_parser import mainFunction, AncillaryParser, CachingLevel
from nomadcore.simple_parser import SimpleMatcher as SM
from nomadcore.local_meta_info import loadJsonFile, InfoKindEl
import os, sys, json
import wien2k_parser_struct

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

        structSuperContext = wien2k_parser_struct.Wien2kStructContext()
        structParser = AncillaryParser(
            fileDescription = wien2k_parser_struct.buildStructureMatchers(),
            parser = self.parser,
            cachingLevelForMetaName = wien2k_parser_struct.get_cachingLevelForMetaName(self.metaInfoEnv, CachingLevel.PreOpenedIgnore),
            superContext = structSuperContext)

        mainFile = self.parser.fIn.fIn.name
        fName = mainFile[:-4] + ".struct"
        if os.path.exists(fName):
            with open(fName) as fIn:
                structParser.parseFile(fIn)

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
                      SM(r":NATO :\s*(?P<x_wien2k_number_of_independent_atoms>[0-9]+)INDEPENDENT AND\s*(?P<x_wien2k_total_atoms>[0-9]+)\s*TOTAL ATOMS IN UNITCELL"),
                      SM(r"\s*SUBSTANCE: (?P<x_wien2k_system_name>.*)"),
                      SM(r":POT\s*:\s*POTENTIAL OPTION\s*(?P<x_wien2k_potential_option>[0-9]+)"),
                      SM(r":LAT\s*:\s*LATTICE CONSTANTS=\s*(?P<x_wien2k_lattice_const_a>[0-9.]+)\s*(?P<x_wien2k_lattice_const_b>[0-9.]+)\s*(?P<x_wien2k_lattice_const_c>[0-9.]+)"),
                      SM(r":VOL\s*:\s*UNIT CELL VOLUME\s*=\s*(?P<x_wien2k_unit_cell_volume__angstrom3>[0-9.]+)"),
                      SM(r":ENE  : \W*\w*\W*\TOTAL ENERGY IN Ry =\s*(?P<x_wien2k_total_ene>[-+0-9.]+)")
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
