import explorerhat as eh
import time

eh.motor.stop()

def accelerate(speed, tmp):
    increment = int(speed/tmp)
    base_speed=0
    for i in range(tmp):
        base_speed = base_speed + increment
        print(base_speed)
        eh.motor.forwards(base_speed)
        time.sleep(1)
    eh.motor.forwards(speed)
    
def decelerate(initial_speed, tmp, final_speed):
    decrement = int((initial_speed-final_speed)/tmp)
    base_speed = initial_speed
    for i in range(tmp):
        base_speed = base_speed - decrement
        print(base_speed)
        eh.motor.forwards(base_speed)
        time.sleep(1)
    eh.motor.forwards(final_speed)

def turn_right():
    eh.motor.one.speed(-40)
    time.sleep(0.1)
    eh.motor.two.speed(40)
    time.sleep(1)
    eh.motor.stop()
    
    
def turn_left():
    eh.motor.one.speed(40)
    time.sleep(0.1)
    eh.motor.two.speed(-40)
    time.sleep(1)
    eh.motor.stop()

time.sleep(1)

accelerate(100,3)
time.sleep(5)
decelerate(100,4,0)
print("JOB DONE")
ok=1

while ok==1:
    if eh.touch.one.is_pressed() :
        time.sleep(1)
        print("Going forward...")
        #eh.motor.forwards()
       # time.sleep(2)
        #eh.motor.stop()
        turn_left()
        #eh.motor.forwards()
        time.sleep(1)
        eh.motor.stop()
        ok=2
