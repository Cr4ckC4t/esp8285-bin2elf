class PHTEntry():
	def __init__(self, type=0x0, offset=0x0, vaddr=0x0, paddr=0x0, filesz=0x0, memsz=0x0, flags=0x0, align=0x0):
		self.size = 0x20 # 32 byte
		self.p_entry = [0x00] * self.size

		self.p_type = type              # p_type (segment type, 1 = LOAD)
		self.p_offset = offset          # p_offset (segment file offset)
		self.p_vaddr = vaddr            # p_vaddr (virtual address)
		self.p_paddr = paddr            # p_paddr (physical address)
		self.p_filesz = filesz          # p_filesz (segment size in file)
		self.p_memsz = memsz           # p_memsz (segment size in memory)
		self.p_flags = flags            # p_flags (segment flags)
		self.p_align = align            # p_align (segment alignment)

	def update(self, idx, val):
		self.p_entry[idx] = val & 0xff
		self.p_entry[idx+1] = (val >> 8) & 0xff
		self.p_entry[idx+2] = (val >> 16) & 0xff
		self.p_entry[idx+3] = (val >> 24) & 0xff

	def finalize(self):
		self.update(0x00, self.p_type)
		self.update(0x04, self.p_offset)
		self.update(0x08, self.p_vaddr)
		self.update(0x0c, self.p_paddr)
		self.update(0x10, self.p_filesz)
		self.update(0x14, self.p_memsz)
		self.update(0x18, self.p_flags)
		self.update(0x1c, self.p_align)
		return self.p_entry

class ProgramHeaderTable():
	def __init__(self, default_type, default_align):
		self.default_align = default_align
		self.default_type = default_type
		self.p_header = []
		self.entries = {}
		self.p_flag_dict = {
			'None'  : 0,    # no permissions
			'PF_X'  : 1,    # execute
			'PF_W'  : 2,    # write
			'PF_WX' : 3,    # write, execute
			'PF_R'  : 4,    # read
			'PF_RX' : 5,    # read, execute
			'PF_RW' : 6,    # read, write
			'PF_RWX': 7     # read, write, execute
		}

	def getSize(self):
		if len(self.entries) == 0:
			return 0
		return 0x20 * len(self.entries)

	def addHeader(self, name, offset=0x0, vaddr=0x0, paddr=0x0, filesz=0x0, memsz=0x0, flags='None', type=None, align=None):
		self.entries[name] = PHTEntry(
		type   = (type if type else self.default_type),
			offset = offset,
			vaddr  = vaddr,
			paddr  = paddr,
			filesz = filesz,
			memsz  = memsz,
			flags  = self.p_flag_dict[flags],
			align  = (align if align else self.default_align)
		)

	def finalize(self):
		for entry in self.entries:
			self.p_header += self.entries[entry].finalize()
		return self.p_header
