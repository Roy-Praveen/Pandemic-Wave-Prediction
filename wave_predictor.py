import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import *
import math as mt
import scipy
import scipy.signal

dt = pd.read_csv('owid-covid-data.csv')

print(dt)
print(dt.columns)

#-------------------------------------------------------------------------------------------------------------------------
pop_den = dt.loc[dt['iso_code']=='IND','population_density']
print(pop_den)
pop_den_ind = max(pop_den)
print("Population Density of India is",pop_den_ind)


dt1 = dt.loc[dt['population_density'] >= pop_den_ind-100]
print(dt1)

#print(dt1.iso_code.unique())-----------------Prints the list of conuntries with close to population density as India

print("Poulation Density Filter has been applied")

#---------------------------------------------------------------------------------------------------------------------------

dt1['people_fully_vaccinated_per_hundred'] = dt1['people_fully_vaccinated_per_hundred'].replace(np.nan, 0)
print(dt1)

pep_vac = dt1.loc[dt1['iso_code']=='IND','people_fully_vaccinated_per_hundred'] #This should give you a value of India = 58.77
print(pep_vac)
pep_vac_per_hun = max(pep_vac)
print("People Fully Vaccinated in India per 100 Indians",pep_vac_per_hun)



dt2 = dt1.loc[dt1['people_fully_vaccinated_per_hundred'] > pep_vac_per_hun-5]
print(dt2)
dt2lis= dt2.iso_code.unique()#------------------Prints list of countries with vaccination percentage close to India

'''
dt3 = dt2.loc[dt2['people_fully_vaccinated_per_hundred'] > pep_vac_per_hun+5]
print(dt3)
dt3lis= dt3.iso_code.unique()

print(np.setdiff1d(dt2lis,dt3lis))
'''
#-----------------------------------------------------------------------------------------------------------------------------
'''
Of the countries which have vaccination percentage and population density close to India, we want to figure out the countires which have
had or having a fouth wave. 
The logic behind this exercise is to find the
	-difference in the number of days between the 3rd and 4th wave
	-difference in the distributions (slope, mean, variance)
	-compare it with India
	-predict the 4th wave and its nature with a certain level of confidence
'''
#-----------------------------------------------------------------------------------------------------------------------------
rem_ind = np.where(dt2lis == 'IND')
dt2lis = np. delete(dt2lis, rem_ind)
l = len(dt2lis)
print(l)

mod_country_lis= []

def append_func(label):
	if label == 'Include in Model':
		if dt2lis[i] not in mod_country_lis:mod_country_lis.append(dt2lis[i])
	else:
		while dt2lis[i] in mod_country_lis: mod_country_lis.remove(dt2lis[i])

for i in range(0,l):
	
	print(i)
	x = dt.loc[dt['iso_code']==dt2lis[i],'date']
	y = dt.loc[dt['iso_code']==dt2lis[i],'new_cases_smoothed']
	plt.subplot(1,2,1)
	plt.plot(x,y)
	plt.title("Include if this has had 4 waves and they are distingushable")

	x = dt.loc[dt['iso_code']=='IND','date']
	y = dt.loc[dt['iso_code']=='IND','new_cases_smoothed']
	plt.subplot(1,2,2)
	plt.plot(x,y)
	plt.title("IND")
	
	rax = plt.axes([0.81, 0.000001, 0.175, 0.075])
	sel_butt = RadioButtons(rax,['Include in Model', 'Do not include in Model'],[False,False])
	sel_butt.on_clicked(append_func)
	plt.show()
	

	
#----------------------------------------------------------------------------------------------------------------------------
#Next step is to find the 4 peaks
#Caution-- If you choose countries with more peaks or less peaks, the predictor will not work well
#So I have decided to run a search to find the best prominence for which the "find_peaks" function will give 4 peaks
#Yet you have to select the countries which have 4 peaks
#----------------------------------------------------------------------------------------------------------------------------

def peak_finder(model_country,prom):
	x = dt.loc[dt['iso_code']==model_country,'new_cases_smoothed']
	peaks = scipy.signal.find_peaks(x,prominence=prom)
	return(peaks)

def append_func3(country,peaks_list):
	peaks_list=list(peaks_list)
	new_dict = {country:peaks_list}
	print(new_dict)
	Merge(mod_count_peaks,new_dict)
	return

def append_func2(country,expr):
	expr=int(expr)
	new_dict = {country:expr}
	print(new_dict)
	Merge(mod_count_prom,new_dict)
	return

def Merge(arg1,new_dict):
    arg1.update(new_dict)
    return

print(mod_country_lis)
mod_count_prom={}
mod_count_peaks={}

#Prominence Checker
for country in mod_country_lis:
	x = dt.loc[dt['iso_code']==country,'new_cases_smoothed']
	print(x)
	max_x = round(x.max())
	min_x = 0
	for i in range(min_x,max_x,10):
		peaks,attributes = peak_finder(country,i)
		

		if len(peaks) == 4:
			append_func2(country,i)
			append_func3(country,peaks)
			break
		else:
			continue

print(mod_count_prom)
print(mod_count_peaks)

#-------------------------------------------------------------------------------------------------------------------------------
#At the final phase we are going to calulate the distance between the 1st and 2nd, 2nd and 3rd and 3rd and 4th peaks in the models 
#Compare the 1st and 2nd and 2nd and 3rd peak's distance with INDIA's and which ever country matches best is used to predict next wave 

#But since this predicts based on a single country this does not predict the peak well
#-------------------------------------------------------------------------------------------------------------------------------

x = dt.loc[dt['iso_code']=='IND','new_cases_smoothed']
print(x)
max_x = round(x.max())
min_x = 0
for i in range(min_x,max_x,10):
	peaks,attributes = peak_finder(country,i)
	peaks=list(peaks)
	if len(peaks) == 3:
		ref_dict={'IND':peaks}
		break
	else:
		continue


ind=ref_dict['IND']
ind_dist =[ind[1]-ind[0],ind[2]-ind[1]]


cou_dist = {}
for country in (mod_count_peaks.keys()):
	lis=mod_count_peaks[country]
	cou_dist[country]=[lis[1]-lis[0],lis[2]-lis[1],lis[3]-lis[2]]

'''
euc_dict={}
for country in (mod_count_peaks.keys()):
	euc_dict[country]= (ind_dist[0]-cou_dist[country][0])**2 + (ind_dist[1]-cou_dist[country][1])**2

best_model_country = min(euc_dict, key=euc_dict.get)
print(best_model_country)

print(cou_dist[best_model_country][2])

print("India will have the peak of the 4th wave %d days from the peak of the 3rd wave" %cou_dist[best_model_country][2])
'''


#--------------------------------------------------------------------------------------------------------------------------------
#The averages distance between the peaks 3 and 4
#The variance of the interpeak distances
#Thus a mean for the 4th peak and the distribution corresponding to the start of the 4th wave is given
#--------------------------------------------------------------------------------------------------------------------------------
dist_array=[]
for country in cou_dist.keys():
	dist_array.append(cou_dist[country][2])

mean  = np.average(dist_array)
variance = np.var(dist_array)
standard_Deviation = np.std(dist_array)

print('Mean:',mean,', Variance:',variance,'& Standard Devaition:',standard_Deviation)

print('Based on averages of countries which have had fourth wave, India will have the peak of the fourth wave %.f days after the 3rd wave plus or minus %.f days' % (mean,standard_Deviation))
print('At the extreme case, the 4th wave will have its peak %.f days or %.f days after the 3rd wave' % (mean-2*standard_Deviation,mean+2*standard_Deviation))


