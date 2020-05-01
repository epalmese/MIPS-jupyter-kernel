# MIPS Jupyter Kernel

This kernel uses **python3** to interface with the MIPS assembly interpreter SPIM from a Jupyter notebook.

## Setup:

- Install the MIPS interpreter SPIM with `sudo apt-get install spim`.

- Install Jupyter Lab with `pip install jupyterlab`, or the package manager of your choice (`pip3`, `conda`, etc.).

- Navigate to the **kernel** folder in this repository and run `./install_kernel.sh` (you may need to add permissions) to generate a kernel spec file and folder.

- From **/kernel**, run `jupyter lab` (or `notebook`) and select the MIPS kernel option to open a new MIPS notebook using the provided kernel module.

## Usage:

### Running code:

- Execute MIPS code by running code cells. Output will be displayed under the cell.

- User input is also taken under the cell.

### Debugging:

Syntax and labeling errors will be shown after code cell execution. The first and last line of a cell can contain commands to assist debugging, run before and/or after execution respectively:

- `#!RESET` will reinitialize the MIPS interpreter to start a new session with clean registers and memory. For example, you may wish to include this at the top of each cell that precedes a new program.

- `#!AUTO` will scan your code cell for register references and show the contents of the detected registers.

- `#!ALL` will show the contents of every register available.

- `#!SYM` will show the names and addresses of all global labels.

- `#!$reg, reg, ...` will show the contents of given registers. For example: `#!$v0, $a0, $ra` will show registers `v0`, `a0`, and `ra`.

- `#!0xaddress, ...` will show the contents of a given memory address. For example: `#!0x00400024` will show what instruction is in that address.

These commands can be combined (as in `#!AUTO, SYM, RESET`) and will be executed in the stated order.

Examples can be seen in the `test.ipynb` notebook file [here](kernel/test.ipynb) (relative link).
