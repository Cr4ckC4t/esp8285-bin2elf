#!/usr/bin/env python3

import argparse
import sys
from bin_utils import BINReader, ELFBuilder, ELFSegment

def parse_header(elf, bin):
	elf.magic = bin.getByte()
	elf.n_segments = bin.getByte()
	elf.flash_mode = bin.getByte()
	flash_freq_size = bin.getByte()
	elf.flash_freq = flash_freq_size & 0x0f
	elf.flash_size = flash_freq_size >> 4 & 0x0f
	elf.entry_addr = bin.getWordLE()

def parse_segments(elf, bin, segments):
	for segment in segments:
		s = ELFSegment()
		s.addr = bin.getWordLE()
		s.size = bin.getWordLE()
		s.raw = bin.getBytesRaw(s.size)
		elf.segments[segment] = s

def parse_trailer(elf, bin, to_offset=0):
	# discard zero padding
	while((checksum := bin.getByte()) == 0x00):
		pass

	# get checksum even though we won't use it
	elf.checksum = checksum

	# discard bootloader padding (0xAA)
	if to_offset != 0:
		_ = bin.getBytesRaw(to_offset-bin.offset)

# Reversing the logic from write_bin of elf2bin.py
def parse_mem(mem):
	bin = BINReader(mem)
	eboot = ELFBuilder('Bootloader')
	app = ELFBuilder('Application')

	# parse bootloader
	parse_header(eboot, bin)
	parse_segments(eboot, bin, ['.text', '.rodata'])
	parse_trailer(eboot, bin, 4096)

	print(eboot)

	# parse application
	parse_header(app, bin)
	parse_segments(app, bin, ['.irom0.text', '.text', '.text1', '.data', '.rodata'])
	parse_trailer(app, bin)

	print(app)

	app.convertToElf('app.elf')


def main():
	parser = argparse.ArgumentParser(description='Create ELF file from ESP8266/ESP285 flashdump')
	parser.add_argument('-f', '--flashdump', action='store', required=True, help='ESP8266 flashdump')

	args = parser.parse_args()

	try:
		with open(args.flashdump, 'rb') as f:
			mem = f.read()

	except Exception as e:
		print(f'Failed to read {args.flashdump}: {e}')
		return 1

	try:
		parse_mem(mem)
	except Exception as e:
		print(f'Failed to parse contents of {args.flashdump}: {e}')
		return 1

	return 0



if __name__ == '__main__':
	sys.exit(main())
