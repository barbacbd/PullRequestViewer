#!/bin/bash
# MIT License
#
# Copyright (c) 2024 Brent Barbachem
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

VenvPath="rh-gather-venv"
PyVersion=`python3 --version | awk '{print $2}'`
MinPythonVersion="3.9.0"
# temporary variable until the pypi package is available
UsePyPi=false
JiraConfig=false
UseConfigFile=false
ConfigFile="config.yaml"
args=()

while getopts c:o:pjh flag
do
    case "${flag}" in
	c)
	    ConfigFile=${OPTARG}
	    UseConfigFile=true
	    ;;
	o) args+=("--output" "${OPTARG}");;
	p) UsePyPi=true;;
	j) args+=("--coordinate_with_jira");;
	h)
	    echo "RH PR Gather"
	    echo ""
	    echo "  -c    ConfigFile:   Supply the full path to the configuration file (yaml)."
	    echo "  -o    OutputFile:   Supply the name of the output file (xlsx)."
	    echo "  -p    UsePyPi:      When applied, the package will be pulled from PyPi."
	    echo "                      Default behavior will pull the latest code from the"
	    echo "                      main branch of the github project."
	    echo "  -j     JiraConfig:  When applied, Jira configuration information will be"
	    echo "                      prompted."
	    echo "  -h     Help"
	    exit 1
    esac
done



if "$UseConfigFile" ; then
    args+=("--input" "$ConfigFile")
else
    args+=("--config")
fi

if [ "$(printf '%s\n' "$MinPythonVersion" "$PyVersion" | sort -V | head -n1)" = "$MinPythonVersion" ]; then 
    echo "Current python version ${PyVersion} is greater than or equal to ${MinPythonVersion}"
else
    echo "ERROR: Python ${PyVersion} is less than minimum python version ${MinPythonVersion}"
fi

# create the virtual environment
python3 -m venv $VenvPath

source $VenvPath/bin/activate

# temporary checks until the pypi package is available
if "$UsePyPi" ; then
    echo "Running the install from PyPi."
    # cover instances where the package may already be installed
    pip install rh_pr_gather --upgrade
else
    echo "Running the install from the latest version of master."
    wget https://github.com/barbacbd/PullRequestViewer/archive/master.tar.gz
    tar -xvzf master.tar.gz
    cd PullRequestViewer-main
    pip install . --upgrade

    cd ..
    echo "Removing the archives."
    rm -rf PullRequestViewer-main
    rm -rf master.tar.gz
fi

# if the output file currently exists then it will be deleted here.
if [ -f "github.xlsx" ]; then
    echo "WARN: github.xlsx exists, the file is going to be removed."
    rm github.xlsx
fi

# supply all of the args (compiled as a list above) to the executable
rh-pr-gather ${args[@]}

deactivate

rm -rf $VenvPath
