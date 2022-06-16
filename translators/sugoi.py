import requests
import hashlib
import urllib.parse
import random
import traceback
import json
import time
import textwrap

import aiohttp

class Translator(object):
	def __init__(self):
		pass

	async def translate(self, from_lang, to_lang, query_text):
		headers = {'Content-type': 'application/json'}
		data = {"content": query_text, "message":"translate sentences"}
		async with aiohttp.ClientSession() as session:
			async with session.post('http://localhost:14366', json=data, headers=headers) as resp:
				result = await resp.json(content_type=None)
		return result
		#lines = textwrap.wrap(result, 70, break_long_words=False)

