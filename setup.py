# Copyright 2015-2018 Lorenzo Pardini
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from setuptools import setup, find_packages


def main():
    setup(
        name='wien2kparser',
        version='0.1',
<<<<<<< HEAD
        description='NOMAD parser implementation for Exciting.',
        license='APACHE 2.0',
        package_dir={'': 'parser/parser-wien2k'},
        packages=find_packages('parser/parser-wien2k'),
=======
        description='NOMAD parser implementation for Wien2k.',
        license='APACHE 2.0',
        package_dir={'': 'parser'},
        packages=find_packages('parser'),
>>>>>>> 45edbd908359cbb40b004309010e2487a8ffbb7c
        install_requires=[
            'nomadcore'
        ],
    )


if __name__ == '__main__':
    main()