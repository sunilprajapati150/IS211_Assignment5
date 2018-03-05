#!usr/bin/env python
# -*- coding: utf-8 -*-
""" simulation of how network request and process by a single web server"""

import urllib2
import csv
import argparse
import random
import datetime


class Server(object):

    def __init__(self):
        self.current_task = None
        self.time_remaining = 0

    def tick(self):
        if self.current_task != None:
            self.time_remaining = self.time_remaining - 1
            if self.time_remaining <= 0:
                self.current_task = None

    def busy(self):
        if self.current_task != None:
            return True
        else:
            return False

    def start_next(self, new_task):
        self.current_task = new_task
        self.time_remaining = new_task.proccs_time()

class Request(object):

    def __init__(self, time, time_req):
        self.timestamp = time
        self.time_req = time_req

    def proccs_time(self):
        return self.time_req

    def wait_time(self, current_time):
        return current_time - self.timestamp
    
class Queue(object):

    def __init__(self):
        self.items = []

    def is_empty(self):
        return self.items == []

    def enqueue(self, item):
        self.items.insert(0, item)

    def dequeue(self):
        return self.items.pop()

    def size(self):
        return len(self.items)

def simulateOneServer(num_seconds, time_required):
    """
    the average wait time for a request.
        
    Examples:
        >>> simulateOneServer(15, 3)
        Average wait -15.00 secs   0 tasks remaining.
    """
    host_server = Server()
    request_queue = Queue()
    waiting_times = []
    request_link = Request(num_seconds, time_required)
    request_queue.enqueue(request_link)

    for current_second in range(num_seconds):

        if (not host_server.busy()) and (not request_queue.is_empty()):
            next_task = request_queue.dequeue()
            waiting_times.append(next_task.wait_time(current_second))
            host_server.start_next(next_task)

        host_server.tick()

    average_wait = sum(waiting_times) / len(waiting_times)
    print "Average wait %6.2f secs %3d tasks remaining." % \
    (average_wait, request_queue.size())

def simulateManyServers(request_file, servers):
    
    servers_list = [n for n in range(0, int(servers))]
    server_room = {}
    for computer in servers_list:
        server_room[computer] = simulateOneServer
    for data in request_file:
        for serv_num in servers_list:
            random.seed(datetime.datetime.now())
            server_num = random.choice(servers_list)
            server_room[server_num](int(data[0]), int(data[2]))

def main():
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--file', help='Enter URL of CSV File')
    parser.add_argument('-c', '--servers', help='Enter number of Servers')
    args = parser.parse_args()

    try:
        if args.file:
            take_the_file = urllib2.urlopen(args.file)
            read_the_file = csv.reader(take_the_file)
            for row in read_the_file:
                simulateOneServer(int(row[0]), int(row[2]))
        elif args.servers:
            take_the_file = urllib2.urlopen('http://s3.amazonaws.com/cuny-is211-spring2015/requests.csv')
            read_the_file = csv.reader(take_the_file)
            simulateManyServers(read_the_file, args.servers)
        else:
            print 'Invalid attempt, please enter a url'

    except urllib2.URLError as url_err:
        print 'The URL is not VALID, enter VALID URL'
        raise url_err
    
if __name__ == '__main__':
    main()
