
import sched, time

class Alarm(Exception):
	pass
def raiseAlarm(exc=Alarm):
	raise exc()

runner = sched.scheduler(time.time, time.sleep)
e1 = runner.enter(1, 1, lambda: print("hi"))
print(e1)
e2 = runner.enter(2, 1, raiseAlarm)
print(e2)
e3 = runner.enter(3, 1, lambda: print("oh no"))
print(e3)
runner.run()

