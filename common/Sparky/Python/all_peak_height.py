import os
import sys
import sparky
import string

#class All_peak_height:
def all_peak_height(session):
   #session = sparky.session_list[0]
   for i in range(len(session.project.spectrum_list())):
      # t1rho #f=open(sparky.user_sparky_directory + "/Lists/" + session.selected_spectrum().name + ".frq", 'w')
      sfo1=session.selected_spectrum().hz_per_ppm[0]
      sfo2=session.selected_spectrum().hz_per_ppm[1]
      line="%17.9f\n%17.9f\n" % (sfo1,sfo2)
      # t1rho #f.write(line)
      # t1rho #f.close()
      file=open(sparky.user_sparky_directory + "/Lists/" + session.project.spectrum_list()[i].name + ".list", 'w')
      line="      User         w1         w2     w1 (Hz)    w2 (Hz)  Data Height \n"
      #line="      User         w1         w2   Data Height \n"
      file.write(line)
      line="\n"
      file.write(line)
      peaks_information=[]
      #Based on peak position in each spectrum (based on its own peaks)
      #=================================================================
      #for j in range(len(session.project.spectrum_list()[i].peak_list())):
      #   h=session.project.spectrum_list()[i].data_height(session.project.spectrum_list()[i].peak_list()[j].position)
      #   l=session.project.spectrum_list()[i].peak_list()[j].label.text
      #   w1=session.project.spectrum_list()[i].peak_list()[j].frequency[0]
      #   w2=session.project.spectrum_list()[i].peak_list()[j].frequency[1]
      
      #Based on the peaks in the selected spectrum:
      #=================================================================
      for j in range(len(session.selected_spectrum().peak_list())):
         h=session.project.spectrum_list()[i].data_height(session.selected_spectrum().peak_list()[j].position)
         l= session.selected_spectrum().peak_list()[j].label.text
         w1=session.selected_spectrum().peak_list()[j].frequency[0]
         w2=session.selected_spectrum().peak_list()[j].frequency[1]
         hz1=w1*sfo1
         hz2=w2*sfo2
         # 
         peaks_information.append(Peak_information(l,w1,w2,hz1,hz2,h))
         #peaks_information.append(Peak_information(l,w1,w2,h))
      
      #spi=sort_peaks_information
      #spi=sorted(peaks_information, key=lambda a:a.label)  
      #spi=peaks_information

      # sort based only on digits extracted from the label
      def residue_number(peak):
          number = ''
          number_started = False
          for char in peak.label:
              if char.isdigit():
                  number_started = True
                  number += char
              else:
                  if number_started:
                      return int(number)

      spi=sorted(peaks_information, key=residue_number)
      

      #Based on peak position in each spectrum (based on its own peaks)
      #=================================================================
      #for j in range(len(session.project.spectrum_list()[i].peak_list())):


      #Based on the peaks in the selected spectrum:
      #=================================================================
      for j in range(len(session.selected_spectrum().peak_list())):
         line="%11s%17.9f%17.9f%17.9f%17.9f%21.9f \n" % (spi[j].label, spi[j].w1, spi[j].w2, spi[j].hz1, spi[j].hz2, spi[j].height)
         #line="%11s%11.3f%11.3f%16.3f \n" % (spi[j].label, spi[j].w1, spi[j].w2, spi[j].height)
         file.write(line)
   
      file.close()

#class Peak_information:
#   def __init__(self, label, w1, w2, height):
#      self.label=label
#      self.w1=w1
#      self.w2=w2
#      self.height=height
#   
#   def __repr__(self):
#      return repr((self.label, self.w1, self.w2, self.height))

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

#def all_peak_height(session):
#   #session = sparky.session_list[0]
#   for i in range(len(session.project.spectrum_list())):
#      file=open(sparky.user_sparky_directory + "/Lists/" + session.project.spectrum_list()[i].name + ".list", 'w')
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
