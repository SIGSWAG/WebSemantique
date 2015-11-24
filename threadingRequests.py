import threading
import time
import urllib.request
import urllib.parse
import requests

exitFlag = 0



#Define a single thread making a request on a server
class ParallelRequest(threading.Thread):
	def __init__(self, threadId, url, args,lock,results):
		threading.Thread.__init__(self)
		self.threadId = threadId
		self.args = args
		self.lock = lock
		self.results = results
		self.url = url

	def run(self):
		params = urllib.parse.urlencode(self.args)
		params = params.encode('utf-8')
		response = requests.Session().post(url=self.url,data=params)
		with self.lock:
			try:
				ret = response.json()
			except:
				ret = {'status': 'ERROR', 'statusInfo': 'network-error'}
			finally:
				self.results[self.threadId] = ret

#Define a group of request to submit to a server
class RequestPool:
	def __init__(self, url, args_list):
		self.url = url
		self.args_list = args_list

	def launch(self):
		threads = []
		threadId = 1
		self.results = [None] * (len(self.args_list)+1)
		lock = threading.Lock()
		#each request is defined by its args list
		for args in self.args_list :
			threads = []
			thread = ParallelRequest(threadId,self.url,args,lock,self.results)
			thread.start()
			threads.append(thread)
			threadId += 1

		for t in threads:
			t.join()

	def getResults(self):
		return self.results
