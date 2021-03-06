# @date 2019-01-01
# @author Frederic SCHERMA
# @license Copyright (c) 2019 Dream Overflow
# streamable model

class Streamable(object):
	"""
	Interface for an object having some variable to be monitored/streamed.
	"""

	STREAM_UNDEFINED = 0
	STREAM_GENERAL = 1
	STREAM_TRADER = 1
	STREAM_STRATEGY = 2
	STREAM_STRATEGY_CHART = 3
	STREAM_STRATEGY_INFO = 4

	def __init__(self, monitor_service, stream_category, stream_group, stream_name):
		self._monitor_service = monitor_service
		self._activity = False

		self._stream_name = stream_name
		self._stream_category = stream_category
		self._stream_group = stream_group

		self._members = {}
		self._count = 0   # reference counter

	def enable(self):
		self._activity = True

	def disable(self):
		self._activity = False

	@property
	def name(self):
		return self._name

	@property
	def activity(self):
		return self._activity

	def add_member(self, member):
		self._members[member.name] = member

	def remove_member(self, member_name):
		if member_name in self._members:
			del self._members[member_name]

	def member(self, member_name):
		return self._members.get(member_name)

	def push(self):
		if self._monitor_service:
			for k, member in self._members.items():
				if member.has_update():
					# push and cleanup
					self._monitor_service.push(self._stream_category, self._stream_group, self._stream_name, member.content())
					member.clean()

	def use(self):
		self._count += 1

	def unuse(self):
		if self._count > 0:
			self._count -= 1

	def is_free(self):
		return self._count == 0


class StreamMember(object):
	"""
	Base class for a streamed member.
	"""

	TYPE_UNDEFINED = None

	def __init__(self, name, member_type):
		self._name = name
		self._type = member_type
		self._updated = False

	@property
	def name(self):
		return self._name

	@property
	def value(self):
		return self._value

	def update(self, value):
		pass

	def has_update(self):
		return self._updated

	def clean(self):
		self._updated = False

	def content(self):
		"""
		Dict formatted content.
		"""
		return {'n': self._name, 't': None, 'v': None}


class StreamMemberBool(StreamMember):
	"""
	Specialization for a boolean value.
	"""

	TYPE_BOOL = "b"

	def __init__(self, name):
		super().__init__(name, StreamMemberBool.TYPE_BOOL)

		self._value = False

	def update(self, value):
		self._value = value
		self._updated = True

	def content(self):
		return {'n': self._name, 't': self.TYPE_BOOL, 'v': self._value}


class StreamMemberInt(StreamMember):
	"""
	Specialization for an integer value.
	"""

	TYPE_INT = "i"

	def __init__(self, name):
		super().__init__(name, StreamMemberInt.TYPE_INT)

		self._value = 0

	def update(self, value):
		self._value = value
		self._updated = True

	def content(self):
		return {'n': self._name, 't': self._type, 'v': self._value}


class StreamMemberIntList(StreamMember):
	"""
	Specialization for a list of integer.
	"""

	TYPE_INT_LIST = "il"

	def __init__(self, name):
		super().__init__(name, StreamMemberIntList.TYPE_INT_LIST)

		self._value = 0

	def update(self, int_array):
		self._value = value
		self._updated = True

	def content(self):
		return {'n': self._name, 't': self._type, 'v': self._value}


class StreamMemberFloat(StreamMember):
	"""
	Specialization for a signal float value.
	"""

	TYPE_FLOAT = "f"

	def __init__(self, name):
		super().__init__(name, StreamMemberFloat.TYPE_FLOAT)

		self._value = 0.0

	def update(self, value):
		self._value = value
		self._updated = True

	def content(self):
		return {'n': self._name, 't': self._type, 'v': self._value}


class StreamMemberFloatTuple(StreamMember):
	"""
	Specialization for a signal float tuple values.
	"""

	TYPE_FLOAT_TUPLE = "ft"

	def __init__(self, name):
		super().__init__(name, StreamMemberFloatTuple.TYPE_FLOAT_TUPLE)
		self._values = []

	def update(self, array):
		self._values = array
		self._updated = True

	def content(self):
		return {'n': self._name, 't': self._type, 'v': self._values}


