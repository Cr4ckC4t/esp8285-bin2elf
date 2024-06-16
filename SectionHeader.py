class SHTEntry():
	def __init__(self, name, type, flags, addr, offset, size, link, info, addralign, entsize):
		self.size = 0x28
		self.sh_entry = [0x00] * self.size
		self.sh_name = name
		self.sh_type = type
		self.sh_flags = flags
		self.sh_addr = addr
		self.sh_offset = offset
		self.sh_size = size
		self.sh_link = link
		self.sh_info = info
		self.sh_addralign = addralign
		self.sh_entsize = entsize

	def update(self, idx, val):
		self.sh_entry[idx] = val & 0xff
		self.sh_entry[idx+1] = (val >> 8) & 0xff
		self.sh_entry[idx+2] = (val >> 16) & 0xff
		self.sh_entry[idx+3] = (val >> 24) & 0xff

	def finalize(self):
		self.update(0x00, self.sh_name)
		self.update(0x04, self.sh_type)
		self.update(0x08, self.sh_flags)
		self.update(0x0c, self.sh_addr)
		self.update(0x10, self.sh_offset)
		self.update(0x14, self.sh_size)
		self.update(0x18, self.sh_link)
		self.update(0x1c, self.sh_info)
		self.update(0x20, self.sh_addralign)
		self.update(0x24, self.sh_entsize)
		return self.sh_entry

class SHFlags():
	def __init__(self):
		self.WRITE = 0x1
		self.ALLOC = 0x2
		self.EXECINSTR = 0x4
		self.MERGE = 0x10
		self.STRINGS = 0x20
		self.INFO_LINK = 0x40
		self.LINK_ORDER = 0x80
		self.OS_NONCONFORMING = 0x100
		self.GROUP = 0x200
		self.TLS = 0x400
		self.MASKOS = 0x0ff00000
		self.MASKPROC = 0xf0000000

class SectionHeaderTable():
	def __init__(self):
		self.s_header = []
		self.entries = {}

		self.s_type_dict = {
			'SHT_NULL'		: 0,
			'SHT_PROGBITS'		: 1,
			'SHT_SYMTAB'		: 2,
			'SHT_STRTAB' 		: 3,
			'SHT_RELA'		: 4,
			'SHT_HASH' 		: 5,
			'SHT_DYNAMIC' 		: 6,
			'SHT_NOTE' 		: 7,
			'SHT_NOBITS' 		: 8,
			'SHT_REL' 		: 9,
			'SHT_SHLIB' 		: 10,
			'SHT_DYNSYM' 		: 11,
			'SHT_INIT_ARRAY' 	: 14,
			'SHT_FINI_ARRAY' 	: 15,
			'SHT_PREINIT_ARRAY' 	: 16,
			'SHT_GROUP' 		: 17,
			'SHT_SYMTAB_SHNDX' 	: 18,
			'SHT_LOOS'		: 0x60000000,
			'SHT_HIOS' 		: 0x6fffffff,
			'SHT_LOPROC' 		: 0x70000000,
			'SHT_HIPROC' 		: 0x7fffffff,
			'SHT_LOUSER' 		: 0x80000000,
			'SHT_HIUSER' 		: 0xffffffff,
		}

	def getSize(self):
		if len(self.entries) == 0:
			return 0
		return 0x28 * len(self.entries)

	def addSection(self, id, name=0x0, type='SHT_NULL', flags=0x0, addr=0x0, offset=0x0, size=0x0, link=0x0, info=0x0, addralign=0x0, entsize=0x0):
		self.entries[id] = SHTEntry(
			name = name,
			type = self.s_type_dict[type],
			flags = flags,
			addr = addr,
			offset = offset,
			size = size,
			link = link,
			info = info,
			addralign = addralign,
			entsize=entsize
		)

	def finalize(self):
		for entry in self.entries:
			self.s_header += self.entries[entry].finalize()
		return self.s_header

class StringTable():
	def __init__(self):
		self.strtab = []
		self.strs = []

	def get(self, name):
		offset = 0
		for i in range(len(self.strs)):
			if name == self.strs[i]:
				return offset
			offset += len(self.strs[i]) + 1 # take null byte into account

		self.strs.append(name)
		return offset

	def finalize(self):
		for str in self.strs:
			self.strtab += list(str.encode())+[0]
		return self.strtab
