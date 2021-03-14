import board
import time
import digitalio
import adafruit_character_lcd.character_lcd as characterlcd
import RPi.GPIO as GPIO
import datetime
import math
import os

lcd_rs = digitalio.DigitalInOut(board.D26)
lcd_en = digitalio.DigitalInOut(board.D19)
lcd_d7 = digitalio.DigitalInOut(board.D27)
lcd_d6 = digitalio.DigitalInOut(board.D22)
lcd_d5 = digitalio.DigitalInOut(board.D24)
lcd_d4 = digitalio.DigitalInOut(board.D25)
lcd_columns = 16
lcd_rows = 2
backlight_pin=digitalio.DigitalInOut(board.D17)
lcd = characterlcd.Character_LCD_Mono(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows, backlight_pin)

button0 = digitalio.DigitalInOut(board.D21)
button1 = digitalio.DigitalInOut(board.D20)
button2 = digitalio.DigitalInOut(board.D16)
button0.switch_to_input(pull=digitalio.Pull.UP)
button1.switch_to_input(pull=digitalio.Pull.UP)
button2.switch_to_input(pull=digitalio.Pull.UP)

GPIO.setmode(GPIO.BCM)
LED=12
GPIO.setup(LED,GPIO.OUT)
pwm=GPIO.PWM(LED,100)
pwm.start(0)

lcd.create_char(1, bytes([0x0, 0x04,0x0C,0x1f,0x1f,0x0C,0x04, 0x0])) #LEFT ARROW
lcd.create_char(2, bytes([0x0, 0x04,0x06,0x1f,0x1f,0x06,0x04, 0x0])) #RIGHT ARROW

def PwmUpdate(dutyCycle):
	#
	pwm.ChangeDutyCycle(dutyCycle)

def PrePad(string,length):
	#
	return "0"*(length-len(string))+string

def ButtonCheck():
	if not(button0.value):
		return 0
	elif not(button1.value):
		return 1
	elif not(button2.value):
		return 2
	else:
		return -1

def TextUpdate():
	global page
	if page==-2:
		AlarmBlaringPage()
	elif page==-1:
		SleepPage()
	elif page==0:
		AlarmPage()
	elif page==1:
		AmbientLightPage()
	elif page==2:
		TimeSetPage()

def CursorUpdate():
	global cursorLocation
	if cursorLocation>15:
		cursorLocation=15
	elif cursorLocation<0:
		cursorLocation=0
	lcd.cursor_position(cursorLocation,1)

# Pages

# Page -2
def AlarmBlaringPage():
	lcd.backlight=1
	lcd.cursor_position(0,0)
	lcd.message="Wakey Wakey!    \nEggs and Bakey! "

# Page -1
def SleepPage():
	lcd.backlight=0
	lcd.clear()
	lcd.cursor_position(0,0)
	lcd.message = "Current Time:   \n"+datetime.datetime.today().strftime('   %H:%M        ')

# Page 0
def AlarmPage():
	global alarmHour,alarmMin,alarm
	if alarm:
		state="Armed   "
	else:
		state="Disarmed"
	lcd.cursor_position(0,0)
	lcd.message="Alarm: "+state+" \n\x01\x02 "+PrePad(str(alarmHour),2)+":"+PrePad(str(alarmMin),2)+"T       "
	CursorUpdate()

# Page 1
def AmbientLightPage():
	global lightCurve
	if brightnessIndex==0:
		brightnessMsg="0%  "
	elif brightnessIndex==1:
		brightnessMsg="20% "
	elif brightnessIndex==2:
		brightnessMsg="40% "
	elif brightnessIndex==3:
		brightnessMsg="60% "
	elif brightnessIndex==4:
		brightnessMsg="80% "
	elif brightnessIndex==5:
		brightnessMsg="100%"
	lcd.cursor_position(0,0)
	lcd.message="Light: "+brightnessMsg+"     \n\x01\x02 -+           "
	CursorUpdate()
	PwmUpdate(lightCurve[brightnessIndex])

# Page 2
def TimeSetPage():
	global systemHour,systemMin
	lcd.cursor_position(0,0)
	lcd.message="System Time:    \n\x01\x02 "+PrePad(str(systemHour),2)+":"+PrePad(str(systemMin),2)+"A      R"
	CursorUpdate()


# INITIATION VARIABLES

systemHour=10
systemMin=9
lightCurve=[0,6.25,12.5,25,50,100]
dutyCycle=0
brightnessIndex=0
cursorLocation=2
page=-1
button=-1
lcd.blink=1
lcd.cursor=1
alarmHour=7
alarmMin=30
alarm=False
alarmUnix=0
lastPress=0
lightRampUpTime=600
lightRampDownTime=90
displayOff=15


