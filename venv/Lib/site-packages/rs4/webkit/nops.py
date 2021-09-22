from cssselect import GenericTranslator
import lxml.etree
import lxml.html
import lxml.html.clean
import re
import traceback
from copy import deepcopy
from .. import strutil
from . import cssutil

TABSSPACE = re.compile(r'[\s\t]+')
SIMPLIFIED_CHILD_CSS = re.compile (r"\s*([<\[])(\-?)([0-9]+)[>\]]$")

def inner_trim(value):
	if strutil.is_str_like (value):
		# remove tab and white space
		value = re.sub(TABSSPACE, ' ', value)
		value = ''.join(value.splitlines())
		return value.strip()
	return ''

def remove_dquotes (s):
	s = s.strip ()
	if not s:
		return ""
	if s [0] in '\'"':		
		return s [1:-1].replace ('\%s' % s [0], s [0])
	return s		
	
def _filter_by_data (element, text):
	op, op2, text = text [0], text [1], remove_dquotes (text [2:])
	if op2 not in "=|~":
		text = op2 + text
		op2 = "="
		
	if op2 == "=":
		etext = element.text	
		if not etext:
			etext = ""
		else:	
			etext = etext.strip ()
	elif op2 == "|":
		etext = nops.get_text (element)
	else: # "~"		
		etext = element.tail and element.tail.strip () or ''	

	if op == "=":
		return etext == text
	elif op == "/":
		rx = re.compile (text, re.M|re.S)
		return rx.search (etext)
	elif op == "!":
		return etext != text
	elif op == "*":
		return etext.find (text) != -1
	elif op == "^":	
		return etext.startswith (text)
	elif op == "$":
		return etext.endswith (text)
	elif op == "~":	
		return text in etext.split ()
	else:
		raise AssertionError ("unknown operator %s" % op)	
	
def filter_by_data (elements, text):
	return [element for element in elements if _filter_by_data (element, text)]		
										
