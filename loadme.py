import threading
import requests
import Queue
import os
import time
import sys

from itertools import cycle

errcount = 0

class UrlReaderX(threading.Thread):
    def __init__(self, queue, output):
        super(UrlReaderX, self).__init__()
        self.setDaemon = True
        self.queue = queue
        self.output = output

    def run(self):
        while True:
            try:
#                print self
                target = self.queue.get(block = False)
#                print str(target)
                headers = {'User-Agent': 'Mozilla/5.0'}
                data = requests.get(target, headers = headers)
 #               print data.status_code
                current_page = data.url.split('&')[0].split('=')[1]
                if data.status_code == 200:
                    self.queue.task_done()
  #                  print 'putting!'
                    self.output.put((data.text, current_page), block = False)
                elif data.status_code == 404:
                    print '404->', str(target)
                    self.queue.task_done()
                else:
                    self.queue.task_done()
                    self.queue.put(target)
            except Queue.Empty:
                break
            except requests.exceptions.ConnectionError:
#	        r.status_code = "Connection refused"
#		print data.status_code
#		print 'exception!'
#		global errcount
#		errcount += 1
                self.queue.task_done()
                self.queue.put(target)

#errcount = 0

def load(urlrange, num_threads):
    print 'here kek!'
    mainqueue = Queue.Queue()
    outq = Queue.Queue()
    mythreads = []

    for url in urlrange:
        mainqueue.put(url)

    print len(list(mainqueue.__dict__['queue']))

    for j in xrange(num_threads):
        mythreads.append(UrlReaderX(mainqueue, outq))
        mythreads[-1].start()

    lst = ['|', '/', '-', '\\']
    pool = cycle(lst)
    brd = len(mainqueue.__dict__['queue'])
    while True:
        if len(mainqueue.__dict__['queue']) == 0:
            break
        time.sleep(0.1)
        sys.stdout.write("\r%c %f%%" % (next(pool), ((float(brd - len(mainqueue.__dict__['queue']))/brd)*100)))
        sys.stdout.flush()
    print 'working!'
    mainqueue.join()
    for j in xrange(num_threads):
        mythreads.append(UrlReaderX(mainqueue, outq))
        mythreads[j].join()
#    global errcount
#    print errcount
    print 'exited!'
    print 'err', str(errcount)
    return list(outq.__dict__['queue'])


