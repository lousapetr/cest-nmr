import os
import sys
import sparky
import string

#class All_peak_height:
def write_precisely(session):
   #session = sparky.session_list[0]
   #for i in range(len(session.project.spectrum_list())):
      f=open(sparky.user_sparky_directory + "/Lists_ha/" + session.selected_spectrum().name + ".frq", 'w')
      sfo1=session.selected_spectrum().hz_per_ppm[0]
      sfo2=session.selected_spectrum().hz_per_ppm[1]
      line="%17.9f\n%17.9f\n" % (sfo1,sfo2)
      f.write(line)
      f.close()
      file=open(sparky.user_sparky_directory + "/Lists_ha/" + session.selected_spectrum().name + ".list", 'w')
      line="      User         w1         w2     w1 (Hz)    w2 (Hz)  Data Height \n"
      file.write(line)
      line="\n"
      file.write(line)
      peaks_information=[]
      
      #Based on the peaks in the selected spectrum:
      #=================================================================
      for j in range(len(session.selected_spectrum().peak_list())):
         h=session.selected_spectrum().data_height(session.selected_spectrum().peak_list()[j].position)
         l= session.selected_spectrum().peak_list()[j].label.text
         w1=session.selected_spectrum().peak_list()[j].frequency[0]
         w2=session.selected_spectrum().peak_list()[j].frequency[1]
         hz1=w1*sfo1
         hz2=w2*sfo2

         # 
         peaks_information.append(Peak_information(l,w1,w2,hz1,hz2,h))
      
      #spi=sort_peaks_information
      spi=sorted(peaks_information, key=lambda a:a.label)  
      


      #Based on the peaks in the selected spectrum:
      #=================================================================
      for j in range(len(session.selected_spectrum().peak_list())):
         line="%11s%17.9f%17.9f%17.9f%17.9f%21.9f \n" % (spi[j].label, spi[j].w1, spi[j].w2, spi[j].hz1, spi[j].hz2, spi[j].height)
         file.write(line)
   
      file.close()

class Peak_information:
   def __init__(self, label, w1, w2, hz1, hz2, height):
      self.label=label
      self.w1=w1
      self.w2=w2
      self.hz1=hz1
      self.hz2=hz2
      self.height=height
   
   def __repr__(self):
      return repr((self.label, self.w1, self.w2, self.hz1, self.hz2, self.height))