print("Starting Loop")
while True:
	button=ButtonCheck()
	if button!=-1:	# RUNS THE ENCLOSED IF THERE HAS BEEN A BUTTON PRESS
		lastPress=time.time()
		if page==-1:	# when there is a user interaction this clause will exit the page from the passive time displaying mode to page 0, the alarm setting page.
			page=0
			cursorLocation=2
			lcd.backlight=1
			CursorUpdate()
			TextUpdate()
		elif page==-2:  # when there is a user interaction this clause will exit the page from the alarm blaring mode to page 0, the alarm setting page.
			alarm=False
			page=0
			CursorUpdate()
			TextUpdate()
			deactivationTime=time.time()
			tPlus=0
			startLuminosity=100*math.exp((math.log(0.005)/lightRampUpTime)*tMinus)
			if startLuminosity>100:
				startLuminosity=100
			while tPlus<lightRampDownTime:
				tPlus=time.time()-deactivationTime
				Luminosity=startLuminosity*math.exp((math.log(0.005)/lightRampDownTime)*tPlus)
				PwmUpdate(Luminosity)
				time.sleep(0.1)
			PwmUpdate(0)
		else:
			if button==0:	# LEFT BUTTON CHECK
				cursorLocation-=1
				CursorUpdate()
			elif button==1:	# RIGHT BUTTON CHECK
				cursorLocation+=1
				CursorUpdate()
			elif button==2:	# SELECT BUTTON CHECK
				# THIS SHOULD DO STUFF TO CHANGE EITHER THE PAGE THAT THE DISPLAY IS SHOWING, OR ALTER THE CONTENT OF THE CURRENT DISPLAY
				if cursorLocation==0:
					page-=1
				elif cursorLocation==1:
					page+=1
				page%=3 	#Currently set to 3 as only really three navigatable pages [0,1,2], increase if more pages added

				if page==0:
					# Do the things that the alarm setting page would require
					if cursorLocation==3:
						alarmHour+=10
					elif cursorLocation==4:
						alarmHour+=1
					elif cursorLocation==6:
						alarmMin+=10
					elif cursorLocation==7:
						alarmMin+=1
					elif cursorLocation==8:
						alarm=not(alarm)
					alarmHour%=24
					alarmMin%=60

					tomorrow=(datetime.date.today()+datetime.timedelta(days=1)).strftime('%Y-%m-%d ')
					alarmStr=tomorrow+PrePad(str(alarmHour),2)+":"+PrePad(str(alarmMin),2)
					alarmUnix=time.mktime(datetime.datetime.strptime(alarmStr,'%Y-%m-%d %H:%M').timetuple())
					print(alarmUnix)
				elif page==1:
					# Do the things that the ambient light brighness setting page would require
					if cursorLocation==3:
						brightnessIndex-=1
					elif cursorLocation==4:
						brightnessIndex+=1
					brightnessIndex%=6
				elif page==2:
					# Do the things that the system time setting page would require
					if cursorLocation==3:
						systemHour+=10
					elif cursorLocation==4:
						systemHour+=1
					elif cursorLocation==6:
						systemMin+=10
					elif cursorLocation==7:
						systemMin+=1
					elif cursorLocation==8:
						systemString="sudo date -u 1101"+PrePad(str(systemHour),2)+PrePad(str(systemMin),2)+"21"
						alarm=False
						print(systemString)
						os.system(systemString)
					elif cursorLocation==15:
						lcd.clear()
						lcd.cursor_position(0,0)
						lcd.message = "REBOOTING       \nNOW...          "
						os.system("sudo reboot now")
						time.sleep(5)
					systemHour%=24
					systemMin%=60
				TextUpdate()
		time.sleep(0.2)

	tMinus=alarmUnix-time.time()
	if tMinus<lightRampUpTime and alarm:
		if page!=-2:
			page=-2
			TextUpdate()
		Luminosity=100*math.exp((math.log(0.005)/lightRampUpTime)*tMinus) #RANGES FROM 0-100 OVER THE COURSE OF THE 'LightRampUpTime' DURATION, REACHING 1 AT THE 'alarmUnix' TIMESTAMP
		if tMinus<0:							# Runs when the alarm time is expired whilst the user still hasn't interacted to turn it off.
			Luminosity=40*math.cos(tMinus)+60 	# Causes the light to pulse in a sinusoid pattern of period ~6.3s 
		PwmUpdate(Luminosity)
	elif time.time()>lastPress+displayOff:
		lastPress=time.time()
		systemHour=int(datetime.datetime.today().strftime('%H'))
		systemMin=int(datetime.datetime.today().strftime('%M'))
		page=-1
		TextUpdate()
	time.sleep(0.1)