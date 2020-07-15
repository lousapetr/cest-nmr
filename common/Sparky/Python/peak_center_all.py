import os
import sys
import sparky
import string

#class All_peak_height:
def peak_center_all(session):
   for i in range(len(session.project.spectrum_list())):
      file=open(sparky.user_sparky_directory + "/Lists_ca/" + session.project.spectrum_list()[i].name + ".list", 'w')
      peaks_information=[]

      for j in range(len(session.project.spectrum_list()[i].peak_list())):
         session.project.spectrum_list()[i].peak_list()[j].center()
         h=session.project.spectrum_list()[i].data_height(session.project.spectrum_list()[i].peak_list()[j].position)
         l=session.project.spectrum_list()[i].peak_list()[j].label.text
         w1=session.project.spectrum_list()[i].peak_list()[j].frequency[0]
         w2=session.project.spectrum_list()[i].peak_list()[j].frequency[1]
         # 
         peaks_information.append(Peak_information(l,w1,w2,h))
      
      #spi=sort_peaks_information
      spi=sorted(peaks_information, key=lambda a:a.label)  

      #Based on peak position in each spectrum (based on its own peaks)
      #=================================================================
      for j in range(len(session.project.spectrum_list()[i].peak_list())):
         #line="%11s%14.6f%14.6f%13.0f \n" % (spi[j].label, spi[j].w1, spi[j].w2, spi[j].height)
         line="%11s%17.9f%17.9f%21.9f \n" % (spi[j].label, spi[j].w1, spi[j].w2, spi[j].height)
         file.write(line)
   
      file.close()


class Peak_information:
   def __init__(self, label, w1, w2, height):
      self.label=label
      self.w1=w1
      self.w2=w2
      self.height=height
   
   def __repr__(self):
      return repr((self.label, self.w1, self.w2, self.height))

