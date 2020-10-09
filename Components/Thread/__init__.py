from threading import Thread, Lock
from queue import Queue
from Components import AbstractComponent
import os

task_lock = Lock()
exitFlag = 0


class TaskThread(Thread):
    def __init__(self, root_app, queue):
        super().__init__()

        self.queue = queue
        self.root_app = root_app

    def run(self):
        while not exitFlag:
            if not self.queue.empty():
                data = self.queue.get()
                self.root_app.exec_task(data)


class ThreadComponent(AbstractComponent):
    def __init__(self, root_app):
        super().__init__("Thread", root_app)

        self.state.set("queue", Queue())
        self.state.set("protected_queue", Queue())
        self.state.set("threads", [])

    def create_thread(self):
        new_thread = TaskThread(self.root_app, self.state.queue)
        self.state.threads.append(new_thread)

    def add_task(self, exec_type, namespace, payload):
        task = {
            'type': exec_type,
            'namespace': namespace,
            'payload': payload
        }

        self.state.queue.put(task)

    def initialization(self, payload):
        for i in range(os.cpu_count()-1):
            self.create_thread()

        for thread in self.state.threads:
            thread.start()

    def stop_threads(self):
        for thread in self.state.threads:
            thread.join()
