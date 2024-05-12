from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QMutexLocker, QObject
        

class Worker(QThread):
    ''' 
    - Takes a single function to be runned multiple times with different parameters.
    - Emits a signal with the result of each finished run
    - Emits a signal when all runs are done
    '''
    taskComplete = pyqtSignal(object)  # Signal with task output
    finished = pyqtSignal()  # Signal when all tasks are done
    onError = pyqtSignal(str)  # Signal when an error occurs

    def __init__(self, function):
        super().__init__()
        self.tasks = []
        self.total = 1
        self.current = 0
        self.mutex = QMutex()
        self.infoMutex = QMutex()
        if not callable(function):
            raise Exception("Function must be callable")
        self.function = function


    def progressBarString(self):
        ''' Returns a string with a progress bar '''
        progress = self.progress()
        return f"[{'='*progress}{' '*(100-progress)}] {progress}% ({self.current}/{self.total})"

    def progress(self):
        ''' Returns the progress of the current task in percentage 0-100'''
        with QMutexLocker(self.infoMutex):
            return (self.current * 100) // self.total

    def cancel(self):
        ''' Cancels all tasks '''
        with QMutexLocker(self.mutex):
            self.tasks = []
        with QMutexLocker(self.infoMutex):
            self.total = 1
            self.current = 0


    def disconnectAll(self):
        try:
            self.taskComplete.disconnect()
            self.finished.disconnect()
            self.onError.disconnect()
        except:
            pass

    
    def add_task(self, task_args):
        ''' Adds a task to the worker '''
        with QMutexLocker(self.mutex):
            if isinstance(task_args, list):
                self.tasks.extend(task_args)
            else:
                self.tasks.append(task_args)
        with QMutexLocker(self.infoMutex):
            self.total = len(self.tasks)

    def run(self):
        with QMutexLocker(self.infoMutex):
            self.current = 0
        while True:
            task_args = None
            with QMutexLocker(self.mutex):
                if len(self.tasks) > 0:
                    task_args = self.tasks.pop(0)
                else:
                    break
            out = None
            try:
                out = self.function(*task_args)
            except Exception as e:
                self.onError.emit(str(e))

            with QMutexLocker(self.infoMutex):
                self.current += 1

            self.taskComplete.emit(out)


        with QMutexLocker(self.infoMutex):
            self.current = self.total
        self.finished.emit()