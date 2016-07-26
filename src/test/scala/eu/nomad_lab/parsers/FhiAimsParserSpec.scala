package eu.nomad_lab.parsers

import org.specs2.mutable.Specification

object Wien2kTests extends Specification {
  "Wien2kParserTest" >> {
    "test with json-events" >> {
      ParserRun.parse(Wien2kParser, "parsers/wien2k/test/examples/ok/ok.scf", "json-events") must_== ParseResult.ParseSuccess
    }
    "test with json" >> {
      ParserRun.parse(Wien2kParser, "parsers/wien2k/test/examples/ok/ok.scf", "json") must_== ParseResult.ParseSuccess
    }
  }
}
