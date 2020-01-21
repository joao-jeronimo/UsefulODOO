#!/usr/bin/python3
# -*- coding: utf8 -*-

import pudb

class RequirementNotSatisfiedException(Exception):
    pass

class Task:
    def taskSignature(self):
        return self.__class__.__name__
    def taskReqs(self):
        return []
    # The main task routine.
    def run(self, taskMan):
        pass
    # Called after sucessfull task commit. After this is ran successfully,
    # the journal can be re-written to disk.
    def tearDown(self, taskMan):
        pass
    # Called if the TaskMan awakes while a task is being run.
    def undo(self, taskMan):
        pass

class TaskMan:
    # Current schedullable tasks:
    taskList = []
    # Currently runnign task:
    currentTask = None
    # Running tasks can add their own tasks to thie queue:
    newTasks = []
    newChildreenTasks = []
    # Signatures for tasks ran in the past - for dependencies:
    pastTasks = set()
    
    def taskMan_main(self):
        #pudb.set_trace()
        while len(self.taskList)>0 or len(self.newTasks)>0 or len(self.newChildreenTasks)>0:
            #pudb.set_trace()
            # Add more tasks to the end of the queue:
            self.taskList = self.newChildreenTasks + self.taskList + self.newTasks
            self.newChildreenTasks.clear()
            self.newTasks.clear()
            # Prepare one task to run:
            #pudb.set_trace()
            self.currentTask = self.taskList[0]
            self.taskList = self.taskList[1:]
            # Test task requirements and run task:
            requirements = self.currentTask.taskReqs()
            for thisReq in requirements:
                if thisReq not in self.pastTasks:
                    raise RequirementNotSatisfiedException()
            self.currentTask.run(self)
            # After running the task:
            self.currentTask.tearDown(self)
            self.pastTasks.add(self.currentTask.taskSignature())
            print("Task successfull: %s" % self.currentTask.taskSignature())
            self.currentTask = None
            # Save the task list:
            self.saveTaskList()
    
    def scheduleTask(self, taskfunc):
        self.newTasks.append(taskfunc)
    def scheduleChildTask(self, taskfunc):
        self.newChildreenTasks.append(taskfunc)
    
    def saveTaskList(self):
        pass
