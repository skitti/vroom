import sys
import scipy
import numpy
import matplotlib
import pandas
import sklearn
import time

from scipy.interpolate import UnivariateSpline
from pandas.tools.plotting import scatter_matrix
import matplotlib.pyplot as plt
from matplotlib.pyplot import ion, show
from itertools import islice

class Dataset():
	
	def __init__ (self,variables,tolerance, use_sampling, sampling_time):
		#self.var_choice = var_choice
		self.file = pandas.read_csv("C:\Skolan\Exjobb\Drive_KTH_Formula_Student_1december-kopia.csv")
		self.dataset = pandas.DataFrame(self.file, columns=variables)
		self.array = self.dataset.values
		self.tolerance = tolerance
		self.sampling = sampling_time
		self.X = self.array[:,0]
		self.Y1 = self.array [:,1]
		self.Y2 = self.array [:,2]
		
		if use_sampling == True:			
			sampled = pandas.DataFrame.sample(self,frac = .5, random_state=None, axis = None)
			sampled.head(20)
			#Dataset.downsample(self)
		else:
			pass
			
		Dataset.get_spline(self)
		Dataset.get_derivative(self)
		self.rakidx = Dataset.get_straight_index(self)
		Dataset.filtrering(self)
		Dataset.get_index_data(self)
	
	def downsample(self):
		self.X = list(islice(self.X,0,None,self.sampling))
		self.Y1 = list(islice(self.Y1,0,None,self.sampling))
		self.Y2 = list(islice(self.Y2,0,None,self.sampling))
		
		
	def batt_check (self):
		variables = []
		for e in range (1,16):
			battery = e
			for x in range (1,10):
				bcell = "Cell_StatusTemperature_Stack_"+str(battery)+"_Cell_"+str(x)
				variables.append(bcell)	
		return variables
		
	def get_spline(self):
		self.y_spl = UnivariateSpline(self.X,self.Y1,s=0.00005,k=3) #röd, s=0.00005 tamam
		self.y_spl1 = UnivariateSpline(self.X,self.Y2,s=0.00005,k=3)
		pass
	
	def get_derivative(self):
		self.y_prim=(self.y_spl.derivative())
		self.y2_prim =(self.y_spl1.derivative())
		#self.y1_bis = (self.y_prim.derivative())
		#self.y2_bis = (self.y2_prim.derivative())
		pandas.options.display.max_columns = 999
		print(self.y_prim (self.X))
		
		self.straight = []
		Dataset.plot(self)
		
		for r in range(len(self.y_prim(self.X))):
			if abs(self.y_prim(r))<self.tolerance:
				self.straight.append(0)
			else:
				self.straight.append(1)
		return self.straight
		
	def plot (self):
		plt.subplot(311)
		plt.ion()
		plt.plot(self.X,self.y_prim(self.X),'r',self.X,self.y2_prim(self.X), 'k')
		plt.subplot(312)
		plt.plot(self.X,self.y_spl(self.X),'r')
		plt.subplot(313)
		plt.plot(self.X,self.y_spl1(self.X),'k')
		plt.show(block=True)
		#fixa subplot vanliga kurwa
		
	def get_straight_index (self):
		self.rak = []			
		for idx, x in enumerate(self.straight):
			if x == 0:
				self.rak.append(idx)
			else:
				continue				
		counter = 0
		self.listlist = []
		self.listt = []
		while counter < len(self.rak):
			a = self.rak[counter]
			try:
				b = self.rak[counter+1]
			except IndexError:
				pass
			if a+1 == b:
				self.listt.append(a)
			else:
				self.listlist.append(self.listt)
				self.listt=[]
			counter +=1

	def filtrering (self):
		self.filtrerad = []
		for seq in self.listlist:
			if len(seq)<4:
				pass
			else:
				self.filtrerad.append(seq)	
				
	def get_index_data (self):
		counter = 0
		hastighet = []
		length = []
		for x in self.filtrerad:
			for y in x:
				hastighet.append(self.array [y,4])
				counter +=1			
			medelhastighet = sum(hastighet)/len(hastighet)
			tid = self.array[y,0]-self.array[y-len(x),0]		
			length.append(medelhastighet*tid)
		length = [ '%.2f' % elem for elem in length]
		print(length)		

def main():
	tic = time.clock()
	variables=[]
	tolerance = 0.00003 #how much can it turn to be accepted as a straight road
	use_sampling = True
	sampling_time = 4
	read_data = pandas.read_csv("C:\Skolan\Exjobb\Drive_KTH_Formula_Student_1december.csv")
	objekt = Dataset(["Time[s]","IMU_GPSLongetude","IMU_GPSLatetude[deg]","Front_Vehicle_StatusSteering_Angle_Front_Right","IMU_speedSpeed_IMU"],tolerance, use_sampling,
	sampling_time)
	objekt.filtrering()
	#print(objekt.batt_check())
	toc = time.clock()
	print("Processing time:  {0:.3f} s".format(toc-tic))
	
main()

choice = ('''Choose four variables to compare: \n
Power = "Battery_Status_2HV_Power[W]"
Speed_Imu = "IMU_speedSpeed_IMU"
Throttle = "Pedal_StatusThrottle_Pedal[%]"
Battery_Model = "MABX_SOCSOC_Batterymodel"
Battery Discharge = "MABX_SOCAh_DisCharge[Ah]"
Battery Current = "Battery_StatusHV_Battery_Current[A]"
IMU forces = "IMU_AccelerationAcceleration_X"
Steering angle = "Front_Vehicle_StatusSteering_Angle_Front_Right"
Yaw Rate = "IMU_GyroYawrate"
Longitude = "IMU_GPSLongetude"
Latitude = "IMU_GPSLatetude[deg]"
Time = "Time[s]" \n
''')
	