class SymbolTableEntry():
	index = 0
	def __init__(self, name, addr, size, info, other):
		self.st_entry = [0x00] * 0x10
		self.st_name = name
		self.st_value = addr
		self.st_size = size
		self.st_info = info
		self.st_other = other
		self.st_shndx = SymbolTableEntry.index
		SymbolTableEntry.index+=1

	def update(self, idx, val):
		self.st_entry[idx] = val & 0xff

	def updateHalfWord(self, idx, val):
		self.update(idx, val)
		self.update(idx+1, val >> 8)

	def updateWord(self, idx, val):
		self.update(idx, val)
		self.update(idx+2, val >> 16)


	def finalize(self):
		self.updateWord(0x0, self.st_name)
		self.updateWord(0x4, self.st_value)
		self.updateWord(0x8, self.st_size)
		self.update(0xc, self.st_info)
		self.update(0xd, self.st_other)
		self.updateHalfWord(0xe, self.st_shndx)
		return self.st_entry

class SymbolTable():
	def __init__(self):
		self.symtab = []
		self.entries = {}

	def addSymbol(self, id, name=0x0, addr=0x0, size=0x0, info=0x0, other=0x0):
		s = SymbolTableEntry(
			name=name,
			addr=addr,
			size=size,
			info=info,
			other=other,
		)
		self.entries[id] = s

	def finalize(self):
		for entry in self.entries:
			self.symtab += self.entries[entry].finalize()
		return self.symtab
