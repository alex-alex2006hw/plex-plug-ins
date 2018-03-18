import urllib2, cookielib, re, common

# This script uses HEAD requests (with fallback in case of 405) 
# to follow the redirect path up to the real URL
# (c) 2012 Filippo Valsorda - FiloSottile
# Released under the GPL license
#
# https://gist.github.com/FiloSottile/2077115
#
# Modified by CA for cCloudTV for Plex
# https://github.com/coder-alpha/CcloudTv.bundle
# https://forums.plex.tv/discussion/166602/rel-ccloudtv-channel-iptv
#

class HeadRequest(urllib2.Request):
	def get_method(self):
		return "HEAD"

class HEADRedirectHandler(urllib2.HTTPRedirectHandler):
	"""
	Subclass the HTTPRedirectHandler to make it use our 
	HeadRequest also on the redirected URL
	"""
	def redirect_request(self, req, fp, code, msg, headers, newurl): 
		if code in (301, 302, 303, 307):
			newurl = newurl.replace(' ', '%20') 
			newheaders = dict((k,v) for k,v in req.headers.items()
							  if k.lower() not in ("content-length", "content-type"))
			return HeadRequest(newurl, 
							   headers=newheaders,
							   origin_req_host=req.get_origin_req_host(), 
							   unverifiable=True) 
		else: 
			raise urllib2.HTTPError(req.get_full_url(), code, msg, headers, fp) 
			
class HTTPMethodFallback(urllib2.BaseHandler):
	"""
	Fallback to GET if HEAD is not allowed (405 HTTP error)
	"""
	def http_error_405(self, req, fp, code, msg, headers): 
		fp.read()
		fp.close()

		newheaders = dict((k,v) for k,v in req.headers.items()
						  if k.lower() not in ("content-length", "content-type"))
		return self.parent.open(urllib2.Request(req.get_full_url(), 
										 headers=newheaders, 
										 origin_req_host=req.get_origin_req_host(), 
										 unverifiable=True))


# Build our opener

def GetRedirect2(url, rurl, timeout):

	try:
		opener = urllib2.OpenerDirector() 
		for handler in [urllib2.HTTPHandler, urllib2.HTTPDefaultErrorHandler,
						HTTPMethodFallback, HEADRedirectHandler,
						urllib2.HTTPErrorProcessor, urllib2.HTTPSHandler]:
			opener.add_handler(handler())

		response = opener.open(HeadRequest(url))
		txt = response.read()
		if 'META HTTP-EQUIV="refresh"' in txt:
					url = re.findall('http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', txt)[0]
					response = GetRedirect2(url, rurl, timeout)
						

		return response
	
	except StandardError:
		headers = {'User-Agent': common.USER_AGENT,
		   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		   'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
		   'Accept-Encoding': 'none',
		   'Accept-Language': 'en-US,en;q=0.8',
		   'Connection': 'keep-alive',
		   'Referer': rurl}
	   
		if '|' in url:
			url_split = url.split('|')
			url = url_split[0]
			headers['Referer'] = url
			for params in url_split:
				if '=' in params:
					param_split = params.split('=')
					param = param_split[0].strip()
					param_val = urllib2.quote(param_split[1].strip(), safe='/=&')
					headers[param] = param_val
	   
		try:
			req = urllib2.Request(url, headers=headers)
			response = urllib2.urlopen(req, timeout=timeout)
			txt = response.read()
			if 'META HTTP-EQUIV="refresh"' in txt:
						url = re.findall('http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', txt)[0]
						response = GetRedirect2(url, url, timeout)
			return response
		except urllib2.HTTPError, e:
			pass

	return None
	
def GetRedirect(url, timeout):
	return GetRedirect2(url, url, timeout)

def Test(url):
	conn = GetRedirect(url, 10)
	print conn.geturl()