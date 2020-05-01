#!/bin/bash

install () {
    mkdir -p ~/.local/share/jupyter/kernels/mips
    kerneljs='{
        "argv": ["'$1'", "-m", "mips_kernel", "-f", "{connection_file}"],
                 "display_name": "MIPS"
    }'

   echo $kerneljs > ~/.local/share/jupyter/kernels/mips/kernel.json
   chmod u+r logo-32x32.png
   chmod u+r logo-64x64.png
   cp logo-32x32.png ~/.local/share/jupyter/kernels/mips
   cp logo-64x64.png ~/.local/share/jupyter/kernels/mips
   echo "Kernel spec generated."
}

pv1=$(python --version 2>&1)
pv2=$(python3 --version 2>&1)
if [[ $pv1 == *"Python 3."* ]] ; then install "python"
elif [[ $pv2 == *"Python 3."* ]] ; then install "python3"
else echo "Python 3.5 or higher is necessary. Install python3."
fi
