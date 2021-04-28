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
import numpy as np            # pylint: disable=unused-import
import typing                 # pylint: disable=unused-import
from nomad.metainfo import (  # pylint: disable=unused-import
    MSection, MCategory, Category, Package, Quantity, Section, SubSection, SectionProxy,
    Reference
)
from nomad.metainfo.legacy import LegacyDefinition

from nomad.datamodel.metainfo import public

m_package = Package(
    name='wien2k_nomadmetainfo_json',
    description='None',
    a_legacy=LegacyDefinition(name='wien2k.nomadmetainfo.json'))


class x_wien2k_header(MSection):
    '''
    header (labels) of wien2k.
    '''

    m_def = Section(validate=False, a_legacy=LegacyDefinition(name='x_wien2k_header'))

    x_wien2k_release_date = Quantity(
        type=str,
        shape=[],
        description='''
        Release date of wien2k.
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_release_date'))

    x_wien2k_version = Quantity(
        type=str,
        shape=[],
        description='''
        Version of WIEN2k.
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_version'))


class x_wien2k_section_XC(MSection):
    '''
    exchange-correlation potential, in in0
    '''

    m_def = Section(validate=False, a_legacy=LegacyDefinition(name='x_wien2k_section_XC'))

    x_wien2k_indxc = Quantity(
        type=str,
        shape=[],
        description='''
        exchange-correlation potential, in in0
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_indxc'))


class x_wien2k_section_equiv_atoms(MSection):
    '''
    section containing a class of equivalent atoms
    '''

    m_def = Section(validate=False, a_legacy=LegacyDefinition(name='x_wien2k_section_equiv_atoms'))

    x_wien2k_atom_pos_x = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        unit='meter',
        description='''
        position of atom x in internal units
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_atom_pos_x'))

    x_wien2k_atom_pos_y = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        unit='meter',
        description='''
        position of atom y in internal units
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_atom_pos_y'))

    x_wien2k_atom_pos_z = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        unit='meter',
        description='''
        position of atom z  in internal units
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_atom_pos_z'))

    x_wien2k_atom_name = Quantity(
        type=str,
        shape=[],
        description='''
        name of atom, labelling non-equvalent atoms
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_atom_name'))

    x_wien2k_NPT = Quantity(
        type=np.dtype(np.int32),
        shape=[],
        description='''
        number of radial mesh points
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_NPT'))

    x_wien2k_RMT = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        atomic sphere radius (muffin-tin radius)
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_RMT'))

    x_wien2k_R0 = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        first radial mesh point
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_R0'))

    x_wien2k_atomic_number_Z = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        atomic number Z
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_atomic_number_Z'))


class section_run(public.section_run):

    m_def = Section(validate=False, extends_base_section=True, a_legacy=LegacyDefinition(name='section_run'))

    x_wien2k_header = SubSection(
        sub_section=SectionProxy('x_wien2k_header'),
        repeats=True,
        a_legacy=LegacyDefinition(name='x_wien2k_header'))


class section_scf_iteration(public.section_scf_iteration):

    m_def = Section(validate=False, extends_base_section=True, a_legacy=LegacyDefinition(name='section_scf_iteration'))

    x_wien2k_iteration_number = Quantity(
        type=np.dtype(np.int32),
        shape=[],
        description='''
        scf iteration number
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_iteration_number'))

    x_wien2k_nr_of_independent_atoms = Quantity(
        type=int,
        description='''
        number of independent atoms in the cell
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_nr_of_independent_atoms'))

    x_wien2k_potential_option = Quantity(
        type=str,
        shape=[],
        description='''
        exchange correlation potential option
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_potential_option'))

    x_wien2k_system_name = Quantity(
        type=str,
        shape=[],
        description='''
        user given name for this system
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_system_name'))

    x_wien2k_total_atoms = Quantity(
        type=np.dtype(np.int32),
        shape=[],
        description='''
        total number of atoms in the cell
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_total_atoms'))

    x_wien2k_lattice_const_a = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        lattice parameter a in this calculation
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_lattice_const_a'))

    x_wien2k_lattice_const_b = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        lattice parameter b in this calculation
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_lattice_const_b'))

    x_wien2k_lattice_const_c = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        lattice parameter c in this calculation
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_lattice_const_c'))

    x_wien2k_unit_cell_volume_bohr3 = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        unit='bohr ** 3',
        description='''
        unit cell volume
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_unit_cell_volume_bohr3'))

    x_wien2k_spinpolarization = Quantity(
        type=str,
        description='''
        spinpolarization treatment
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_spinpolarization'))

    x_wien2k_noe = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        number of electrons
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_noe'))

    x_wien2k_nr_kpts = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        number of k-points
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_nr_kpts'))

    x_wien2k_cutoff = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        Potential and charge cut-off, Ry**.5
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_cutoff'))

    x_wien2k_ene_gap = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        unit='joule',
        description='''
        energy gap in Ry
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_ene_gap'))

    x_wien2k_ene_gap_eV = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        unit='electron_volt',
        description='''
        energy gap in eV
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_ene_gap_eV'))

    x_wien2k_matrix_size = Quantity(
        type=np.dtype(np.int32),
        shape=[],
        description='''
        matrix size
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_matrix_size'))

    x_wien2k_rkm = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        rkm
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_rkm'))

    x_wien2k_LOs = Quantity(
        type=np.dtype(np.int32),
        shape=[],
        description='''
        LOs
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_LOs'))

    x_wien2k_mmtot = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        total magnetic moment in cell
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_mmtot'))

    x_wien2k_mmint = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        magnetic moment in the interstital region
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_mmint'))

    x_wien2k_mmi = Quantity(
        type=np.dtype(np.float64),
        shape=['x_wien2k_nr_of_independent_atoms'],
        description='''
        magnetic moment inside the sphere
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_mmi'))

    x_wien2k_mmi001 = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        magnetic moment inside the sphere
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_mmi001'))

    x_wien2k_charge_distance = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        charge distance between last 2 iterations
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_charge_distance'))

    x_wien2k_for_abs = Quantity(
        type=np.dtype(np.float64),
        shape=['x_wien2k_nr_of_independent_atoms'],
        description='''
        force on atom xx in mRy/bohr (in the local (for each atom) cartesian coordinate
        system): |F|
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_for_abs'))

    x_wien2k_for = Quantity(
        type=np.dtype(np.float64),
        shape=['x_wien2k_nr_of_independent_atoms', 3],
        description='''
        forces on inequivalent atoms in mRy/bohr (in the local (for each atom) cartesian coordinate
        system)
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_for'))

    x_wien2k_for_x = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        force on atom xx in mRy/bohr (in the local (for each atom) cartesian coordinate
        system): Fx
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_for_x'))

    x_wien2k_for_y = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        force on atom xx in mRy/bohr (in the local (for each atom) cartesian coordinate
        system): Fy
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_for_y'))

    x_wien2k_for_z = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        force on atom xx in mRy/bohr (in the local (for each atom) cartesian coordinate
        system): Fz
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_for_z'))

    x_wien2k_for_gl = Quantity(
        type=np.dtype(np.float64),
        shape=['x_wien2k_nr_of_independent_atoms', 3],
        description='''
        force on inequivalent atoms (in the global coordinate system of the unit cell (in
        the same way as the atomic positions are specified))
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_for_gl'))

    x_wien2k_for_x_gl = Quantity(
        type=np.dtype(np.float64),
        shape=['x_wien2k_nr_of_independent_atoms'],
        description='''
        force on inequivalent atom xx (in the global coordinate system of the unit cell (in
        the same way as the atomic positions are specified)): Fx
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_for_x_gl'))

    x_wien2k_for_y_gl = Quantity(
        type=np.dtype(np.float64),
        shape=['x_wien2k_nr_of_independent_atoms'],
        description='''
        force on inequivalent atom xx in (in the global coordinate system of the unit cell (in
        the same way as the atomic positions are specified)): Fy
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_for_y_gl'))

    x_wien2k_for_z_gl = Quantity(
        type=np.dtype(np.float64),
        shape=['x_wien2k_nr_of_independent_atoms'],
        description='''
        force on inequivalent atom xx in (in the global coordinate system of the unit cell (in
        the same way as the atomic positions are specified)): Fz
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_for_z_gl'))

    x_wien2k_atom_nr = Quantity(
        type=str,
        shape=[],
        description='''
        number of atom, labelling atoms
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_atom_nr'))

    x_wien2k_atom_mult = Quantity(
        type=np.dtype(np.int32),
        shape=['x_wien2k_nr_of_independent_atoms'],
        description='''
        atom multiplicity
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_atom_mult'))

    x_wien2k_sphere_nr = Quantity(
        type=str,
        shape=[],
        description='''
        number of sphere, labelling spheres
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_sphere_nr'))

    x_wien2k_tot_diff_charge = Quantity(
        type=np.dtype(np.float64),
        shape=['x_wien2k_nr_of_independent_atoms'],
        description='''
        total difference charge density for atom xx between last 2 iterations
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_tot_diff_charge'))

    x_wien2k_tot_int_charge = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        total interstitial charge (mixed after MIXER)
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_tot_int_charge'))

    x_wien2k_tot_charge_in_sphere = Quantity(
        type=np.dtype(np.float64),
        shape=['x_wien2k_nr_of_independent_atoms'],
        description='''
        total charge in sphere xx (mixed after MIXER)
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_tot_charge_in_sphere'))

    x_wien2k_tot_int_charge_nm = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        total interstitial charge (new (not mixed) from LAPW2+LCORE
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_tot_int_charge_nm'))

    x_wien2k_tot_charge_in_sphere_nm = Quantity(
        type=np.dtype(np.float64),
        shape=['x_wien2k_nr_of_independent_atoms'],
        description='''
        total charge in sphere xx (new (not mixed) from LAPW2+LCORE
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_tot_charge_in_sphere_nm'))

    x_wien2k_tot_val_charge_cell = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        total valence charge inside unit cell
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_tot_val_charge_cell'))

    x_wien2k_tot_val_charge_sphere = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        total valence charge in sphere xx
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_tot_val_charge_sphere'))

    x_wien2k_density_at_nucleus_valence = Quantity(
        type=np.dtype(np.float64),
        shape=['x_wien2k_nr_of_independent_atoms'],
        description='''
        density for atom xx at the nucleus (first radial mesh point); valence
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_density_at_nucleus_valence'))

    x_wien2k_density_at_nucleus_semicore = Quantity(
        type=np.dtype(np.float64),
        shape=['x_wien2k_nr_of_independent_atoms'],
        description='''
        density for atom xx at the nucleus (first radial mesh point); semi-core
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_density_at_nucleus_semicore'))

    x_wien2k_density_at_nucleus_core = Quantity(
        type=np.dtype(np.float64),
        shape=['x_wien2k_nr_of_independent_atoms'],
        description='''
        density for atom xx at the nucleus (first radial mesh point); core
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_density_at_nucleus_core'))

    x_wien2k_density_at_nucleus_tot = Quantity(
        type=np.dtype(np.float64),
        shape=['x_wien2k_nr_of_independent_atoms'],
        description='''
        density for atom xx at the nucleus (first radial mesh point); total
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_density_at_nucleus_tot'))

    x_wien2k_nuclear_charge = Quantity(
        type=np.dtype(np.float64),
        shape=['x_wien2k_nr_of_independent_atoms'],
        description='''
        nuclear and electronic charge; normalization check of electronic charge densities.
        If a significant amount of electrons is missing, one might have core states, whose
        charge density is not completely confined within the respective atomic sphere. In
        such a case the corresponding states should be treated as band states (using LOs).
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_nuclear_charge'))

    x_wien2k_electronic_charge = Quantity(
        type=np.dtype(np.float64),
        shape=['x_wien2k_nr_of_independent_atoms'],
        description='''
        nuclear and electronic charge; normalization check of electronic charge densities.
        If a significant amount of electrons is missing, one might have core states, whose
        charge density is not completely confined within the respective atomic sphere. In
        such a case the corresponding states should be treated as band states (using LOs).
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_electronic_charge'))

    x_wien2k_necnr = Quantity(
        type=np.dtype(np.int32),
        shape=[],
        description='''
        number of the nec test, labelling nec
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_necnr'))


class section_system(public.section_system):

    m_def = Section(validate=False, extends_base_section=True, a_legacy=LegacyDefinition(name='section_system'))

    x_wien2k_nonequiv_atoms = Quantity(
        type=np.dtype(np.int32),
        shape=[],
        description='''
        number of inequivalent atoms in the unit cell
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_nonequiv_atoms'))

    x_wien2k_system_nameIn = Quantity(
        type=str,
        shape=[],
        description='''
        user given name for this system given in the struct file
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_system_nameIn'))

    x_wien2k_calc_mode = Quantity(
        type=str,
        shape=[],
        description='''
        relativistic or nonrelativistic calculation mode
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_calc_mode'))

    x_wien2k_unit_cell_param_a = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        unit='meter',
        description='''
        unit cell parameters - a
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_unit_cell_param_a'))

    x_wien2k_unit_cell_param_b = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        unit='meter',
        description='''
        unit cell parameters - b
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_unit_cell_param_b'))

    x_wien2k_unit_cell_param_c = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        unit='meter',
        description='''
        unit cell parameters - c
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_unit_cell_param_c'))

    x_wien2k_angle_between_unit_axis_alfa = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        unit cell parameters - alfa
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_angle_between_unit_axis_alfa'))

    x_wien2k_angle_between_unit_axis_beta = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        unit cell parameters - beta
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_angle_between_unit_axis_beta'))

    x_wien2k_angle_between_unit_axis_gamma = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        unit cell parameters - gamma
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_angle_between_unit_axis_gamma'))

    x_wien2k_section_equiv_atoms = SubSection(
        sub_section=SectionProxy('x_wien2k_section_equiv_atoms'),
        repeats=True,
        a_legacy=LegacyDefinition(name='x_wien2k_section_equiv_atoms'))


class section_method(public.section_method):

    m_def = Section(validate=False, extends_base_section=True, a_legacy=LegacyDefinition(name='section_method'))

    x_wien2k_switch = Quantity(
        type=str,
        shape=[],
        description='''
        switch in in0 between TOT, KXC, POT, MULT, COUL, EXCH
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_switch'))

    x_wien2k_ifft = Quantity(
        type=np.dtype(np.int32),
        shape=[3],
        description='''
        FFT-mesh parameters in x direction for the calculation of the XC-potential in the
        interstitial region, in in0
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_ifft'))

    x_wien2k_ifft_x = Quantity(
        type=np.dtype(np.int32),
        shape=[],
        description='''
        FFT-mesh parameters in x direction for the calculation of the XC-potential in the
        interstitial region, in in0
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_ifft_x'))

    x_wien2k_ifft_y = Quantity(
        type=np.dtype(np.int32),
        shape=[],
        description='''
        FFT-mesh parameters in y direction for the calculation of the XC-potential in the
        interstitial region, in in0
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_ifft_y'))

    x_wien2k_ifft_z = Quantity(
        type=np.dtype(np.int32),
        shape=[],
        description='''
        FFT-mesh parameters in z direction for the calculation of the XC-potential in the
        interstitial region, in in0
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_ifft_z'))

    x_wien2k_ifft_factor = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        Multiplicative factor to the IFFT grid, in in0
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_ifft_factor'))

    x_wien2k_iprint = Quantity(
        type=np.dtype(np.int32),
        shape=[],
        description='''
        optional print switch, in in0
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_iprint'))

    x_wien2k_wf_switch = Quantity(
        type=str,
        shape=[],
        description='''
        wave function switch between WFFIL, SUPWF, WPPRI
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_wf_switch'))

    x_wien2k_rkmax = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        RmtKmax - determines matrix size (convergence), where Kmax is the plane wave cut-
        off, Rmt is the smallest of all atomic sphere radii
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_rkmax'))

    x_wien2k_in2_switch = Quantity(
        type=str,
        shape=[],
        description='''
        switch, in in2 between (TOT,FOR,QTL,EFG,ALM,CLM,FERMI)
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_in2_switch'))

    x_wien2k_in2_emin = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        lower energy cut-off for defining the range of occupied states; in in2
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_in2_emin'))

    x_wien2k_in2_ne = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        number of electrons (per unit cell) in given energy range in in2
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_in2_ne'))

    x_wien2k_in2_espermin = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        LAPW2 tries to find the .mean. energies for each l channel, for both the valence
        and the semicore states. To define .valence. and .semicore. it starts at (EF -
        .esepermin.) and searches for a .gap. with a width of at least .eseper0. and
        defines this as separation energy of valence and semicore; in in2
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_in2_espermin'))

    x_wien2k_in2_esper0 = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        minimum gap width; in in2
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_in2_esper0'))

    x_wien2k_smearing_kind = Quantity(
        type=str,
        shape=[],
        description='''
        determines how EF is determined; in in2
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_smearing_kind'))

    x_wien2k_in2_gmax = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        max. G (magnitude of largest vector) in charge density Fourier expansion; in in2
        ''',
        a_legacy=LegacyDefinition(name='x_wien2k_in2_gmax'))

    x_wien2k_section_XC = SubSection(
        sub_section=SectionProxy('x_wien2k_section_XC'),
        repeats=True,
        a_legacy=LegacyDefinition(name='x_wien2k_section_XC'))


m_package.__init_metainfo__()
