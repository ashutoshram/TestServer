class F:
	def __init__ (self, val):
		self.val = val
		
	def __str__ (self):
		return self.val
	
	def add_percent (self, pos = 0):
		if pos == 0:
			self.val = "'%' || " + str (self.val) + " || '%'"
		elif pos == 1:	
			self.val = "'%' || " + str (self.val)
		else:
			self.val = str (self.val) + " || '%'"
