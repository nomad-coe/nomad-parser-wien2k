#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
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

import pytest
import numpy as np

from nomad.datamodel import EntryArchive
from wien2kparser import Wien2kParser


def approx(value, abs=0, rel=1e-6):
    return pytest.approx(value, abs=abs, rel=rel)


@pytest.fixture(scope='module')
def parser():
    return Wien2kParser()


def test_single_point(parser):
    archive = EntryArchive()
    parser.parse('tests/data/basic/ok.scf', archive, None)

    sec_run = archive.section_run[0]
    assert sec_run.program_version == '12.1 22/7/2012'
    assert sec_run.time_run_date_start.magnitude == 1397313280.0

    sec_method = archive.section_run[0].section_method[0]
    assert sec_method.section_XC_functionals[1].XC_functional_name == 'GGA_C_PBE_SOL'
    assert sec_method.x_wien2k_ifft[1] == 120
    assert sec_method.x_wien2k_rkmax[2] == 4
    assert sec_method.smearing_kind == 'tetrahedra'
    assert sec_method.x_wien2k_in2_espermin == 0.50

    sec_scc = archive.section_run[0].section_single_configuration_calculation[0]
    assert sec_scc.energy_total.magnitude == approx(-8.09654094e-15)
    assert np.shape(sec_scc.atom_forces) == (49, 3)
    assert sec_scc.atom_forces[19][1].magnitude == approx(-2.76650574e-10)
    assert sec_scc.energy_reference_fermi[0].magnitude == approx(-4.46784636e-19)
    sec_scfs = sec_scc.section_scf_iteration
    assert len(sec_scfs) == 40
    assert sec_scfs[21].energy_total_scf_iteration.magnitude == approx(-8.09654095e-15)
    assert sec_scfs[6].x_wien2k_noe == 196.000
    assert sec_scfs[17].x_wien2k_tot_diff_charge[9] == approx(0.0001539)

    sec_system = archive.section_run[0].section_system[0]
    assert np.shape(sec_system.atom_positions) == (49, 3)
    assert sec_system.atom_positions[18][1].magnitude == approx(9.94126646e-10)
    assert sec_system.lattice_vectors[1][1].magnitude == approx(1.06500038e-09)
    assert sec_system.atom_labels == ['C'] * 49


def test_eigenvalues(parser):
    archive = EntryArchive()
    parser.parse('tests/data/eigenvalues/64k_8Rk_mBJkol.scf', archive, None)

    sec_eigenvalues = archive.section_run[0].section_single_configuration_calculation[0].section_eigenvalues[0]
    assert np.shape(sec_eigenvalues.eigenvalues_values) == (1, 8, 315)
    assert np.shape(sec_eigenvalues.eigenvalues_kpoints) == (8, 3)
    assert sec_eigenvalues.eigenvalues_values[0][2][31].magnitude == approx(-2.98121062e-18)
    assert sec_eigenvalues.eigenvalues_kpoints[7][0] == 0.375
    assert sec_eigenvalues.eigenvalues_kpoints_multiplicity[6] == 8

    sec_dos = archive.section_run[0].section_single_configuration_calculation[0].dos_electronic[0]
    assert np.shape(sec_dos.dos_total[0].dos_values) == (1251,)
    assert len(sec_dos.dos_energies) == 1251
    assert sec_dos.dos_total[0].dos_values[1178] == approx(5.93635529e+19)
    assert sec_dos.dos_energies[285].magnitude == approx(-9.37345115e-19)


def test_dos(parser):
    archive = EntryArchive()
    parser.parse('tests/data/dos/CrO2-sp.scf', archive, None)

    # eigenvalues are problematic as shape is not homogenously

    sec_dos = archive.section_run[0].section_single_configuration_calculation[0].dos_electronic[0]
    assert np.shape(sec_dos.dos_total[1].dos_values) == (1000,)
    assert sec_dos.dos_energies[26].magnitude == approx(-9.76582818e-19)
    assert sec_dos.dos_total[1].dos_values[334] == approx(1.32586595e+19)

    assert np.shape(sec_dos.dos_species_projected[1].dos_values) == (1000,)
    assert sec_dos.dos_species_projected[1].dos_values[926] == approx(1.20913559e+18)
