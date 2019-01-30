/*
 * Copyright 2016-2018 Daria Tomecka, Fawzi Mohamed
 * 
 *   Licensed under the Apache License, Version 2.0 (the "License");
 *   you may not use this file except in compliance with the License.
 *   You may obtain a copy of the License at
 * 
 *     http://www.apache.org/licenses/LICENSE-2.0
 * 
 *   Unless required by applicable law or agreed to in writing, software
 *   distributed under the License is distributed on an "AS IS" BASIS,
 *   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *   See the License for the specific language governing permissions and
 *   limitations under the License.
 */

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
  mainFileRe = """:ITE[0-9]+:  1. ITERATION""".r,
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
    "nomad_meta_info/meta.nomadmetainfo.json",
    "nomad_meta_info/wien2k.nomadmetainfo.json"
  ) ++ DefaultPythonInterpreter.commonFiles(),
  dirMap = Map(
    "parser-wien2k" -> "parsers/wien2k/parser/parser-wien2k",
    "nomad_meta_info" -> "nomad-meta-info/meta_info/nomad_meta_info",
    "python" -> "python-common/common/python/nomadcore"
  ) ++ DefaultPythonInterpreter.commonDirMapping(),
  metaInfoEnv = Some(lab.meta.KnownMetaInfoEnvs.wien2k)
)
