#!/usr/bin/env python3

import neovim
from neovim import attach
import sys
from threading import Timer
import signal
import os


def dump_and_exit(buffer: neovim.api.Buffer):
    lines = buffer[:]
    for l in lines:
        print(l)
    # buffer[:] = []
    sys.exit(0)


def kill():
    sig = signal.CTRL_C_EVENT if sys.platform == 'win32' else signal.SIGINT
    os.kill(os.getpid(), sig)


def start_timer(timeout=1):
    t = Timer(timeout, kill)
    t.daemon = True
    t.start()


start_timer()

lines = []
for line in sys.stdin:
    lines.append(line.rstrip('\n'))

try:
    with attach('socket', path='/tmp/nvim') as nvim:
        nvim.command('set tw=100 ft=c')
        nvim.current.buffer[:] = lines

        # Find first non-empty line
        first_non_empty_line = (None, None)
        for (i, l) in enumerate(lines):
            if l != '' and not l.isspace():
                first_non_empty_line = (i, l)
                break
        if first_non_empty_line is (None, None):
            # Print and bail
            dump_and_exit(nvim.current.buffer)
        # Check if first_non_empty_line starts with /**
        if first_non_empty_line[1].lstrip().startswith('/**'):
            # Skip
            nvim.command(f"execute 'normal! gg{first_non_empty_line[0] + 1}jVGgq'")
        else:
            nvim.command(f"execute 'normal! ggVGgq'")
        dump_and_exit(nvim.current.buffer)
except IOError:
    sys.exit(1)
