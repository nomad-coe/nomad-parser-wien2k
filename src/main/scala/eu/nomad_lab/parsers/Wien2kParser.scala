package eu.nomad_lab.parsers

import eu.nomad_lab
import eu.nomad_lab.DefaultPythonInterpreter
import org.{ json4s => jn }
import eu.{ nomad_lab => lab }
import scala.collection.breakOut

object Wien2kParser extends SimpleExternalParserGenerator(
  name = "Wien2kParser",
  parserInfo = jn.JObject(
    ("name" -> jn.JString("Wien2k")) ::
      ("parserId" -> jn.JString("Wien2k" + lab.Wien2kVersionInfo.version)) ::
      ("versionInfo" -> jn.JObject(
        ("nomadCoreVersion" -> jn.JObject(lab.NomadCoreVersionInfo.toMap.map {
          case (k, v) => k -> jn.JString(v.toString)
        }(breakOut): List[(String, jn.JString)])) ::
          (lab.Wien2kVersionInfo.toMap.map {
            case (key, value) =>
              (key -> jn.JString(value.toString))
          }(breakOut): List[(String, jn.JString)])
      )) :: Nil
  ),
  mainFileTypes = Seq("text/.*"),
  mainFileRe = """:LABEL[0-9]+: using WIEN2k_(?<version>[0-9.]+) \(Release (?<release>[0-9/.]+)\) in """.r,
  cmd = Seq(DefaultPythonInterpreter.pythonExe(), "${envDir}/parsers/wien2k/parser/parser-wien2k/wien2k_parser.py",
    "--uri", "${mainFileUri}", "${mainFilePath}"),
  resList = Seq(
    "parser-wien2k/wien2k_parser.py",
    "parser-wien2k/wien2k_parser_in0.py",
    "parser-wien2k/wien2k_parser_in1c.py",
    "parser-wien2k/wien2k_parser_in2c.py",
    "parser-wien2k/wien2k_parser_in1.py",
    "parser-wien2k/wien2k_parser_in2.py",
    "parser-wien2k/wien2k_parser_struct.py",
    "parser-wien2k/setup_paths.py",
    "nomad_meta_info/public.nomadmetainfo.json",
    "nomad_meta_info/common.nomadmetainfo.json",
    "nomad_meta_info/meta_types.nomadmetainfo.json",
    "nomad_meta_info/wien2k.nomadmetainfo.json"
  ) ++ DefaultPythonInterpreter.commonFiles(),
  dirMap = Map(
    "parser-wien2k" -> "parsers/wien2k/parser/parser-wien2k",
    "nomad_meta_info" -> "nomad-meta-info/meta_info/nomad_meta_info",
    "python" -> "python-common/common/python/nomadcore"
  ) ++ DefaultPythonInterpreter.commonDirMapping(),
  metaInfoEnv = Some(lab.meta.KnownMetaInfoEnvs.wien2k)
)
