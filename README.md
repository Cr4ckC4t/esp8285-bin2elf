# ESP8285 Bin2ELF

Reverse engineering ESP8285 firmware with pure python3.

> [!NOTE]
> This is an ongoing project but the code works for ESP8285 firmware that was generated with `elf2bin.py`.

# Usage
```sh
python3 bin2elf.py -f /flashdump.bin
ELF Header (Bootloader):
	Magic: E9
	Segments: 2
	Flash Mode: dout
	Flash Frequency: 40
	Flash Size: 1M
	Entry Address: 0x4010f480
	Binary Checksum: 2B
ELF Segments:
	.text:
		Address: 0x4010f000
		Size: 0xd60
	.rodata:
		Address: 0x3fff20b8
		Size: 0x28

ELF Header (Application):
	Magic: E9
	Segments: 5
	Flash Mode: dout
	Flash Frequency: 40
	Flash Size: 1M
	Entry Address: 0x401000c0
	Binary Checksum: 58
ELF Segments:
	.irom0.text:
		Address: 0x40201010
		Size: 0x41be0
	.text:
		Address: 0x40100000
		Size: 0x102
	.text1:
		Address: 0x40100104
		Size: 0x68cd
	.data:
		Address: 0x3ffe8000
		Size: 0x5e0
	.rodata:
		Address: 0x3ffe8620
		Size: 0x42c

Converting app to ELF
Assemble program header table
Assemble section header table
Assemble sections
Assemble ELF structure
Writing ELF to: app.elf
```

# Credits/Resources

Standing on the shoulders of giants. Some resources in no particular order:
- https://github.com/esp8266/Arduino/blob/master/tools/elf2bin.py
- https://github.com/jsandin/esp-bin2elf
- https://www.youtube.com/watch?v=w4_3vwN_2dI
- https://github.com/yath/ghidra-xtensa
- https://richard.burtons.org/2015/05/17/esp8266-boot-process/
- https://olof-astrand.medium.com/reverse-engineering-of-esp32-flash-dumps-with-ghidra-or-ida-pro-8c7c58871e68
