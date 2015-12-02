import threading
import time
import urllib.request
import urllib.parse
import requests

exit_flag = 0

#Define a single thread making a request on a server
class ParallelRequest(threading.Thread):
	def __init__(self, thread_id, url, args, lock, results):
		threading.Thread.__init__(self)
		self.thread_id = thread_id
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
				self.results[self.thread_id] = ret


#Define a group of request to submit to a server
class RequestPool:
	def __init__(self, url, args_list):
		self.url = url
		self.args_list = args_list

	def launch(self):
		threads = []
		thread_id = 1
		self.results = [None] * (len(self.args_list)+1)
		lock = threading.Lock()
		#each request is defined by its args list
		for args in self.args_list :
			threads = []
			thread = ParallelRequest(thread_id, self.url, args, lock, self.results)
			thread.start()
			threads.append(thread)
			thread_id += 1

		for t in threads:
			t.join()

	# return the result of a thread, when finished
	def get_results(self):
		return self.results
