class ELFHeader():
	def __init__(self):
		# TODO: ghidra doesnt get this as header.. experiment and find out why
		# build ELF header
		# https://docs.oracle.com/cd/E23824_01/html/819-0690/chapter6-43405.html

		self.elf_header = []				# identification index: e_ident_
		self.elf_header += [0x7f]			# e_ident_magic_num (ELF)
		self.elf_header += [0x45, 0x4c, 0x46]		# e_ident_magic_str ("ELF")
		self.elf_header += [0x01]			# e_ident_class (32-bit)
		self.elf_header += [0x01]			# e_ident_data (LSB)
		self.elf_header += [0x01]			# e_ident_vers
		self.elf_header += [0x00]			# e_ident_osabi
		self.elf_header += [0x00]			# e_ident_abiv
		self.elf_header += [0, 0, 0, 0, 0, 0, 0]	# e_ident_pad

		self.elf_header += [0x02, 0x00]			# e_type (executable)
		self.elf_header += [0x5e, 0x00]			# e_machine (Tensilica Xtensa Architecture)
		self.elf_header += [0x01, 0x00, 0x00, 0x00]	# e_version (EV_CURRENT)
		self.elf_header += [0x00, 0x00, 0x00, 0x00]	# e_entry (entry address of the application)
		self.elf_header += [0x34, 0x00, 0x00, 0x00]	# e_phoff (program header table's file offset in bytes - comes directly after the ELF header)
		self.elf_header += [0x00, 0x00, 0x00, 0x00]	# e_shoff (section header table's file offset in bytes)
		self.elf_header += [0x00, 0x03, 0x00, 0x00]	# e_flags (https://github.com/espressif/binutils-esp32ulp/blob/9bb46bab6b2e1ef1a246c3700f0a9ed791bfe477/include/elf/xtensa.h#L103C1-L104C37)
		self.elf_header += [0x34, 0x00]			# e_ehsize (ELF header's size in bytes - 52 bytes)
		self.elf_header += [0x20, 0x00]			# e_phentsize (The size in bytes of one entry in the file's program header table)
		self.elf_header += [0x00, 0x00]			# e_phnum (number of entries in the program header table)
		self.elf_header += [0x00, 0x00]			# e_shentsize (size in bytes of one entry in the file's section header table)
		self.elf_header += [0x0, 0x00]			# e_shnum (number of entries in the section header table)
		self.elf_header += [0x00, 0x00]			# e_shstrndx (section header table index of the entry that is associated with the section name string table)

	def updateWord(self, idx, val):
		self.updateHalfWord(idx, val)
		self.updateHalfWord(idx+2, val>>16)

	def updateHalfWord(self, idx, val):
		self.elf_header[idx] = val & 0xff
		self.elf_header[idx+1] = (val >> 8) & 0xff

	def updateEntryAddress(self, addr):
		self.updateWord(0x18, addr)

	def updateSHOffset(self, offset):
		self.updateWord(0x20, offset)

	def updatePHNum(self, num):
		self.updateHalfWord(0x2c, num)

	def updateSHEntSize(self, num):
		self.updateHalfWord(0x2e, num)

	def updateSHNum(self, num):
		self.updateHalfWord(0x30, num)

	def updateSHStrNdx(self, num):
		self.updateHalfWord(0x32, num)

	def getSize(self):
		return len(self.elf_header)

	def finalize(self):
		return self.elf_header