class nops:
	@classmethod
	def from_string (cls, html):
		if strutil.is_str_like (html) and html.startswith('<?'):
			html = re.sub(r'^\<\?.*?\?\>', '', html, flags=re.DOTALL)				
		try:
			return lxml.html.fromstring(html)
		except Exception:
			traceback.print_exc()
			return None
		
	@classmethod
	def to_string (cls, node, encoding = "utf8", method='html', doctype = None):
		return lxml.html.tostring (node, encoding = encoding, method = method, doctype = doctype).decode ("utf8")
	
	@classmethod
	def by_xpath (cls, node, expression):
		if expression.find ("re:test") != -1:
			return cls.by_xpath_re (node, expression)
		items = node.xpath(expression)
		return items
	
	@classmethod
	def by_xpath_re (cls, node, expression):
		regexp_namespace = "http://exslt.org/regular-expressions"
		items = node.xpath(expression, namespaces={'re': regexp_namespace})
		return items
	
	@classmethod
	def by_css (cls, node, selector):
		m = SIMPLIFIED_CHILD_CSS.search (selector)
		lev = ""
		index = 0
		if m:
			index = int (m.group (3))
			if m.group (2) == "-":
				index *= -1
			if m.group (1) == "<":
				lev = "child"				
			else:	
				lev = "queue"					
				
			selector = SIMPLIFIED_CHILD_CSS.sub ("", selector).strip ()

		if selector.strip ().startswith ("/"):
			founds = cls.by_xpath (node, selector)				
		else:
			founds = cls.by_xpath (node, GenericTranslator().css_to_xpath(selector))
			
		if not lev:	
			return founds
		
		if lev == "queue":		
			try:
				return [founds [index]]
			except IndexError:
				return []			
		
		r = []
		for each in founds:
			try:
				r.append (cls.get_children (each) [index])
			except IndexError:
				pass
		return r			
		
	@classmethod
	def by_id (cls, node, idd):
		selector = '//*[@id="%s"]' % idd
		elems = node.xpath(selector)
		if elems:
			return elems[0]
		return None

	@classmethod
	def by_tag_attr (cls, node, tag=None, attr=None, value=None, childs=False):
		NS = "http://exslt.org/regular-expressions"
		# selector = tag or '*'
		selector = 'descendant-or-self::%s' % (tag or '*')
		if attr and value:
			selector = '%s[re:test(@%s, "%s", "i")]' % (selector, attr, value)		
		elems = node.xpath(selector, namespaces={"re": NS})
		# remove the root node
		# if we have a selection tag
		if node in elems and (tag or childs):
			elems.remove(node)
		return elems
	
	@classmethod
	def by_tag (cls, node, tag):
		return cls.by_tags (node, [tag])
	
	@classmethod
	def by_tags (cls, node, tags):
		selector = ','.join(tags)
		elems = cls.by_css (node, selector)
		# remove the root node
		# if we have a selection tag
		if node in elems:
			elems.remove(node)
		return elems
	
	@classmethod
	def by_tags_nearest (cls, node, tags):
		if type (tags) is str:
			tags = tags.split (",")
		children = cls.get_children (node)
		while children:
			got = [child for child in children if child.tag in tags]
			if got: 
				return got
			children = cls.get_children (children [0])		
		return []
	
	@classmethod
	def by_tag_nearest (cls, node, tag):		
		return cls.by_tags_nearest (node, tag)
		
	@classmethod
	def by_lt (cls, node, text):
		text = text.strip ()
		return [a for a in cls.by_tag (node, "a") if a.get_text () == text]			
	
	@classmethod
	def by_plt (cls, node, text):
		text = text.strip ()
		return [a for a in cls.by_tag (node, "a") if a.get_text ().find (text) != -1]
	
	@classmethod
	def by_css_data (cls, node, text):
		css, text = text.split (":data", 1)
		css = css.strip ()
		text = text.strip ()
		element = cls.by_css (node, css)
		return filter_by_data (element, text)
		
	@classmethod
	def by_tint (cls, node, text):
		tag, text = text.split ("=", 1)
		text = "=" + text.strip ()
		tag = tag.strip ()
		if not tag [-1].isalpha ():
			text = tag [-1] + text
			tag = tag [:-1]
		text = text.strip ()
		element = cls.by_tag (node, tag)
		return filter_by_data (element, text)
								
	@classmethod
	def prev_siblings (cls, node):
		nodes = []
		for c, n in enumerate (node.itersiblings(preceding=True)):
			nodes.append(n)
		return nodes
		
	@classmethod
	def prev_sibling (cls, node):
		nodes = []
		for c, n in enumerate (node.itersiblings(preceding=True)):
			nodes.append(n)
			if c == 0:
				break
		return nodes[0] if nodes else None
	
	@classmethod
	def next_siblings (cls, node):
		nodes = []
		for c, n in enumerate (node.itersiblings(preceding=False)):
			nodes.append(n)
		return nodes
		
	@classmethod
	def next_sibling (cls, node):
		nodes = []
		for c, n in enumerate (node.itersiblings(preceding=False)):
			nodes.append(n)
			if c == 0:
				break
		return nodes[0] if nodes else None
	
	@classmethod
	def get_siblings (cls, node):
		return cls.prev_siblings (node) + cls.next_siblings (node)
		
	@classmethod
	def new (self, tag):			
		return lxml.etree.Element(tag)
		
	@classmethod
	def get_attr (cls, node, attr=None, default = None):
		if attr:
			val = node.attrib.get(attr, None)
			if not val:
				return default
			return val	
		return node.attrib
	
	@classmethod
	def has_attr (cls, node, attr = None):		
		if attr:
			return attr in node.attrib
		return len (node.attrib) != 0
		
	@classmethod
	def del_attr (cls, node, attr=None):
		if attr:
			_attr = node.attrib.get(attr, None)
			if _attr:
				del node.attrib[attr]

	@classmethod
	def set_attr (cls, node, attr=None, value=None):
		if attr and value:
			node.set(attr, value)
					
	@classmethod
	def append_child (cls, node, child):
		node.append(child)
	
	@classmethod
	def get_path (cls, node):
		tree = lxml.etree.ElementTree(node)
		return tree.getpath(node)
		
	@classmethod
	def insert_child (cls, index, node, child):
		node.insert (index, child)
	
	@classmethod
	def insert_next (cls, node, child):
		index = 0
		p = cls.get_parent (node)
		assert p, "No prarent"
		for sib in cls.get_children (p):
			if sib == node:				
				break
			index += 1		
		p.insert (index + 1, child)
	
	@classmethod
	def insert_before (cls, node, child):
		index = 0
		p = cls.get_parent (node)		
		assert p, "No prarent"
		for sib in cls.get_children (p):
			if sib == node:				
				break
			index += 1
		p.insert (index, child)
			
	@classmethod
	def child_nodes (cls, node):
		return list(node)

	@classmethod
	def child_nodes_with_text (cls, node):
		root = node
		# create the first text node
		# if we have some text in the node
		if root.text:
			t = lxml.html.HtmlElement()
			t.text = root.text
			t.tag = 'text'
			root.text = None
			root.insert(0, t)
		# loop childs
		for c, n in enumerate(list(root)):
			idx = root.index(n)
			# don't process texts nodes
			if n.tag == 'text':
				continue
			# create a text node for tail
			if n.tail:
				t = cls.create_element(tag='text', text=n.tail, tail=None)
				root.insert(idx + 1, t)
		return list(root)

	@classmethod
	def get_children (cls, node):
		return node.getchildren()
	
	@classmethod
	def get_parent (cls, node):
		return node.getparent()
		
	@classmethod
	def get_text (cls, node):
		txts = cls.get_text_list (node, False)
		return inner_trim (' '.join(txts).strip())
	
	@classmethod
	def get_texts (cls, node, trim = True):
		return cls.get_text_list (node, trim)
	
	@classmethod
	def get_text_list (cls, node, trim = True):
		txts = list (node.itertext())
		#if node.tail and node.tail.strip ():
		#	txts.append (node.tail)
		if trim:
			return [i.strip () for i in txts]
		return txts
	
	@classmethod
	def has_tail (self, node, recursive = 0):
		if node.tail and node.tail.strip ():
			return 1				
		if recursive:	
			for child in nops.get_children (node):
				has_tail = self.has_tail (child, 1)
				if has_tail:
					return 1
				
	@classmethod
	def collect_children (cls, node):
		def collect (node, container):
			children = cls.get_children (node)
			if not children:
				return
				
			for child in children:								
				container.append (child)
				collect (child, container)

		container = []
		collect (node, container)
		return container
		
	@classmethod
	def iter_text (cls, node):
		def collect (node, container):
			children = cls.get_children (node)
			if not children:
				return
				
			for child in children:
				if child.tag not in (
					"head", "meta", "link", "input", "hr", "br", "img", 
					"table", "tr", "thead", "tbody", "ol", "ul", "dl"
				):
					text = child.text
					if text is not None:
						text = text.strip ()
					else:
						text = ""
					container.append (text)
				collect (child, container)

		container = []
		collect (node, container)
		return container

	@classmethod
	def is_text_node (cls, node):
		return True if node.tag == 'text' else False
	
	@classmethod
	def get_tag (cls, node):
		return node.tag
	
	@classmethod
	def replace_tag (cls, node, tag):
		node.tag = tag

	@classmethod
	def strip_tags (cls, node, *tags):
		lxml.etree.strip_tags(node, *tags)
			
	@classmethod
	def drop_node (cls, node):		
		try: 
			node.drop_tag ()
		except AttributeError:			
			p = node.getparent ()
			for child in node.getchildren ():
				cls.insert_before (node, child)							
			p.remove (node)
	
	@classmethod
	def drop_tree (cls, node):
		def recursive (node):
			for child in node.getchildren ():
				if child.getchildren ():
					recursive (child)
				else:
					node.remove (child)

		try: 
			node.drop_tree ()
		except AttributeError:
			recursive (node)
			node.getparent ().remove (node)
	
	@classmethod
	def contains (cls, node, doc):
		def find_recursive (node, doc):
			children = doc.getchildren ()
			if node in children:
				return True
			for child in children:
				is_contain = find_recursive (node, child)
				if is_contain:
					return True
			return False							
		return find_recursive (node, doc)
			
	@classmethod
	def create_element (cls, tag='p', text=None, tail=None):
		t = lxml.html.HtmlElement()
		t.tag = tag
		t.text = text
		t.tail = tail
		return t

	@classmethod
	def get_comments (cls, node):
		return node.xpath('//comment()')
	
	@classmethod
	def remove_comments (cls, node):
		for item in cls.get_comments (node):
			try:
				item.drop_tree ()
			except AssertionError: # out of root node
				pass
				
	@classmethod
	def text_to_para (cls, text):
		return cls.create_element ('p', text)
	
	@classmethod
	def outer_html (cls, node):
		e0 = node
		if e0.tail:
			e0 = deepcopy(e0)
			e0.tail = None
		return cls.to_string(e0)
	
	ALLOW_TAGS = [
		'a', 'span', 'p', 'br', 'strong', 'b',
		'em', 'i', 'tt', 'code', 'pre', 'blockquote', 'img', 'h1',
		'h2', 'h3', 'h4', 'h5', 'h6'
	]
		
	@classmethod
	def clean_html (cls, node, allow_tags = None):
		article_cleaner = lxml.html.clean.Cleaner()
		article_cleaner.javascript = True
		article_cleaner.style = True
		if not allow_tags:
			article_cleaner.allow_tags = cls.ALLOW_TAGS
		else:
			article_cleaner.allow_tags = allow_tags			
		article_cleaner.remove_unknown_tags = False
		return article_cleaner.clean_html (node)
	
	@classmethod
	def get_param (cls, node, attr, name):
		name = name.lower ()
		params = cls.get_attr (node, attr)
		for param in params.split (";"):
			param = param.strip ()
			if not param.lower ().startswith (name):
				continue
			
			val = param [len (name):].strip ()
			if not val: return ""
			if val [0] == "=":
				val = val [1:].strip ()
				if not val: return ""
			if val [0] in "\"'":
				return val [1:-1]
			return val		
	
	@classmethod
	def resolve_links (cls, node, base_href = None):
		if base_href:
			try:
				# such support is added in lxml 3.3.0
				node.make_links_absolute (base_href, resolve_base_href=True, handle_failures='discard')
			except TypeError:
				node.make_links_absolute (base_href, resolve_base_href=True)
		else:
			node.resolve_base_href ()
		return node
	
	@classmethod
	def get_child_has_grand_children_or_none (cls, origin_node):
		node = origin_node
		while 1:
			children = cls.get_children (node)
			if not children or len (children) > 1:
				return node
			node = children [0]
	
	@classmethod
	def add_class (cls, node, name):
		classes = cls.get_attr (node, "class", "").split (" ")		
		for c in name.split (" "):
			if c not in classes:
				classes.append (c)
		cls.set_attr (node, "class", " ".join (classes).strip ())
	
	@classmethod
	def remove_class (cls, node, name):
		classes = [c for c in cls.get_attr (node, "class", "").split (" ") if c != name]
		new_class = " ".join (classes).strip ()
		if not new_class:
			cls.del_attr (node, "class")
		else:	
			cls.set_attr (node, "class", new_class)		
	
	@classmethod	
	def has_class (cls, node, name):
		return [c for c in cls.get_attr (node, "class", "").split (" ") if c == name]
	
	@classmethod	
	def update_class (cls, node, name, new_name):
		cls.remove_class (node, name)
		cls.add_class (node, new_name)		
	
	@classmethod
	def batch (cls, node, batch):
		for cmd, param in batch:
			if cmd == "strip":
				cls.strip_tags (node, param)				
			
			elif cmd in ("replace", "wrap", "insertb", "inserta", "attach"):
				t = param.split (" ")
				a = " ".join (t[:-1]).strip ()
				b = t[-1].strip ()
				for each in cls.by_css (node, a):
					if cmd == "replace":
						each.tag = b
					elif cmd == "attach":
						n = cls.new (b)
						cls.append_child (each, n)
					elif cmd == "inserta":
						n = cls.new (b)
						cls.insert_after (each, n)
					elif cmd == "insertb":
						n = cls.new (b)
						cls.insert_before (each, n)	
					else:
						n = cls.new (b)
						cls.insert_next (each, n)
						cls.append_child (n, each)
							
			else:
				method, target =  cssutil.make_detector (*param)
				elts = method (node, target)				
				if cmd == "select":
					body = nops.new ("body")
					for elt in elts:
						cls.append_child (body, elt)
					for each in cls.by_tag (node, "body"):
						cls.drop_tree (each)
					cls.append_child (node, body)
					
				else:
					for elt in elts:
						if cmd [:6] == "class+":							
							cls.add_class (elt, cmd [6:])
						elif cmd [:6] == "class-":
							cls.remove_class (elt, cmd [6:])
						elif cmd in ("deltree", "rmtree"):
							cls.drop_tree (elt)
						elif cmd in ("unwrap", "delnode", "rmnode"):
							cls.drop_node (elt)
						elif cmd == "rmtail":
							elt.tail = None
						elif cmd in ("clear", "rmtext"):
							elt.text = ""
						elif cmd == "backspace":
							elt.text += " "
						elif cmd == "frontspace":
							elt.text = " " + elt.text
						else:
							raise SystemError ('Unknown command: %s' % cmd)
						
	@classmethod
	def walk_siblings (cls, node):
		current_sibling = cls.prev_sibling (node)
		b = []
		while current_sibling is not None:
			b.append (current_sibling)
			current_sibling = cls.prev_sibling (current_sibling)
		return b
	
	@classmethod
	def is_decendent (cls, target, node):
		if target == node:
			return 0
		for child in cls.get_children (node):
			if child == target:
				return 1
			if cls.is_decendent (target, child):
				return 1
		return 0	
	
	@classmethod
	def is_ancestor (cls, target, node):
		if target == node:
			return 0
		p = node
		while p:			
			if p == target:
				return 1
			p = cls.get_parent (p)
		return 0	
		
	@classmethod
	def sort_decendent (cls, ancestor, nodes, sorted_children = None):
		if sorted_children is None:
			sorted_children = []
		for child in cls.get_children (ancestor):
			if child in nodes and child not in sorted_children:
				sorted_children.insert (0, child)
				if len (nodes) == len (sorted_children):
					return sorted_children
			cls.sort_decendent (child, nodes, sorted_children)
		return sorted_children	
															
if __name__ == "__main__":	
	from urllib.request import urlopen
	from contextlib import closing
	
	with closing(urlopen("http://www.drugandalcoholrehabhouston.com")) as f:
		build (f.read ())
