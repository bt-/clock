import datetime
from clock_framework import datetimeutils
from datetimeutils import DateTimeUtils
from task import Task
import clock_framework.filters 

class TaskCollection:
    def __init__(self):
        self.tasks = []

    def exists(self, task):
        for t in self.tasks:
            if t.equals(task):
                return True
        return False

    def get_task(self, task):
        for t in self.tasks:
            if t.equals(task):
                return t
        return None

    def add_task(self, task):
        if task.is_stop(): # Do not add [Stop] tasks
            return task
        # If task already exists, add its periods
        if self.exists(task): 
            t = self.get_task(task)
            for p in task.periods:
                t.periods.append(p)
            return t

        self.tasks.append(task)
        return task

    @staticmethod
    def from_file(filename):
        try:
            file = open(filename, 'r')
            lines = [line for line in file]
        except Exception:
            lines = []
            print('Could not open file ./clock.txt')
        return TaskCollection.from_lines(lines)

    @staticmethod
    def from_lines(lines):
        collection = TaskCollection()
        current_day = datetime.datetime(1900, 1, 1)
        current_task = None
        for line in lines:
            if DateTimeUtils.is_date(line):
                current_task and current_task.discard_last()
                current_day = DateTimeUtils.get_date(line)
                current_task = None
                continue

            time = DateTimeUtils.parse_time(current_day, line[0:5])
            current_task and current_task.finish(time)
            current_task = collection.add_task(Task(line[6:].replace('\n', ''), time))

        current_task and current_task.finish(datetime.datetime.now())
        return collection


    def filter(self, filter):
        c = TaskCollection()
        c.tasks = [filter.get_task(task) for task in self.tasks if filter.is_valid(task)]
        return c

    @staticmethod
    def get_filters(options):
        filters = []
        if options.today.is_active:
            filters.append(clock_framework.filters.DateFilter(datetime.datetime.today()))
        if options.this_week.is_active:
            today = datetime.datetime.today()
            monday = today - datetime.timedelta(days=today.weekday())
            sunday = monday + datetime.timedelta(days=6)
            filters.append(clock_framework.filters.PeriodFilter(monday, sunday))
        if options.from_filter.is_active or options.to_filter.is_active:
            from_date = datetime.datetime(1900, 1, 1)
            to_date = datetime.datetime(2100, 1, 1)
            if options.from_filter.is_active:
                from_date = datetime.datetime.strptime(options.from_filter.value, '%Y-%m-%d')
            if options.to_filter.is_active:
                to_date = datetime.datetime.strptime(options.to_filter.value, '%Y-%m-%d')
            filters.append(clock_framework.filters.PeriodFilter(from_date, to_date))
        if len(options.arguments) > 0:
            filters.append(clock_framework.filters.TagFilter(options.arguments))
        return filters

