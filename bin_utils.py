from ProgramHeader import ProgramHeaderTable
from SectionHeader import SectionHeaderTable, StringTable, SHFlags
from ELFHeader import ELFHeader
from SymbolTable import SymbolTable

class ELFSegment():
	def __init__(self):
		self.size = 0x00
		self.addr = 0x00
		self.raw = None


class ELFBuilder():
	def __init__(self, name):
		self.name = name
		self.magic = 0x00
		self.n_segments = 0x00
		self.flash_mode = 0x00
		self.flash_freq = 0x00
		self.flash_size = 0x00
		self.entry_addr = 0x00

		self.segments = {}
		self.checksum = 0x00


		# app ELF # TODO maybe decapsulate from boot elf later
		self.offset = 0x00
		self.ALIGN = 0x1000

		self.elf_header = ELFHeader()
		self.pht = ProgramHeaderTable(default_type = 0x1, default_align = self.ALIGN)
		self.sht = SectionHeaderTable()
		self.symtab = SymbolTable()
		self.shstrtab = StringTable()

		self.sections = []

	def __str__(self):
		# taken from elf2bin.py
		self.fmodeb = { 3:'dout', 2:'dio', 1:'qout', 0:'qio' }
		self.ffreqb = { 0:'40', 1:'26', 2:'20', 15:'80' }
		self.fsizeb = { 0:'512K', 1:'256K', 2:'1M', 3:'2M', 4:'4M', 8:'8M', 9:'16M' }

		repr = f'ELF Header ({self.name}):\n'
		repr += f'\tMagic: {self.magic:02X}\n'
		repr += f'\tSegments: {self.n_segments}\n'
		repr += f'\tFlash Mode: {self.fmodeb[self.flash_mode]}\n'
		repr += f'\tFlash Frequency: {self.ffreqb[self.flash_freq]}\n'
		repr += f'\tFlash Size: {self.fsizeb[self.flash_size]}\n'
		repr += f'\tEntry Address: {hex(self.entry_addr)}\n'
		repr += f'\tBinary Checksum: {self.checksum:02X}\n'
		repr += f'ELF Segments:\n'
		for segment in self.segments:
			repr += f'\t{segment}:\n'
			repr += f'\t\tAddress: {hex(self.segments[segment].addr)}\n'
			repr += f'\t\tSize: {hex(self.segments[segment].size)}\n'

		return repr

	def convertToElf(self, outfile):
		# this is tailored to the app created by elf2bin.py
		# this will fail when trying to create the eboot.elf
		if self.name != 'Application':
			print('Converting bin to elf is currently only implemented for the application.')
			return
		else:
			print(f'Converting app to ELF')

		# update ELF header
		self.elf_header.updateEntryAddress(self.entry_addr)

		# build program header table
		# https://docs.oracle.com/cd/E19683-01/816-1386/chapter6-83432/index.html
		print(f'Assemble program header table')

		# .padding
		self.pht.addHeader('.padding')

		# .data (.data .noinit .rodata) - .noinit seems to be empty space between the two sections
		self.pht.addHeader('.data',
			vaddr = self.segments['.data'].addr,
			paddr = self.segments['.data'].addr,
			flags = 'PF_RW'
		)

		# ignoring .bss for now (TODO - check later if that's needed)
		# turns out it doesn't hurt to bad if that's missing

		# .text (.text .text1)
		self.pht.addHeader('.text',
			vaddr = self.segments['.text'].addr,
			paddr = self.segments['.text'].addr,
			flags = 'PF_RX'
		)

		# .irom0.text
		self.pht.addHeader('.irom0.text',
			vaddr = self.segments['.irom0.text'].addr,
			paddr = self.segments['.irom0.text'].addr,
			flags = 'PF_RWX'
		)


		# build section header table
		print(f'Assemble section header table')

		# mandatory null section
		self.sht.addSection('.null', self.shstrtab.get(''))

		shf = SHFlags()
		# size and offset will be added when the section contents are actually written
		self.sht.addSection('.data',
			name = self.shstrtab.get('.data'),
			type = 'SHT_PROGBITS',
			flags = shf.WRITE | shf.ALLOC,
			addr = self.segments['.data'].addr,
			addralign = 0x10
		)
		self.sht.addSection('.text',
			name = self.shstrtab.get('.text'),
			type = 'SHT_PROGBITS',
			flags = shf.ALLOC | shf.EXECINSTR,
			addr = self.segments['.text'].addr,
			addralign = 0x4
		)
		self.sht.addSection('.irom0.text',
			name = self.shstrtab.get('.irom0.text'),
			type = 'SHT_PROGBITS',
			flags = shf.ALLOC | shf.EXECINSTR | shf.WRITE,
			addr = self.segments['.irom0.text'].addr,
			addralign = 0x10
		)
		self.sht.addSection('.text1',
			name = self.shstrtab.get('.text1'),
			type = 'SHT_PROGBITS',
			flags = shf.ALLOC | shf.EXECINSTR,
			addr = self.segments['.text1'].addr,
			addralign = 0x04
		)
		self.sht.addSection('.rodata',
			name = self.shstrtab.get('.rodata'),
			type = 'SHT_PROGBITS',
			flags = shf.ALLOC,
			addr = self.segments['.rodata'].addr,
			addralign = 0x10
		)

		self.sht.addSection('.symtab',
			name = self.shstrtab.get('.symtab'),
			type = 'SHT_SYMTAB',
			addralign = 0x4,
			entsize = 0x10
			# link = 0 since we don't use string table
		)


		# This should be the last section, so we can get the SHSTRNDX easy later
		self.sht.addSection('.shstrtab',
			name = self.shstrtab.get('.shstrtab'),
			type = 'SHT_STRTAB',
			addralign = 0x1
		)


		# update ELF Header
		self.elf_header.updatePHNum(len(self.pht.entries))
		self.elf_header.updateSHEntSize(0x28)

		print(f'Assemble sections')

		# create sections
		self.offset = self.elf_header.getSize() + self.pht.getSize()

		# .padding
		self.pht.entries['.padding'].p_offset = self.offset

		# .data
		self.alignSegmentOffset(self.pht.entries['.data'])
		size = self.addSegment(['.data', '.rodata'])
		# TODO: figure out how .noinit size is calculated and add that.. don't know if it's important
		self.pht.entries['.data'].p_filesz = size
		self.pht.entries['.data'].p_memsz = size

		# .text
		self.alignSegmentOffset(self.pht.entries['.text'])
		size = self.addSegment(['.text', '.text1'])
		self.pht.entries['.text'].p_filesz = size
		self.pht.entries['.text'].p_memsz = size

		# .irom0.text
		self.alignSegmentOffset(self.pht.entries['.irom0.text'])
		size = self.addSegment(['.irom0.text'])
		self.pht.entries['.irom0.text'].p_filesz = size
		self.pht.entries['.irom0.text'].p_memsz = size

		# build symbol table
		self.symtab.addSymbol('.STN_UNDEF')
		self.symtab.addSymbol('.data',
			addr = self.segments['.data'].addr,
			info = 0x3, # weak, global
		)
		self.symtab.addSymbol('.text',
			addr = self.segments['.text'].addr,
			info = 0x3, # weak, global
		)
		self.symtab.addSymbol('.text1',
			addr = self.segments['.text1'].addr,
			info = 0x3, # weak, global
		)
		self.symtab.addSymbol('.irom0.text',
			addr = self.segments['.irom0.text'].addr,
			info = 0x3, # weak, global
		)
		self.symtab.addSymbol('.rodata',
			addr = self.segments['.rodata'].addr,
			info = 0x3, # weak, global
		)

		self.alignSectionOffset(self.sht.entries['.symtab'])
		self.addSectionContent('.symtab', self.symtab.finalize())

		# string tables
		self.addSectionContent('.shstrtab', self.shstrtab.finalize())

		print(f'Assemble ELF structure')

		self.elf_header.updateSHStrNdx(len(self.sht.entries)-1)
		self.elf_header.updateSHNum(len(self.sht.entries))
		self.elf_header.updateSHOffset(self.offset)

		elf_raw = []
		elf_raw += self.elf_header.finalize()
		elf_raw += self.pht.finalize()
		elf_raw += self.sections
		elf_raw += self.sht.finalize()

		print(f'Writing ELF to: {outfile}')

		n = 0
		for c in elf_raw:
			n+=1
			if type(c) != type(1):
				print(f'{n}: {c[0]:02x}')

		with open(outfile, 'wb+') as f:
			f.write(bytes(elf_raw))

	def addSegment(self, sectionnames):
		# we assume an aligned position for this segment
		segmentStart = self.offset
		# for all sections that shall be added in this segment:
		for i in range(len(sectionnames)):
			# write raw content
			raw = list(self.segments[sectionnames[i]].raw)
			self.addSectionContent(sectionnames[i],raw)
			# if there are more sections, align them accordingly
			if i<(len(sectionnames)-1):
				self.alignSectionOffset(self.sht.entries[sectionnames[i+1]])
		return self.offset - segmentStart


	def addSectionContent(self, name, data):
		self.sht.entries[name].sh_offset = self.offset
		self.sections += data
		self.offset += len(data)
		self.sht.entries[name].sh_size = len(data)

	def alignSegmentOffset(self, nextSegment):
		# align to page size
		while (self.offset % self.ALIGN):
			self.sections += [0x00]
			self.offset += 1

		# align PHT Entry (vaddr must be equal offset % p_align)
		while ((self.offset % nextSegment.p_align) != (nextSegment.p_vaddr % nextSegment.p_align)):
			self.sections += [0x00]
			self.offset += 1


	def alignSectionOffset(self, nextSection):
		# align section
		while ((self.offset % nextSection.sh_addralign) != (nextSection.sh_addr % nextSection.sh_addralign)):
			self.sections += [0x00]
			self.offset += 1


class BINReader():
	def __init__(self, mem):
		self.bin = mem
		self.len = len(mem)
		self.offset = 0

	# get n bytes - without boundary checks for now
	def getBytesRaw(self, n):
		self.offset += n
		return bytes(self.bin[self.offset-n:self.offset])

	# wrapper for LE
	def getBytesLE(self, n):
		return int.from_bytes(self.getBytesRaw(n)[::-1])

	# wrapper for BE
	def getBytesBE(self, n):
		return int.from_bytes(self.getBytesRaw(n))

	# wrapper for n=1
	def getByte(self):
		return self.getBytesLE(1)

	# wrapper for n=2
	def getHalfWordLE(self):
		return self.getBytesLE(2)

	# wrapper for n=4
	def getWordLE(self):
		return self.getBytesLE(4)
