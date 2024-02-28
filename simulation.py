import requests
import argparse


class Queue:
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


class Server:
    def __init__(self):
        self.current_task = None
        self.time_remaining = 0  # for current task

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
        self.time_remaining = new_task.process_time()


class Request:
    def __init__(self, time, sim_sec, name=None):
        self.timestamp = time
        self.sim_sec = sim_sec
        self.name = name

    def process_time(self):
        return self.sim_sec

    def wait_time(self, current_time):
        return current_time - self.timestamp


def simulate_one_server(filename):

    host_server = Server()
    server_queue = Queue()
    waiting_times = []

    # pull all requests from the file into a list
    response = requests.get(filename, verify=False)
    data = response.text
    rows = data.split('\r\n')


    requests_list = []
    # put all requests from the file onto the server queue
    for row in rows:
        #print(row)
        items = row.split(',')
        #print(items[0], items[2])
        req = Request(int(items[0]), int(items[2]), items[1])  # received time, sim_seconds, task name
        requests_list.append(req)



    main_clock = 0
    while True: # main sim loop
        # check if it's time to add next requests to the server queue
        while len(requests_list) != 0:
            req0 = requests_list[0]
            if req0.timestamp == main_clock:
                #pause = input('89: get a request')
                # pull it off requests and put it on the server queue
                requests_list.pop(0) # remove first from list
                server_queue.enqueue(req0)
            else:
                break # done processing requests for this clock time
        # make the server run
        if (not server_queue.is_empty()):
            if not host_server.busy():
                next_task = server_queue.dequeue()  # task == request
                waiting_times.append(next_task.wait_time(main_clock))
                host_server.start_next(next_task)
        host_server.tick()
        main_clock += 1
        #print('103: clock:', main_clock)
        if len(requests_list)==0 and server_queue.is_empty() and host_server.current_task is None:
            break  # all done with simulation

    average_wait = sum(waiting_times) / len(waiting_times)
    print("Average Wait %6.2f secs %3d tasks remaining."
          % (average_wait, server_queue.size()))


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="Enter URL for request inputs file", type=str, required=True)
    # parser.add_argument("--servers", help="Number of servers", type=int, required=True)
    args = parser.parse_args()

    if args.file:
        simulate_one_server(args.file)



if __name__ == '__main__':
    main()
