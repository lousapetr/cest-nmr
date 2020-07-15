import os
import sys
import sparky
import string

#class All_peak_height:
def all_own_peak_height(session):
   #session = sparky.session_list[0]
   for i in range(len(session.project.spectrum_list())):
      file=open(sparky.user_sparky_directory + "/Lists/" + session.project.spectrum_list()[i].name + ".list", 'w')
      sfo2=session.selected_spectrum().hz_per_ppm[1]
      sfo3=session.selected_spectrum().hz_per_ppm[2]
      line="      User         w2         w3     w2 (Hz)    w3 (Hz)  Data Height \n"
      file.write(line)
      line="\n"
      file.write(line)
      peaks_information=[]
      
      #Based on the peaks in the selected spectrum:
      #=================================================================
      #for j in range(len(session.selected_spectrum().peak_list())):
      #   h=session.project.spectrum_list()[i].data_height(session.selected_spectrum().peak_list()[j].position)
      #   l= session.selected_spectrum().peak_list()[j].label.text
      #   w1=session.selected_spectrum().peak_list()[j].frequency[0]
      #   w2=session.selected_spectrum().peak_list()[j].frequency[1]
      #Based on peak position in each spectrum (based on its own peaks)
      #=================================================================
      for j in range(len(session.project.spectrum_list()[i].peak_list())):
         h=session.project.spectrum_list()[i].data_height(session.project.spectrum_list()[i].peak_list()[j].position)
         l=session.project.spectrum_list()[i].peak_list()[j].label.text
         w2=session.project.spectrum_list()[i].peak_list()[j].frequency[1]
         w3=session.project.spectrum_list()[i].peak_list()[j].frequency[2]
         hz2=w2*sfo2
         hz3=w3*sfo3
         # 
         peaks_information.append(Peak_information(l,w2,w3,hz2,hz3,h))
      
      #spi=sort_peaks_information
      spi=sorted(peaks_information, key=lambda a:a.label)  
      

      #Based on the peaks in the selected spectrum:
      #=================================================================
      #for j in range(len(session.selected_spectrum().peak_list())):


      #Based on peak position in each spectrum (based on its own peaks)
      #=================================================================
      for j in range(len(session.project.spectrum_list()[i].peak_list())):
         #line="%11s%14.6f%14.6f%13.0f \n" % (spi[j].label, spi[j].w1, spi[j].w2, spi[j].height)
         line="%11s%17.9f%17.9f%17.9f%17.9f%21.9f \n" % (spi[j].label, spi[j].w2, spi[j].w3, spi[j].hz2, spi[j].hz3, spi[j].height)
         file.write(line)
   
      file.close()

class Peak_information:
   def __init__(self, label, w2, w3, hz2, hz3, height):
      self.label=label
      self.w2=w2
      self.w3=w3
      self.hz2=hz2
      self.hz3=hz3
      self.height=height
   
   def __repr__(self):
      return repr((self.label, self.w2, self.w3, self.hz2, self.hz3, self.height))

#def all_peak_height(session):
#   #session = sparky.session_list[0]
#   for i in range(len(session.project.spectrum_list())):
#      file=open(sparky.user_sparky_directory + "/Lists_ha/" + session.project.spectrum_list()[i].name + ".list", 'w')
#      line="\tUser\tw1\tw2\tData Height\n"
#      file.write(line)
#      line="\n"
#      file.write(line)
#      for j in range(len(session.project.spectrum_list()[i].peak_list())):
#         h=session.project.spectrum_list()[i].data_height(session.project.spectrum_list()[i].peak_list()[j].position)
#         l=session.project.spectrum_list()[i].peak_list()[j].label.text
#         w1=session.project.spectrum_list()[i].peak_list()[j].frequency[0]
#         w2=session.project.spectrum_list()[i].peak_list()[j].frequency[1]
#         
#         line="%11s%11.3f%11.3f\t%13.0f\n" % (l, w1, w2, h)
#         file.write(line)
#   
#      file.close()
#