class StreamMemberFloatSerie(StreamMember):
	"""
	Specialization for a signal float serie value.
	"""

	TYPE_FLOAT_SERIE = "fs"

	def __init__(self, name, index):
		super().__init__(name, StreamMemberFloatSerie.TYPE_FLOAT_SERIE)

		self._index = index
		self._base = 0.0
		self._value = 0.0

	def update(self, value, timestamp):
		self._value = value
		self._timestamp = timestamp
		self._updated = True

	def content(self):
		return {'n': self._name, 'i': self._index, 't': self._type, 'v': self._value, 'b': self._timestamp}


class StreamMemberFloatBarSerie(StreamMember):
	"""
	Specialization for a signal float bar serie value.
	"""

	TYPE_FLOAT_BAR_SERIE = "fbs"

	def __init__(self, name, index):
		super().__init__(name, StreamMemberFloatBarSerie.TYPE_FLOAT_BAR_SERIE)

		self._index = index
		self._base = 0.0
		self._value = 0.0

	def update(self, value, timestamp):
		self._value = value
		self._timestamp = timestamp
		self._updated = True

	def content(self):
		return {'n': self._name, 'i': self._index, 't': self._type, 'v': self._value, 'b': self._timestamp}


class StreamMemberStrList(StreamMember):
	"""
	Specialization for a list of str.
	"""

	TYPE_STRING_LIST = "sl"

	def __init__(self, name):
		super().__init__(name, StreamMemberStrList.TYPE_STRING_LIST)

		self._value = 0.0

	def update(self, str_list):
		self._value = str_list
		self._updated = True

	def content(self):
		return {'n': self._name, 't': self._type, 'v': self._value}


class StreamMemberTradeList(StreamMember):
	"""
	Specialization for a list of trades.
	@todo could have a trade it for interaction
	@todo could inform if order is in progress (buy, sell, stop, limit)...
	@todo entry,update,exit detail
	"""

	TYPE_TRADE_LIST = "tl"

	def __init__(self, name):
		super().__init__(name, StreamMemberTradeList.TYPE_TRADE_LIST)

		self._trades = []

	def update(self, trades):
		self._trades = []

		for trade in trades:
			self._trades.append({
				't': trade.trade_type,
				'os': trade.entry_state,
				'es': trade.exit_state,
				'u': trade.timeframe,
				'p': trade.aep,
				'd': trade.dir,
				'q': trade.q,  # order qty
				'e': trade.e,  # filled entry qty
				'x': trade.x,  # filled exit qty
				'sl': trade.sl,
				'tp': trade.tp
			})

		self._updated = True

	def content(self):
		return {'n': self._name, 't': self._type, 'v': self._trades}


class StreamMemberSerie(StreamMember):
	"""
	Specialization for a serie begin/end. Value is a float second timestamp.
	"""

	TYPE_SERIE = "se"

	def __init__(self, name):
		super().__init__(name, StreamMemberSerie.TYPE_SERIE)

		self._value = 0.0

	def update(self, timestamp):
		self._value = timestamp
		self._updated = True

	def content(self):
		return {'n': self._name, 't': self._type, 'v': self._value}


class StreamMemberFloatScatter(StreamMember):
	"""
	Specialization for a signal float scatter value.
	"""

	TYPE_FLOAT_SCATTER = "fsc"

	def __init__(self, name, index, glyph):
		super().__init__(name, StreamMemberFloatScatter.TYPE_FLOAT_SCATTER)

		self._index = index
		self._base = 0.0
		self._value = 0.0
		self._glyph = glyph

	def update(self, value, timestamp):
		self._value = value
		self._timestamp = timestamp
		self._updated = True

	def content(self):
		return {'n': self._name, 'i': self._index, 't': self._type, 'v': self._value, 'b': self._timestamp, 'o': self._glyph}


class StreamMemberOhlcSerie(StreamMember):
	"""
	Specialization for a signal OHLC value.
	"""

	TYPE_OHLC_SERIE = "os"

	def __init__(self, name):
		super().__init__(name, StreamMemberOhlcSerie.TYPE_OHLC_SERIE)

		self._index = 0
		self._value = (0.0, 0.0, 0.0, 0.0)

	def update(self, v, timestamp):
		self._value = v  # quadruplet
		self._timestamp = timestamp
		self._updated = True

	def content(self):
		return {'n': self._name, 'i': self._index, 't': self._type, 'v': self._value, 'b': self._timestamp}
