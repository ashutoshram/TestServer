from selenium.webdriver.common.by import By
import re

By.TEXT_IN_TAG = "text in tag"
By.CSS_TEXT = "css text"

def get_finding_string (params):
	what = ""
	if not params:
		return By.CSS_SELECTOR, ""
	if params [0] in "\"'":
		quot = params [0]								
		pos = 1
		while 1:
			s = params.find (quot, pos)
			if s ==- 1:
				raise AssertionError ("Quotes Not Matched In ADU Rule")
			if params [s-1] == "\\":
				pos = s + 1
			else:
				break
		what = params [1:s]
		params = params [s + 1:].strip ()
	
	s = params.find (" by ")
	if s == -1:
		by = "CSS_SELECTOR"
		if what.startswith ("/"):
			by = "XPATH"
	else:
		by = params [s + 4:].strip ()
		params = params [:s]
		
	if not what:
		what = params.strip ()
	
	try:
		by = getattr (By, by)
	except AttributeError:
		raise AssertionError	 ("Unknown By Object '%s' In ADU Rule" % by)
					
	return by, what

def make_detector (by, what):
	from .nops import nops as p
	
	if by == By.XPATH:
		fmethod, fobject = p.by_xpath, what
	elif by == By.TEXT_IN_TAG:
		fmethod, fobject = p.by_tint, what
	elif by == By.CSS_TEXT:
		fmethod, fobject = p.by_csstext, what			
	elif by == By.LINK_TEXT:
		fmethod, fobject = p.by_lt, what
	elif by == By.PARTIAL_LINK_TEXT:
		fmethod, fobject = p.by_plt, what			
	elif by == By.TAG_NAME:	
		fmethod, fobject = p.by_tag, what
	else:
		if by == By.ID:
			css = "#" + what
		elif by == By.CLASS_NAME:	
			css = "." + what
		elif by == By.NAME:	
			css = '[name="%s"]' % what
		elif by == By.CSS_SELECTOR:
			css = what
		else:
			raise AssertionError ("Unknown By Method")			
		if css.find (":data") != -1:
			fmethod, fobject = p.by_css_data, css				
		else:	
			fmethod, fobject = p.by_css, css
							
	return fmethod, fobject

def get_parser_method (param):
	return make_detector (*get_finding_string (param))
get_finder = get_parser_method

RX_TAGS = re.compile (
	(
		"(img|a|table|div|span|font|small|b|i|u|strong|"
		"tr|td|th|p|blockquote|ul|ol|dl|li|dt|dl|dd|button|"
		"input|form|textarea|options|select)"
		"($|[^a-z])"
	)
)

RX_UF = re.compile (r"(^|[^a-z])([gf]\.[a-zA-Z][_a-zA-Z0-9]*\s*\()")

def get_extractor (params):
	ffrom = None
	temp = params.split (" from ", 1)
	if len (temp) == 2:
		ffrom = temp [0].strip ()
		params = temp [1]
		return (ffrom,) + (get_finder (params))	
	
	if RX_UF.search (params):		
		return (params.strip (), None, None)
		
	if params [0] in ".#/" or params.find ('rf-') != -1 or params.find (':data') != -1 or RX_TAGS.match (params):
		# definitly html eleemt
		return ('data',) + (get_finder (params))
		
	return (params.strip (), None, None)


RX_VARNAME = re.compile (r'\(\s*([a-z]+)?\s*[),.]')	
def get_var (ctx):
	var = ctx
	if ctx.find ("g.") != -1 or ctx.find ("f.") != -1:
		try:
			var = RX_VARNAME.findall (ctx)[0]
		except IndexError:	
			var = ctx	
	return var
	