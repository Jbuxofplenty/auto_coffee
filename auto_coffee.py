#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
# import RPi.GPIO as GPIO
import threading
import time
import json

hostName = "0.0.0.0"
serverPort = 8080

# Used to shut down threads if another request is sent
exit_event = threading.Event()

class MyServer(BaseHTTPRequestHandler):
	def __init__(self, *args, **kwargs):
		self.FLOW_SENSOR = 17
		self.IN_SOLENOID_VALVE = 19
		self.OUT_SOLENOID_VALVE = 20
		self.LINEAR_ACTUATOR = 21
		self.config = self.LoadConfig()
		super().__init__(*args, **kwargs)

	def do_GET(self):
		if self.path == "/coffee" or self.path == "/Coffee":
			exit_event.clear()
			self.SendWebpage(f'Making some coffee homeboy.')
			in_flow = self.config["coffee"]["in_flow_time"]
			out_flow = self.config["coffee"]["out_flow_time"]
			time_to_boil = self.config["coffee"]["time_to_boil"]
			self.SendWebpage(f'In flow: {in_flow}, Out flow: {out_flow}, Time to Boil: {time_to_boil}', False)
			self.MakeCoffeeOrTea(in_flow, out_flow, time_to_boil)
			self.SendWebpage(f'Finished.', False)
		elif self.path == "/tea" or self.path == "/Tea":
			exit_event.clear()
			self.SendWebpage(f'Making some tea homeboy.')
			in_flow = self.config["tea"]["in_flow_time"]
			out_flow = self.config["tea"]["out_flow_time"]
			time_to_boil = self.config["tea"]["time_to_boil"]
			self.SendWebpage(f'In flow: {in_flow}, Out flow: {out_flow}, Time to Boil: {time_to_boil}', False)
			self.MakeCoffeeOrTea(in_flow, out_flow, time_to_boil)
			self.SendWebpage(f'Finished.', False)
		elif self.path == "/favicon.ico":
			return
		else:
			self.SendWebpage(f'Did not recognize the request. Append /tea or /coffee to the path immediately after the address/port specification.')
			self.SendWebpage(f'Restarting server...', False)
			self.Reset()
			exit_event.set()

	def do_POST(self):
		content_length = int(self.headers['Content-Length'])
		body = self.rfile.read(content_length)
		json_body = json.loads(body.decode('utf-8'))
		if self.path == "/in":
			exit_event.clear()
			control_time = float(json_body['time'])
			self.OpenInput(control_time)
			self.SendWebpage(f'Will open the input solenoid valve for {control_time} seconds.')
		elif self.path == "/out":
			exit_event.clear()
			control_time = float(json_body['time'])
			self.OpenOutput(control_time)
			self.SendWebpage(f'Will open the output solenoid valve for {control_time} seconds.')
		elif self.path == "/set/coffee/in_flow":
			exit_event.clear()
			control_time = float(json_body['time'])
			self.config["coffee"]["in_flow_time"] = control_time
			self.SaveConfig()
			self.SendWebpage(f'Saved coffee inflow time to {control_time} seconds.')
		elif self.path == "/set/coffee/out_flow":
			exit_event.clear()
			control_time = float(json_body['time'])
			self.config["coffee"]["out_flow_time"] = control_time
			self.SaveConfig()
			self.SendWebpage(f'Saved coffee out flow time to {control_time} seconds.')
		elif self.path == "/set/coffee/time_to_boil":
			exit_event.clear()
			control_time = float(json_body['time'])
			self.config["coffee"]["time_to_boil"] = control_time
			self.SaveConfig()
			self.SendWebpage(f'Saved coffee time to boil to {control_time} seconds.')
		elif self.path == "/set/tea/in_flow":
			exit_event.clear()
			control_time = float(json_body['time'])
			self.config["tea"]["in_flow_time"] = control_time
			self.SaveConfig()
			self.SendWebpage(f'Saved tea inflow time to {control_time} seconds.')
		elif self.path == "/set/tea/out_flow":
			exit_event.clear()
			control_time = float(json_body['time'])
			self.config["tea"]["out_flow_time"] = control_time
			self.SaveConfig()
			self.SendWebpage(f'Saved tea out flow time to {control_time} seconds.')
		elif self.path == "/set/tea/time_to_boil":
			exit_event.clear()
			control_time = float(json_body['time'])
			self.config["tea"]["time_to_boil"] = control_time
			self.SaveConfig()
			self.SendWebpage(f'Saved tea time to boil to {control_time} seconds.')
		else:
			self.SendWebpage(f'Did not recognize the request. Append /in or /out to the path immediately after the address/port specification.')
			self.SendWebpage(f'Restarting server...', False)
			self.Reset()
			exit_event.set()

	def LoadConfig(self):
		with open("config.json") as json_file:
			return json.load(json_file)

	def SaveConfig(self):
		with open("config.json", "w") as write_file:
			json.dump(self.config, write_file)

	def SendWebpage(self, message, header=True):
		# Send webpage to user to let them know we're working on it
		self.send_response(200)
		if header: 
			self.send_header("Content-type", "text/html")
			self.end_headers()
			self.wfile.write(bytes("<html><head><title>Make Some Coffee/Tea</title></head>", "utf-8"))
		self.wfile.write(bytes("<body>", "utf-8"))
		self.wfile.write(bytes(f"<p>{message}</p>", "utf-8"))
		self.wfile.write(bytes("</body></html>", "utf-8"))
		print(message)
				
	def OpenInput(self, in_flow_time):
		# Setup the GPIO pins
		self.SetupGPIO()
		self.SendWebpage('Filling the hot water heater...', False)
		
		# Open the solenoid valve
		GPIO.output(self.IN_SOLENOID_VALVE, GPIO.HIGH)
		self.ThreadSleep(in_flow_time)
		
		# Reset sensors
		GPIO.output(self.IN_SOLENOID_VALVE, GPIO.LOW)

		# Reset
		self.Reset()
		# Notify the user their liquid is ready
		self.SendWebpage(f'Finished.', False)
				
	def OpenOutput(self, out_flow_time):
		# Setup the GPIO pins
		self.SetupGPIO()
		self.SendWebpage('Pouring the hot water...', False)
		
		# Open the solenoid valve
		GPIO.output(self.OUT_SOLENOID_VALVE, GPIO.HIGH)
		self.ThreadSleep(out_flow_time)
		
		# Reset sensors
		GPIO.output(self.OUT_SOLENOID_VALVE, GPIO.LOW)

		# Reset
		self.Reset()
		# Notify the user their liquid is ready
		self.SendWebpage(f'Finished.', False)

	# Callback to update the global count variable when signals
	# are sent to the GPIO pin via the flow meter
	def CountPulse(self, channel):
		self.count = self.count+1

		# Divisor converts pulses to volume.  Will probably need to adjust
		# in the future
		self.flow = self.count / (60 * 5)

		print("Current flow: ", self.flow)
		
	def FillHotWaterHeater(self, in_flow_time):	
		self.SendWebpage('Filling the hot water heater...', False)

		# Set the class variables used for the flow sensor
		self.count = 0
		self.flow = 0
		
		# Open the solenoid valve
		GPIO.output(self.IN_SOLENOID_VALVE, GPIO.HIGH)

		# Wait until a liter of water has been poured
		# safety_count = 0 # Auto-turn off after 20 seconds
		# while self.flow < 5 and safety_count < 40:
		# 	time.sleep(0.5)
		# 	safety_count += 1
		self.ThreadSleep(in_flow_time)
			
		# Reset counters
		self.flow = 0
		self.count = 0
		
		# Reset sensors
		GPIO.output(self.IN_SOLENOID_VALVE, GPIO.LOW)
				
	def HeatWater(self):
		self.SendWebpage('Heating the water...', False)

		# Push out the linear actuator to activate the heating
		# circuit on the hot water heater
		GPIO.output(self.LINEAR_ACTUATOR, GPIO.HIGH)

		# Not really necessary to wait this long
		self.ThreadSleep(5)

		# Disengage
		GPIO.output(self.LINEAR_ACTUATOR, GPIO.LOW)
				
	def PourHotWater(self, out_flow_time):
		self.SendWebpage('Pouring the hot water...', False)

		# Open the solenoid valve to allow water to drop into the container
		GPIO.output(self.OUT_SOLENOID_VALVE, GPIO.HIGH)

		# Keep it open until the container is filled
		self.ThreadSleep(out_flow_time)

		# Close solenoid valve
		GPIO.output(self.OUT_SOLENOID_VALVE, GPIO.LOW)
				
	def MakeCoffeeOrTea(self, in_flow_time, out_flow_time, time_to_boil):
		# Setup the GPIO pins
		self.SetupGPIO()
		# Fill the hot water heater
		self.FillHotWaterHeater(in_flow_time)
		# Wait 2 seconds
		self.ThreadSleep(2)
		# Heat water
		self.HeatWater()
		# Wait until the water is boiled
		self.ThreadSleep(time_to_boil)
		# Pour the water
		self.PourHotWater(out_flow_time)
		# Reset
		self.Reset()
		# Notify the user their liquid is ready
		self.SendWebpage(f'Finished.', False)
			
	def ThreadSleep(self, sleep_time):
		for i in range(int(sleep_time*100)):
			if exit_event.is_set():
				self.Reset()
				quit()
			time.sleep(0.01)

	def Reset(self):
		# Necessary if there was an error during execution
		self.SetupGPIO()

		# Set all the GPIO pins to their default values
		GPIO.output(self.IN_SOLENOID_VALVE, GPIO.LOW)
		GPIO.output(self.OUT_SOLENOID_VALVE, GPIO.LOW)
		GPIO.output(self.LINEAR_ACTUATOR, GPIO.LOW)
		GPIO.remove_event_detect(self.FLOW_SENSOR)

		# Cleanup
		GPIO.cleanup()

	def SetupGPIO(self):
		# Cleanup in case an error occurred during execution
		GPIO.cleanup()
		GPIO.setmode(GPIO.BCM)
		
		# GPIO pin setup
		GPIO.setup(self.IN_SOLENOID_VALVE, GPIO.OUT)
		GPIO.setup(self.LINEAR_ACTUATOR, GPIO.OUT)
		GPIO.setup(self.OUT_SOLENOID_VALVE, GPIO.OUT)
		GPIO.setup(self.FLOW_SENSOR, GPIO.IN, pull_up_down = GPIO.PUD_UP)
		GPIO.add_event_detect(self.FLOW_SENSOR, GPIO.FALLING, callback=self.CountPulse)


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

if __name__ == "__main__":
	# Necessary due to the correct handling of interrupt signals
	# GPIO.setwarnings(False)

	webServer = ThreadedHTTPServer((hostName, serverPort), MyServer)
	while True:
		try:
			exit_event.clear()
			thread = threading.Thread(target=webServer.serve_forever)
			thread.start()
			print("Server started http://%s:%s" % (hostName, serverPort))
			exit_event.wait()
			webServer.shutdown()
		except KeyboardInterrupt:
			print('Shutting server down...')
			exit_event.set()
			# Allow for some time for the thread to exit cleanly
			time.sleep(1)
			webServer.shutdown()
			quit()
