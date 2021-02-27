import data as dataTypes
import struct

def uleb128Encode(num: int):
	if not num:
		return bytearray(b"\x00")

	arr = bytearray()
	length = 0

	while num > 0:
		arr.append(num & 127)
		num >>= 7
		if num != 0:
			arr[length] |= 128
		length += 1

	return arr

def pack_data(__data, __dataType):
	data = bytes()
	pack = True
	packType = "<B"

	if __dataType == dataTypes.bbytes:
		pack = False
		data = __data
	elif __dataType == dataTypes.string:
		pack = False
		if len(__data) == 0:
			data += b"\x00"
		else:
			data += b"\x0B"
			data += uleb128Encode(len(__data))
			data += str.encode(__data, "latin_1")
	elif __dataType == dataTypes.rawReplay:
		pack = False
		data += pack_data(len(__data), dataTypes.uInt32)
		data += __data
	else:
		packType = {
			dataTypes.uInt16: "<H",
			dataTypes.sInt16: "<h",
			dataTypes.uInt32: "<L",
			dataTypes.sInt32: "<l",
			dataTypes.uInt64: "<Q",
			dataTypes.sInt64: "<q",
			dataTypes.string: "<s",
			dataTypes.ffloat: "<f"
		}.get(__dataType)

	if pack:
		data += struct.pack(packType, __data)

	return data

def binary_write(structure = None):
	if not structure:
		structure = []

	packetData = bytes()

	for i in structure:
		packetData += pack_data(i[0], i[1])

	return packetData

def replay_time(unixTime):
	return (10000000*unixTime) + 621355968000000000