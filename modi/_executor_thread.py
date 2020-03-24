import threading
import setproctitle

from modi._executor_task import ExecutorTask


class ExecutorThread(threading.Thread):
    """
    :param queue serial_write_q: Inter-process queue for serial writing message
    :param queue json_recv_q: Inter-process queue for receiving json message
    :param dict() module_ids: dict() of module_id : ['timestamp', 'uuid']
    :param list() modules: list() of module instance
    """

    def __init__(self, modules, module_ids, topology_data,
                 can_read_q, can_write_q, init_event, nb_modules):
        super(ExecutorThread, self).__init__()
        self.__exe_task = ExecutorTask(
            modules, module_ids, topology_data, can_read_q, can_write_q, init_event, nb_modules)
        self.__stop = threading.Event()

        setproctitle.setproctitle('pymodi-executor')

    def run(self):
        """ Run executor task
        """
        self.__exe_task.init_modules()
        while not self.stopped():
            self.__exe_task.run()

    def stop(self):
        """ Stop executor task
        """
        
        self.__stop.set()
        print('stop set : ',self.__stop)

    def stopped(self):
        """ Check executor task status
        """

        return self.__stop.is_set()
