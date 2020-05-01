from ipykernel.kernelbase import Kernel #kernel base class
import pexpect #for spawning persistent subprocesses
import subprocess #for kernel scripts
import sys #for debugging
import re #for matching tag functions

#extends the ipykernel base class from Jupyter
class MipsKernel(Kernel):
    implementation = 'MIPS'
    implementation_version = '0.1'
    banner = "MIPS Assembly kernel using SPIM."
    language_info = {'name': 'cmake', 'mimetype': 'text/plain', 'extension': '.s'}
    language = 'MIPS32'

    #kernel constructor, runs on kernel initialization
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.c = pexpect.spawnu('spim') #spawns a persistent SPIM subprocess
        self.p = "(spim) " #prompt indicating readiness
        self.c.expect_exact(self.p) #initial scan for input prompt

    #runs on code block execution
    def do_execute(self, code, silent, store_history=True, user_expressions=None, allow_stdin=True):
        if not silent: #if code cell is not empty

            code += "\n" #sanitize input (EOF exception protection)
            if (code[:2] == "#!"): #tag function prefix
                self.parse_directives(code.split("\n", 1)[0], code) #before execution

            f = open(".temp.s", "w")
            f.write(code) #write code block contents to temporary file
            f.close()

            self.noteout("SPIM Output:\n") #preamble message

            self.c.sendline('load ".temp.s"') #send load command to SPIM process
            self.c.expect_exact(self.p) #set marker after prompt
            subprocess.call(['rm', '.temp.s']) #remove temporary file

            feedback = self.c.before.split("\r\n", 1)[-1]
            if (feedback != ""):
                self.noteout(feedback) #if there are errors, show them

            self.c.sendline('run') #send run command
            self.c.expect('run\r\n') #match command to trim it from output
            self.c.expect('.*') #match anything next

            while (self.p not in self.c.after): #if there is no prompt, expect input
                x = self._input_request(self.c.after, self._parent_ident, self._parent_header) #query frontend
                self.c.sendline(x) #send user input
                self.c.expect_exact(x + '\r\n') #match user input to push the buffer forward
                self.c.expect('.*') #reset

            self.noteout(self.c.after[:-7] + "\n") #trim prompt

            self.newline()

            code = code.rstrip('\n') #remove sanitization newline
            if (code.rfind('\n#!') > 0):
                self.parse_directives(code.rsplit("\n", 1)[-1], code) #after execution

        #augment execution count, etc.
        return {'status': 'ok',
                'execution_count': self.execution_count,
                'user_expressions': {}
                }

    #runs on kernel shutdown
    def do_shutdown(self, restart):
        self.c.sendline()
        self.c.sendline('exit') #send exit command
        self.c.kill(1) #attempt to kill subprocess
        return {'status': 'ok',
                'restart': restart
                }

    #parses given comment line for kernel instructions in the form of tag functions
    def parse_directives(self, line, code):
        comms = re.findall("(AUTO|SYM|ALL|RESET|\$[A-Za-z0-9]+|0x[0-9]+)(?=,| |$)", line) #parse valid kernel instructions
        comms = list(dict.fromkeys(comms)) #remove duplicates by converting list to and from dictionary
        for i in comms:
            if (i == "ALL"):
                self.c.sendline('print_all_regs d') #print all registers (argument included for SPIM bug)
                self.c.expect('print_all_regs d\r\n')
                self.c.expect_exact(self.p)
                self.noteout(self.c.before)
            elif (i == "AUTO"): #parses input code for register references and prints them
                found = re.findall("\$[A-Za-z0-9]+(?=,|\n|$)", code)
                found = list(dict.fromkeys(found)) #removes duplicates
                for i in found:
                    self.c.sendline('print ' + i) #print given register
                    self.c.expect_exact(self.p)
                    self.noteout(self.c.before)
                self.newline()
            elif (i == "RESET"):
                self.c.sendline('reinitialize') #clear session memory and registers
                self.c.expect('notice.\r\n')
                self.c.expect_exact(self.p)
                self.noteout("(!) Interpreter reinitialized.\n")
            elif (i == "SYM"):
                self.c.sendline('print_sym') #print global labels
                self.c.expect('print_sym\r\n')
                self.c.expect_exact(self.p)
                self.noteout(self.c.before)
                self.newline()
            elif (i[:1] == "$"): #register prefix
                self.c.sendline('print ' + i) #print given register
                self.c.expect_exact(self.p)
                self.noteout(self.c.before)
                self.newline()
            elif (i[:2] == "0x"): #memory address prefix
                self.c.sendline('print ' + i) #print given memory address contents
                self.c.expect_exact(self.p)
                self.noteout(self.c.before)
                self.newline()

    #prints string to notebook output cell
    def noteout(self, note):
        content = {'name': 'stdout', 'text': note}
        self.send_response(self.iopub_socket, 'stream', content) #final output message

    #prints newline to notebook output cell
    def newline(self):
        content = {'name': 'stdout', 'text': "\n"}
        self.send_response(self.iopub_socket, 'stream', content) #new line

    #prints string to the console running the notebook
    def __debug(self, note):
        sys.__stdout__.write("DEBUG:\n" + note + "\n") #write to terminal stdout
        sys.__stdout__.flush() #show output despite notebook


#initialize
if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=MipsKernel)
