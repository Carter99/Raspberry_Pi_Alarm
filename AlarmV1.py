
import datetime
import time
import math

#######################

def both():
	global nextState
	nextState=True
	print("Saved")

def b1():
	global hour
	hour+=1
	if hour==12:
		hour=4
	timeUpdate()
def b2():
	global mins
	mins+=10
	if mins==60:
		mins=0
	timeUpdate()
	
def timeUpdate():
	global hour, mins
	press()
	print(str(hour)+":"+str(mins))
	
def Flash():
	global hour, mins
	print(hour)
	print(mins)
	print('flash starting')
	# IMPLEMENT THE FLASHING OF THE LED STRIP FOR THE TIME.
	brightness=0.2
	for h in range(hour):
		pwmUpdate(brightness)
		time.sleep(0.3)
		pwmUpdate(0)
		time.sleep(0.3)
	time.sleep(1.5)
	for m in range(mins//10):
		pwmUpdate(brightness)
		time.sleep(0.3)
		pwmUpdate(0)
		time.sleep(0.3)
	print('flash done')	
	
def prePad(string,length):
	return "0"*(length-len(string))+string
	
def press():
	global lastPress
	lastPress=time.time()
	# IMPLEMENT A QUICK BLINK OF THE LED TO INDICATE THE PRESS HAS BEEN REGISTERED
	pwmUpdate(0.1)
	time.sleep(0.2)
	pwmUpdate(0)
	
def pwmUpdate(ratio):
	global pwm
	dutyCycle=100*ratio
	pwm.ChangeDutyCycle(dutyCycle)
#######################

GPIO.setmode(GPIO.BOARD)
button1=18
button2=22
LED=32

GPIO.setup(button1,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(button2,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED,GPIO.OUT)
pwm=GPIO.PWM(LED,100) # CONFIGURES THE PIN TO OPERATE AT 1000Hz
pwm.start(0)

hour=7
mins=30

lastPress=0
lightRampTime=600
print("Program Start")



while True:

	while GPIO.input(button1)==0 or GPIO.input(button2)==0:
		time.sleep(0.1)

	print("Entering Alarm Setting Mode")
	nextState=False

	while not(nextState):
		if time.time()>lastPress+10:
			Flash()
			lastPress=time.time()
		time.sleep(0.05)
		if GPIO.input(button1)==0:
			time.sleep(0.1)
			if (GPIO.input(button1)==0)and(GPIO.input(button2)==0):
				both()
			else:
				b1()
		elif GPIO.input(button2)==0:
			time.sleep(0.1)
			if (GPIO.input(button1)==0)and(GPIO.input(button2)==0):
				both()
			else:
				b2()
				
	print(str(hour)+":"+str(mins))
	print("Exiting Alarm Setting Mode")


	tomorrow=(datetime.date.today()+datetime.timedelta(days=1)).strftime('%Y-%m-%d ')
	alarmStr=tomorrow+prePad(str(hour),2)+":"+prePad(str(mins),2)

	alarmUnix=time.mktime(datetime.datetime.strptime(alarmStr,'%Y-%m-%d %H:%M').timetuple())

	print(alarmStr)
	print(time.time())
	print(alarmUnix)
	print(alarmUnix-time.time())

	while GPIO.input(button1)==0 or GPIO.input(button2)==0:
		time.sleep(0.1) 



	waitTime=alarmUnix-time.time()-lightRampTime
	print('Awating Alarm Time, T-'+str(waitTime)+'s...')
	time.sleep(waitTime)
	nextState=False
	print('Illumination Begining...')
	while not(nextState):
		if time.time()<alarmUnix:
			t=alarmUnix-time.time()
			Luminosity=math.exp((math.log(0.005)/lightRampTime)*t) #RANGES FROM 0-1 OVER THE COURSE OF THE 'LightRampTime' DURATION, REACHING 1 AT THE 'alarmUnix' TIMESTAMP
		else:
			Luminosity=math.floor(time.time()%2)
		pwmUpdate(Luminosity)
		
		if GPIO.input(button1)==0 or GPIO.input(button2)==0:
			nextState=True
		time.sleep(0.05)
	 
	print('Alarm Deactivated')
	pwmUpdate(0)
	time.sleep(10)
	print('Awaiting Interaction to Engage Alarm Setting Mode')
	while GPIO.input(button1)!=0 and GPIO.input(button2)!=0:
		time.sleep(0.1) 
