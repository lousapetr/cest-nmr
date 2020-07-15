import radio

import Tkinter

from math import *
import re
import os
import string
import popen2

import pyutil
import sparky
import sputil
import tkutil


class s3e_dialog(tkutil.Dialog, tkutil.Stoppable):


  def __init__(self, session):

    self.s3e_root = os.getcwd()
    self.filenames = [[],[]]
    self.session = session
    self.project = session.project

    tkutil.Dialog.__init__(self, session.tk, 'S3E Spectra Processing')

    f = Tkinter.Frame(self.top)
    f.pack(side = 'top', anchor = 'w')

    r = 0

    w1 = Tkinter.Label(f, text = 'Input ser-files')
    w1.grid(row = r, column = 0)
    r = r + 1

    self.spectrum_choice_minus = sputil.spectrum_menu(session, self.top, 'Spectrum (-): ')
    self.spectrum_choice_minus.frame.pack(side = 'top', anchor = 'w')
    r = r + 1

    self.spectrum_choice_plus = sputil.spectrum_menu(session, self.top, 'Spectrum (+): ')
    self.spectrum_choice_plus.frame.pack(side = 'top', anchor = 'w')
    r = r + 1


    asp = tkutil.file_field(f, 'Alpha ser-file: ', 'serfile', width = 60)
    asp.frame.grid(row = r, column = '0', sticky = 'e')
    asp.set(os.getcwd())
    self.a_ser_path = asp
    r = r + 1

    bsp = tkutil.file_field(f, 'Beta ser-file:  ', 'serfile', width = 60)
    bsp.frame.grid(row = r, column = '0', sticky = 'e')
    bsp.set(os.getcwd())
    self.b_ser_path = bsp
    r = r + 1

# ----------------------------------------------------------------------------
# BEGIN SPECTRA HANDLING DIALOG
# ----------------------------------------------------------------------------
#    
    hbutton = tkutil.checkbutton(self.top, 'Show spectra handling dialog', 0)
    hbutton.button.pack(side = 'top', anchor = 'w')

    spectra_handling_dialog = Tkinter.Frame(self.top)
    spectra_handling_dialog.pack(side = 'top', anchor = 'w')

    self.hz_range_widget = [None, None]
    cr = tkutil.entry_row(spectra_handling_dialog, 'Sumation range [Hz]: ',
                          ('min', '1', 3), ('max', '1.4', 3), ('step', '0.1', 3))
    (self.hz_range_widget[0],
     self.hz_range_widget[1],
     self.hz_step_widget) = cr.variables
    cr.frame.pack(side = 'top', anchor = 'w')

    hod = Tkinter.Frame(spectra_handling_dialog)
    hod.pack(side = 'top', anchor = 'w')

    w6 = Tkinter.Label(hod, text = 'Spectra handling output:')
    w6.pack(side = 'top', anchor = 'nw')
    
    ho = tkutil.scrolling_text(hod, height = 9, width = 100)
    ho.frame.pack(side = 'top', anchor = 'nw')
    self.handling_output = ho.text

    #
    spectra_assign_dialog = Tkinter.Frame(self.top)
    spectra_assign_dialog.pack(side = 'top', anchor = 'w')

    spectra_assign_widget = Tkinter.Frame(spectra_assign_dialog)
    spectra_assign_widget.pack(side = 'top', anchor = 'w')

    aod = Tkinter.Frame(spectra_assign_widget)
    aod.pack(side = 'top', anchor = 'w')

    ao = tkutil.scrolling_text(aod, height = 9, width = 77)
    ao.frame.pack(side = 'top', anchor = 'nw')
    self.assign_output = ao.text
    #

    pobr = tkutil.button_row(spectra_handling_dialog,
			     ('Combine spectra', self.handle_spectra_cb),
			     ('Clear handling output', self.clear_handling_output_cb),
			     ('Quit', self.close_cb))
    pobr.frame.pack()


    hbutton.show_widget_cb(spectra_handling_dialog, None)
    hbutton.map_widget(spectra_handling_dialog)
#
# ----------------------------------------------------------------------------
# END SPECTRA HANDLING DIALOG
# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# BEGIN COUPLINGS EVALUATION DIALOG
# ----------------------------------------------------------------------------
#    
    ebutton = tkutil.checkbutton(self.top, 'Show couplings evaluation dialog', 0)
    ebutton.button.pack(side = 'top', anchor = 'w')

    couplings_evaluation_dialog = Tkinter.Frame(self.top)
    couplings_evaluation_dialog.pack(side = 'top', anchor = 'w')

    fph = tkutil.entry_field(couplings_evaluation_dialog, 'Fit in ', '90.0', 9, '% of peak height')
    fph.frame.pack(side = 'top', anchor = 'w')
    self.fit_peak_height = fph.variable

    peak_fitting_method_dialog = Tkinter.Frame(couplings_evaluation_dialog)
    peak_fitting_method_dialog.pack(anchor = 'w')
    
    self.peak_fitting_method = Tkinter.StringVar(peak_fitting_method_dialog)
    self.peak_fitting_method.set('pi')
    
    pfm = Tkinter.Label(peak_fitting_method_dialog, text = 'Peak fitting method')
    pfm.grid(row = 0, column = 0, sticky = 'w')
    pirb = Tkinter.Radiobutton(peak_fitting_method_dialog, text = 'pi', variable = self.peak_fitting_method, value = 'pi', highlightthickness = 0, command = self.update_peak_fitting_method)
    pirb.grid(row = 0, column = 1, sticky = 'w')
    pcrb = Tkinter.Radiobutton(peak_fitting_method_dialog, text = 'pc', variable = self.peak_fitting_method, value = 'pc', highlightthickness = 0, command = self.update_peak_fitting_method)
    pcrb.grid(row = 0, column = 2, sticky = 'w')
    
    eobr = tkutil.button_row(couplings_evaluation_dialog,
			     ('Fit peaks', self.fit_peaks_cb),
			     ('Plot couplings', self.plot_couplings_cb),
			     ('Quit', self.close_cb))
    eobr.frame.pack()

    ebutton.show_widget_cb(couplings_evaluation_dialog, None)
    ebutton.map_widget(couplings_evaluation_dialog)

#
# ----------------------------------------------------------------------------
# END COUPLINGS EVALUATION DIALOG
# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------
#
  def write_file(self, path, mode, content, write_heading = 0):
    
    if path:
      file = open(path, mode)
      if write_heading and self.heading:
	file.write(self.heading['text'] + '\n')
      file.write(content)
      file.close()
    
# ----------------------------------------------------------------------------
#
  def read_file(self, path, mode):
    
    f = open(path, mode)
    file = f.read()
    f.close()
    return file
    
    
# ----------------------------------------------------------------------------
#

  def read_parameters_cb(self):
    
    if self.a_ser_path.get():
      self.read_parameters()

# ----------------------------------------------------------------------------
#

# ----------------------------------------------------------------------------
#

# ----------------------------------------------------------------------------
#
# ----------------------------------------------------------------------------
#
  def apply_cb(self):

    if self.a_ser_path.get():
      if self.b_ser_path.get():
        if self.a_ser_path.get() != self.b_ser_path.get():
	  if self.fid_com.get(1.0, 'end') != '\n':
	    self.apply()
	  else:
            self.conversion_output.insert('end', 'Please fill in the "Conversion script for bruk2pipe"\n')
        else:
          self.conversion_output.insert('end', 'WARNING !!! You have specified the same filename for the "Alpha ser-file" and the "Beta ser-file"\n')
      else:
        self.conversion_output.insert('end', 'Please specify the "Beta ser-file" path\n')
    else:
      self.conversion_output.insert('end', 'Please specify the "Alpha ser-file" path\n')

# ----------------------------------------------------------------------------
#
  def apply(self):

    self.conversion_output.insert('end', 'Conversion of the alpha ser-file:\n')
    output = self.execute_script(self.get_path(self.a_ser_path.get()), 'fid.com', 
                                                    self.fid_com.get(1.0, 'end'))
    self.conversion_output.insert('end', output[0] + output[1])
    self.conversion_output.insert('end', '\n')
    self.conversion_output.insert('end', '\n')
    
    self.conversion_output.insert('end', 'Conversion of the beta ser-file:\n')
    output = self.execute_script(self.get_path(self.b_ser_path.get()), 'fid.com', 
                                                    self.fid_com.get(1.0, 'end'))
    self.conversion_output.insert('end', output[0] + output[1])
    self.conversion_output.insert('end', '\n')
    self.conversion_output.insert('end', '\n')

# ----------------------------------------------------------------------------
#
  def update_peak_fitting_method(self):
    
    pass
    
# ----------------------------------------------------------------------------
#
  def handle_spectra_cb(self):

    if self.a_ser_path.get():
      if self.b_ser_path.get():
            self.handle_spectra()
      else:
        self.handling_output.insert('end', 'Please specify the "Beta ser-file" path\n')
    else:
      self.handling_output.insert('end', 'Please specify the "Alpha ser-file" path\n')

# ----------------------------------------------------------------------------
#
  def handle_spectra(self):
    
    J = float(self.hz_range_widget[0].get())
    

    #print 'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'
    #print self.get_path(self.a_ser_path.get())
    #print self.spectrum_choice_plus.spectrum()
    #print self.spectrum_choice_plus.spectrum().save_path
    #print 'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'

    self.filenames = [[],[]]
    self.filenames[0] = self.filenames[0] + [(self.spectrum_choice_plus.spectrum().save_path)]
    self.filenames[1] = self.filenames[1] + [(self.spectrum_choice_minus.spectrum().save_path)]
    
    self.jecka=[]

    while J <= float(self.hz_range_widget[1].get()):
      
      self.combine_spectra(self.handling_output,
             self.get_path(self.a_ser_path.get()) + '1.dat',
             self.get_path(self.b_ser_path.get()) + '2.dat',
	     self.get_path(self.a_ser_path.get()) + '1p2_' + string.zfill('%3.2f' % J, 4)  + '.ft2',
	     c1 = J,
	     trailer = ' for coupling ' + string.zfill('%3.2f' % J, 4) + ' Hz')

      self.filenames[0] = self.filenames[0] + [self.get_path(self.a_ser_path.get()) + '1p2_' + string.zfill('%3.2f' % J, 4) ]
     
      self.combine_spectra(self.handling_output,
             self.get_path(self.a_ser_path.get()) + '1.dat',
             self.get_path(self.b_ser_path.get()) + '2.dat',
	     self.get_path(self.a_ser_path.get()) + '1m2_' + string.zfill('%3.2f' % J, 4)  + '.ft2',
	     c1 = -J,
	     trailer = ' for coupling ' + string.zfill('%3.2f' % J, 4) + ' Hz')

      self.filenames[1] = self.filenames[1] + [self.get_path(self.a_ser_path.get()) + '1m2_' + string.zfill('%3.2f' % J, 4) ]
   
      #			     ('Assign alpha-spectrum + Save', self.assign_alpha_cb),
      #			     ('Copy alpha assignement', self.copy_alpha_assignement_cb),
      #			     ('Assign beta-spectrum', self.assign_beta_cb),
      #			     ('Copy beta assignement', self.copy_beta_assignement_cb),
      #			     ('Save spectra', self.save_spectra_cb)


      self.jecka.append(J)
      J = J + float(self.hz_step_widget.get())

    self.copy_alpha_assignement_cb()
    self.copy_beta_assignement_cb()

# ----------------------------------------------------------------------------
#
  def combine_spectra(self, output_widget, inName1, inName2, outName, Action = 'add', c1 = 1.0, c2 = 1.0, trailer = ''):
    
    output_widget.insert('end', 'Combining spectra in ratio '
                          + string.zfill('%5.3f' % c1, 4) 
			  + ':'
			  + string.zfill('%5.3f' % c2, 4))
    if trailer != '':
      output_widget.insert('end', trailer)
    output_widget.insert('end', ' ... ')
    if os.access(outName, os.R_OK) == True:
      output_widget.insert('end', 'FOUND\n')
    else:
      output = self.addNMR(inName1, inName2, outName, Action, c1, c2)
      if output[1]:
        output_widget.insert('end', 'ERROR:\n' + output[0] + output[1])
      else:
        output_widget.insert('end', 'OK\n')
    
    ucsf_file = re.compile("(?P<name>.*)""(?P<suffix>\.ft2$)").search(outName).group('name') + '.ucsf'

    output_widget.insert('end', 'Conversion of spectrum to UCSF-format ... ')
    if os.access(ucsf_file, os.R_OK) == True:
      output_widget.insert('end', 'FOUND\n')
    else:
      output = self.pipe2ucsf(outName, ucsf_file)
      if output[1]:
        output_widget.insert('end', 'ERROR:\n' + output[0] + output[1])
      else:
        output_widget.insert('end', 'OK\n')


# ----------------------------------------------------------------------------
#
  def addNMR(self, inName1, inName2, outName, Action, c1, c2):
    
#    r, w, e = popen2.popen3('csh')
    r, w, e = popen2.popen3('bash')
    
#    w.write('source /home/nmr/software/nmrpipe/com/nmrInit.linux.com\n')
    #w.write('. /packages/run/modules-2.0/init/bash\n')
    #w.write('module add nmrpipe\n')
    w.write('cd ' + self.get_path(inName1) + '\n')
    w.write('addNMR -in1 ' + inName1 + ' -in2 ' + inName2 + ' -out ' + outName + ' -' + Action + ' -c1 ' + `c1` + ' -c2 ' + `c2` + '\n')
    print 'addNMR -in1 ' + inName1 + ' -in2 ' + inName2 + ' -out ' + outName + ' -' + Action + ' -c1 ' + `c1` + ' -c2 ' + `c2` + '\n'
    w.write('exit\n')
    
    w.close()
    
    stdout = r.read()
    stderr = e.read()
    
    r.close()
    e.close()
    
    return stdout, stderr
    
# ----------------------------------------------------------------------------
#
  def pipe2ucsf(self, pipe_file, ucsf_file):

#    r, w, e = popen2.popen3('csh')
    r, w, e = popen2.popen3('bash')
    
    ucsf_file_3d=ucsf_file + '_3d'

    w.write('pipe2ucsf ' + pipe_file + ' ' + ucsf_file_3d + '\n')
    w.write('ucsfdata -p2 -o ' + ucsf_file + ' ' + ucsf_file_3d + '\n')
#    w.write('rm ' + ucsf_file_3d + '\n')
    w.write('exit\n')
    
    w.close()
    
    stdout = r.read()
    stderr = e.read()
    
    r.close()
    e.close()
    
    return stdout, stderr
  



#################################################################################################################

#################################################################################################################

#################################################################################################################
#################################################################################################################

#################################################################################################################

#################################################################################################################





# ----------------------------------------------------------------------------
#
  def clear_handling_output_cb(self):
    
    self.handling_output.delete(1.0, 'end')

# ----------------------------------------------------------------------------
#
# ----------------------------------------------------------------------------
#
  def make_saves_cb(self):

    if self.a_ser_path.get():
      if self.filenames[0]:
        if os.access(self.filenames[0][0] + '.save', os.R_OK) == True:
	  self.make_saves()
        else:
          print "AAAAAAAAAAAAA"      
          print  self.filenames[0][0] + '.save'     
          print "AAAAAAAAAAAAA"      
          self.assign_output.insert('end', 'Alpha spectrum save not found\n')
      else:
        self.assign_output.insert('end', 'Please combine the spectra first before making saves\n')
    else:
      self.assign_output.insert('end', 'Please specify the "Alpha ser-file" path\n')

# ----------------------------------------------------------------------------
#
  def make_saves(self):

    save = self.read_file(self.filenames[0][0] + '.save', 'r')

    ornament = re.compile("(?<=<ornament>\n)(.*\n)*(?=<end ornament>)").search(save).group(0)
    template_save = string.replace(save, ornament, '')
    
    for subspectrum in self.filenames:
      for filename in subspectrum:
	save = string.replace(template_save,
	                 self.get_filename(self.filenames[0][0]),
		         self.get_filename(filename))
        old_pathname = re.compile("(?<=pathname ).*(?=\n)").search(save).group(0)
	save = string.replace(save, old_pathname, filename + '.ucsf')
	save = string.replace(save, 'integrate.methods 1 0 1', 'integrate.methods 1 0 0')
	save = string.replace(save, 'integrate.adjust_linewidths 1', 'integrate.adjust_linewidths 0')
	save = string.replace(save, 'integrate.fit_baseline 0', 'integrate.fit_baseline 0')
	save = string.replace(save, 'integrate.motion_range 0.040 0.010', 'integrate.motion_range 0.40 0.10')
        self.write_file(filename + '.save', 'w', save)

# ----------------------------------------------------------------------------
#
# ----------------------------------------------------------------------------
#
# ----------------------------------------------------------------------------
#
  def copy_alpha_assignement_cb(self):

    if self.a_ser_path.get():
      if self.filenames[0]:
        #if os.access(self.filenames[0][0] , os.R_OK) == True:
	#  save = self.read_file(self.filenames[0][0] , 'r')
 	self.copy_alpha_assignement()
        #else:
        #  print "aaaaaaaaaaaaa"      
        #  print  self.filenames[0][0] + '.save'     
        #  print "aaaaaaaaaaaaa"      
        #  self.assign_output.insert('end', 'Alpha spectrum save not found\n')
      else:
        self.assign_output.insert('end', 'Please combine the spectra first before making saves\n')
    else:
      self.assign_output.insert('end', 'Please specify the "Alpha ser-file" path\n')

# ----------------------------------------------------------------------------
#
  def copy_alpha_assignement(self):

    save = self.read_file(self.filenames[0][0] , 'r')

    #ornament = re.compile("(?<=<ornament>\n)(.*\n)*(?=<end ornament>)").search(save).group(0)
    #template_save = string.replace(save, ornament, '')
    template_save=save
    
    subspectrum = self.filenames[0]
    for filename in subspectrum[1:]:
      save = string.replace(template_save,
                       self.get_filename(self.filenames[0][0]),
      	         self.get_filename(filename))
      old_pathname = re.compile("(?<=pathname ).*(?=\n)").search(save).group(0)
      save_cur = string.replace(save, old_pathname, filename + '.ucsf')
      new_name= re.compile(".*\/").sub('',filename)
      old_name = re.compile("(?!path)(?<=name ).*(?=\n)").search(save_cur).group(0)
      save = string.replace(save, old_pathname, filename + '.ucsf')
      save = re.compile("\nname .*(?=\n)").sub('\nname ' + new_name,save)
      save = string.replace(save, 'integrate.methods 1 0 1', 'integrate.methods 1 0 1')
      save = string.replace(save, 'integrate.adjust_linewidths 1', 'integrate.adjust_linewidths 0')
      save = string.replace(save, 'integrate.fit_baseline 0', 'integrate.fit_baseline 0')
      save = string.replace(save, 'integrate.motion_range 0.040 0.010', 'integrate.motion_range 0.40 0.10')
      self.write_file(filename + '.save', 'w', save)

    for id in range(1, len(self.filenames[0])):
      self.session.open_spectrum(self.filenames[0][id] + '.save')
#      for peak in self.project.spectrum_list()[id - 1].peak_list():
#	new_spectrum = self.session.project.spectrum_list()[id]
#        new_spectrum.place_peak(peak.position)
#        self.assign_peak(new_spectrum.peak_list()[len(new_spectrum.peak_list()) - 1], peak.assignment)

# ----------------------------------------------------------------------------
#
  def assign_peak(self, peak, assignement):

    peak_assignement = self.get_peak_assignement(assignement)
    
    for i in range(2):
      peak.assign(i, peak_assignement[0], peak_assignement[1][i])

    peak.show_assignment_label()
    peak.center()
    
# ----------------------------------------------------------------------------
#
  def get_peak_assignement(self, assignement):

    rv = re.compile("(?P<residue>\D*\d*)(?P<w1>\D*\d*(')?)-(?P<w2>\D*\d*(')?)").search(assignement)
    residue = rv.group('residue')
    w = [rv.group('w1'), rv.group('w2')]

    return residue, w

# ----------------------------------------------------------------------------
#
  def assign_beta_cb(self):

    if self.b_ser_path.get():
      if self.filenames[1]:
        if os.access(self.filenames[1][0] + '.ucsf', os.R_OK) == True:
	  self.assign_beta(self.filenames[1][0] + '.save')
        else:
          self.assign_output.insert('end', 'Beta spectrum save not found\n')
      else:
        self.assign_output.insert('end', 'Please combine the spectra first before making saves\n')
    else:
      self.assign_output.insert('end', 'Please specify the "Beta ser-file" path\n')

# ----------------------------------------------------------------------------
#
  def assign_beta(self, beta_name):

    self.assign_output.insert('end', 'Assign spectrum and using `fa` save the spectrum as ' + self.filenames[1][0] + '.save\n')
    if os.access(self.filenames[1][0] + '.save', os.R_OK) == True:
      self.session.open_spectrum(self.filenames[1][0] + '.save')
    else:
      self.create_beta_save()
      self.session.open_spectrum(self.filenames[1][0] + '.save')
      for peak in self.project.spectrum_list()[0].peak_list():
        new_spectrum = self.project.spectrum_list()[len(self.project.spectrum_list()) - 1]
        new_spectrum.place_peak(peak.position)
        self.assign_peak(new_spectrum.peak_list()[len(new_spectrum.peak_list()) - 1], peak.assignment)

# ----------------------------------------------------------------------------
#
  def create_beta_save(self):

    save = self.read_file(self.filenames[0][0] + '.save', 'r')

    ornament = re.compile("(?<=<ornament>\n)(.*\n)*(?=<end ornament>)").search(save).group(0)
    template_save = string.replace(save, ornament, '')
    
    subspectrum = self.filenames[1]
    filename = subspectrum[0]
    save = string.replace(template_save,
                     self.get_filename(self.filenames[0][0]),
    	         self.get_filename(filename))
    old_pathname = re.compile("(?<=pathname ).*(?=\n)").search(save).group(0)
    save = string.replace(save, old_pathname, filename + '.ucsf')
    save = string.replace(save, 'integrate.methods 1 0 1', 'integrate.methods 1 0 1')
    save = string.replace(save, 'integrate.adjust_linewidths 1', 'integrate.adjust_linewidths 0')
    save = string.replace(save, 'integrate.fit_baseline 0', 'integrate.fit_baseline 0')
    save = string.replace(save, 'integrate.motion_range 0.040 0.010', 'integrate.motion_range 0.40 0.10')
    self.write_file(filename + '.save', 'w', save)

# ----------------------------------------------------------------------------
#
  def copy_beta_assignement_cb(self):

    if self.b_ser_path.get():
      if self.filenames[1]:
 	  self.copy_beta_assignement()
      else:
        self.assign_output.insert('end', 'Please combine the spectra first before making saves\n')
    else:
      self.assign_output.insert('end', 'Please specify the "Beta ser-file" path\n')

# ----------------------------------------------------------------------------
#
  def copy_beta_assignement(self):

    save = self.read_file(self.filenames[1][0] , 'r')

    #ornament = re.compile("(?<=<ornament>\n)(.*\n)*(?=<end ornament>)").search(save).group(0)
    #template_save = string.replace(save, ornament, '')
    
    template_save = save
    
    subspectrum = self.filenames[1]
    for filename in subspectrum[1:]:
      save = string.replace(template_save,
                       self.get_filename(self.filenames[1][0]),
      	         self.get_filename(filename))
      old_pathname = re.compile("(?<=pathname ).*(?=\n)").search(save).group(0)
      save_cur = string.replace(save, old_pathname, filename + '.ucsf')
      new_name= re.compile(".*\/").sub('',filename)
      old_name = re.compile("(?!path)(?<=name ).*(?=\n)").search(save_cur).group(0)
      save = string.replace(save, old_pathname, filename + '.ucsf')
      save = re.compile("\nname .*(?=\n)").sub('\nname ' + new_name,save)
      save = string.replace(save, 'integrate.methods 1 0 1', 'integrate.methods 1 0 1')
      save = string.replace(save, 'integrate.adjust_linewidths 1', 'integrate.adjust_linewidths 0')
      save = string.replace(save, 'integrate.fit_baseline 0', 'integrate.fit_baseline 0')
      save = string.replace(save, 'integrate.motion_range 0.040 0.010', 'integrate.motion_range 0.40 0.10')
      self.write_file(filename + '.save', 'w', save)

    for id in range(1, len(self.filenames[1])):
      self.session.open_spectrum(self.filenames[1][id] + '.save')
#      for peak in self.project.spectrum_list()[id + len(self.filenames[1]) - 1].peak_list():
#	new_spectrum = self.project.spectrum_list()[id + len(self.filenames[1])]
#        new_spectrum.place_peak(peak.position)
#        self.assign_peak(new_spectrum.peak_list()[len(new_spectrum.peak_list()) - 1], peak.assignment)

# ----------------------------------------------------------------------------
#
  def save_spectra_cb(self):

    self.session.command_characters('js')

# ----------------------------------------------------------------------------
#
  def fit_peaks_cb(self):

    if not self.fit_peak_height.get():
      self.fit_peak_height.set('90.0')

    peak_fitting_method = self.peak_fitting_method.get()
    if peak_fitting_method == 'pi':
      self.fit_peaks()
    else:
      if peak_fitting_method == 'pc':
        self.center_peaks()

# ----------------------------------------------------------------------------
#
  def fit_peaks(self):

    residues = []
    for residue in range(len(self.project.spectrum_list()[0].peak_list())):
      residues.append([])
      for coup in range(len(self.filenames[0])):
        residues[residue].append([])

    self.view_tmp=[]
    view_buff = 0
    
    for spectrum_no in range(1,len(self.filenames[0])):
      for subspectrum_no in range(len(self.filenames)):
        self.filenames[subspectrum_no][spectrum_no]=self.filenames[subspectrum_no][spectrum_no] + '.save'
    

    for spectrum_no in range(1,len(self.filenames[0])):
      for subspectrum_no in range(len(self.filenames)):
	template_save = self.read_file(self.filenames[subspectrum_no][spectrum_no], 'r')
        positive_treshold = re.compile("(?<=contour.pos\ )(?P<contourlevel>\d+)\ +(?P<treshold>\d+(\.\d+e(\+|\-)\d+)?)(.*)\n*").search(template_save).group('treshold')
        negative_treshold = re.compile("(?<=contour.neg\ )(?P<contourlevel>\d+)\ +(?P<treshold>-\d+(\.\d+e(\+|\-)\d+)?)(.*)\n*").search(template_save).group('treshold')
	spectrum = self.project.spectrum_list()[spectrum_no + 1 + (len(self.filenames[0]) - 1) * subspectrum_no]

        if subspectrum_no==0:
        	spectrum2 = self.project.spectrum_list()[spectrum_no + 1 + (len(self.filenames[0]) - 1)]
        else:
        	spectrum2 = self.project.spectrum_list()[spectrum_no + 1 ]

        for peak in spectrum.peak_list():
	  peak_id = spectrum.peak_list().index(peak)
          views = self.session.project.view_list()
          treshold = peak.data_height * (float(self.fit_peak_height.get()) / 100.0)
          save = string.replace(template_save, positive_treshold, `treshold`, 1)
          save = string.replace(template_save, negative_treshold, `treshold`, 1)
          self.write_file(self.get_path(self.a_ser_path.get()) + peak.spectrum.name + '_' + peak.assignment + '_' + peak.label.text + '.save', 'w', save)
	  self.session.open_spectrum(self.get_path(self.a_ser_path.get()) + peak.spectrum.name + '_' + peak.assignment + '_' + peak.label.text + '.save')
          views = self.session.project.view_list()
	  last_view = views[len(views) - 1]
	  fitted_peak = last_view.spectrum.peak_list()[peak_id]
	  fitted_peak.fit(last_view)
	  rv = re.compile("(?P<subspectrum>\S+)_(?P<ratio>\d+\.\d*)").search(peak.spectrum.name)
	  peak_info = self.get_peak_assignement(peak.assignment), rv.group('subspectrum'), float(rv.group('ratio')), peak.label.text,

          position2=[]
          for dimension in range(len(fitted_peak.position)):
	    position = fitted_peak.position[dimension]
	    peak_info = peak_info + ('%9.3f' % position,)
            position2.append(position)

	  height = fitted_peak.data_height
          height2 = spectrum2.data_height((position2[0],position2[1]))
	  peak_info = peak_info + ( height,)
	  peak_info = peak_info + ( height2,)
          residues[peak_id][spectrum_no].append(peak_info)
	  #self.session.close_spectrum(self.get_path(self.a_ser_path.get()) + peak.spectrum.name + '_' + peak.assignment + '_' + peak.label.text + '.save')
          if view_buff: view_buff.destroy()
          view_buff = last_view
    if view_buff:
      view_buff.destroy()
    self.residues = residues
 

# ----------------------------------------------------------------------------
#
  def center_peaks(self):

    residues = []
    for residue in range(len(self.project.spectrum_list()[0].peak_list())):
      residues.append([])
      for coup in range(len(self.filenames[0])):
        residues[residue].append([])

    self.view_tmp=[]
    view_buff = 0
    
    for spectrum_no in range(1,len(self.filenames[0])):
      for subspectrum_no in range(len(self.filenames)):
        self.filenames[subspectrum_no][spectrum_no]=self.filenames[subspectrum_no][spectrum_no] + '.save'
    

    for spectrum_no in range(1,len(self.filenames[0])):
      for subspectrum_no in range(len(self.filenames)):
	template_save = self.read_file(self.filenames[subspectrum_no][spectrum_no], 'r')
        positive_treshold = re.compile("(?<=contour.pos\ )(?P<contourlevel>\d+)\ +(?P<treshold>\d+(\.\d+e(\+|\-)\d+)?)(.*)\n*").search(template_save).group('treshold')
        negative_treshold = re.compile("(?<=contour.neg\ )(?P<contourlevel>\d+)\ +(?P<treshold>-\d+(\.\d+e(\+|\-)\d+)?)(.*)\n*").search(template_save).group('treshold')
	spectrum = self.project.spectrum_list()[spectrum_no + 1 + (len(self.filenames[0]) - 1) * subspectrum_no]

        if subspectrum_no==0:
        	spectrum2 = self.project.spectrum_list()[spectrum_no + 1 + (len(self.filenames[0]) - 1)]
        else:
        	spectrum2 = self.project.spectrum_list()[spectrum_no + 1 ]

        for peak in spectrum.peak_list():
	  peak_id = spectrum.peak_list().index(peak)
          views = self.session.project.view_list()
          treshold = peak.data_height * (float(self.fit_peak_height.get()) / 100.0)
          save = string.replace(template_save, positive_treshold, `treshold`, 1)
          save = string.replace(template_save, negative_treshold, `treshold`, 1)
          self.write_file(self.get_path(self.a_ser_path.get()) + peak.spectrum.name + '_' + peak.assignment + '_' + peak.label.text + '.save', 'w', save)
	  self.session.open_spectrum(self.get_path(self.a_ser_path.get()) + peak.spectrum.name + '_' + peak.assignment + '_' + peak.label.text + '.save')
          views = self.session.project.view_list()
	  last_view = views[len(views) - 1]
	  fitted_peak = last_view.spectrum.peak_list()[peak_id]
	  fitted_peak.center()
	  rv = re.compile("(?P<subspectrum>\S+)_(?P<ratio>\d+\.\d*)").search(peak.spectrum.name)
	  peak_info = self.get_peak_assignement(peak.assignment), rv.group('subspectrum'), float(rv.group('ratio')), peak.label.text,

          position2=[]
          for dimension in range(len(fitted_peak.position)):
	    position = fitted_peak.position[dimension]
	    peak_info = peak_info + ('%9.3f' % position,)
            position2.append(position)

	  height = fitted_peak.data_height
          height2 = spectrum2.data_height((position2[0],position2[1]))
	  peak_info = peak_info + ( height,)
	  peak_info = peak_info + ( height2,)
          residues[peak_id][spectrum_no].append(peak_info)
	  #self.session.close_spectrum(self.get_path(self.a_ser_path.get()) + peak.spectrum.name + '_' + peak.assignment + '_' + peak.label.text + '.save')
          if view_buff: view_buff.destroy()
          view_buff = last_view
    if view_buff:
      view_buff.destroy()
    self.residues = residues
 

#  def center_peaks(self):
#
#    residues = []
#    for residue in range(len(self.project.spectrum_list()[0].peak_list())):
#      residues.append([])
#      for coup in range(len(self.filenames[0])):
#        residues[residue].append([])
#
#    self.view_tmp=[]
#    view_buff = 0
#    
#    for spectrum_no in range(len(self.filenames[0]))[1:]:
#      for subspectrum_no in range(len(self.filenames)):
#	template_save = self.read_file(self.filenames[subspectrum_no][spectrum_no] + '.save', 'r')
#        positive_treshold = re.compile("(?<=contour.pos\ )(?P<contourlevel>\d+)\ +(?P<treshold>\d+(\.\d+e(\+|\-)\d+)?)(.*)\n*").search(template_save).group('treshold')
#        negative_treshold = re.compile("(?<=contour.neg\ )(?P<contourlevel>\d+)\ +(?P<treshold>-\d+(\.\d+e(\+|\-)\d+)?)(.*)\n*").search(template_save).group('treshold')
#	spectrum = self.project.spectrum_list()[spectrum_no + len(self.filenames[0]) * subspectrum_no]
#        for peak in spectrum.peak_list():
#	  peak_id = spectrum.peak_list().index(peak)
#          treshold = peak.data_height * (float(self.fit_peak_height.get()) / 100.0)
#          save = string.replace(template_save, positive_treshold, `treshold`, 1)
#          save = string.replace(template_save, negative_treshold, `treshold`, 1)
#          self.write_file(self.get_path(self.a_ser_path.get()) + peak.spectrum.name + '_' + peak.assignment + '.save', 'w', save)
#	  self.session.open_spectrum(self.get_path(self.a_ser_path.get()) + peak.spectrum.name + '_' + peak.assignment + '.save')
#          views = self.session.project.view_list()
#	  last_view = views[len(views) - 1]
#	  fitted_peak = last_view.spectrum.peak_list()[peak_id]
#	  fitted_peak.center()
#	  rv = re.compile("(?P<subspectrum>\D+)(?P<hz>\d+\.\d+)_(?P<ratio>.*$)").search(peak.spectrum.name)
#	  peak_info = self.get_peak_assignement(peak.assignment), rv.group('subspectrum'), rv.group('hz'),
#          for dimension in range(len(fitted_peak.position)):
#	    position = fitted_peak.data_height[dimension]
#	    peak_info = peak_info + ('%9.3f' % position,)
#          residues[peak_id][spectrum_no].append(peak_info)
#          if view_buff: view_buff.destroy()
#          view_buff = last_view
#    if view_buff: view_buff.destroy()
#    self.residues = residues
# 
# ----------------------------------------------------------------------------
#
  def clear_assign_output_cb(self):
    
    self.assign_output.delete(1.0, 'end')

# ----------------------------------------------------------------------------
#
  def read_peaks_positions_cb(self):
    
    for view in self.view_tmp:
      view.destroy()
          
# ----------------------------------------------------------------------------
#
  def evaluate_couplings_cb(self):

    self.couplings = ('#combination_factor\t1p2:\tN15ppm\tH1ppm\tdata_height\tdata_height_at_same_position_in_1m2\t1m2:\tN15ppm\tH1ppm\tdata_height\tdata_height_at_same_position_in_1p2\n')
    self.couplings = self.couplings +  ('#assignment\tlabel\tintersect according to position of 1p2 peak in 1m2 spectra, coefitients of peak height dependence (a+k*b) 1p2 in 1p2 spectra:a\t b\t 1m2 in 1m2: a\tb\t  peak height in 1p2 \t peak height in 1m2 \t ratio: 1p2/1m2 \t')
    self.couplings = self.couplings +  ('intersect according to position of 1m2 peak in 1p2 spectra, coefitients of peak height dependence (a+k*b) 1p2 in 1p2 spectra:a\t b\t 1m2 in 1m2: a\tb\t  peak height in 1p2 \t peak height in 1m2 \t ratio: 1p2/1m2 \n')
    for residue in range(len(self.residues)):
      self.couplings = self.couplings + ('# ' + self.residues[residue][1][0][0][0] + ' ' 
        + self.residues[residue][1][0][3])

      # search of zero intersect
      first_1m2=self.residues[residue][1][0][7]
      first_1p2=self.residues[residue][1][1][7]
      reached_1m2=0;
      reached_1p2=0;
      #if first_1m2<0:  
      #       for hz in range(2,len(self.residues[residue])):
      #         if float(self.residues[residue][hz][0][7])>=0:
      #            a0=(float(self.residues[residue][hz][0][7])-float(self.residues[residue][hz-1][0][7]))/(float(self.residues[residue][hz][0][2])-float(self.residues[residue][hz-1][0][2]))
      #            b0=float(self.residues[residue][hz][0][7])-a0*float(self.residues[residue][hz][0][2])
      #            optim0=-b0/a0
      #
      #            a0=(float(self.residues[residue][hz][0][6])-float(self.residues[residue][hz-1][0][6]))/(float(self.residues[residue][hz][0][2])-float(self.residues[residue][hz-1][0][2]))
      #            b0=float(self.residues[residue][hz][0][6])-a0*float(self.residues[residue][hz][0][2])
      #            a1=(float(self.residues[residue][hz][1][6])-float(self.residues[residue][hz-1][1][6]))/(float(self.residues[residue][hz][0][2])-float(self.residues[residue][hz-1][0][2]))
      #            b1=float(self.residues[residue][hz][1][6])-a1*float(self.residues[residue][hz][1][2])
      #
      #            self.couplings = self.couplings + ( ' ' + optim0 + ' ' + a0 + ' ' + b0 + ' ' + a1  + ' ' + b1 + ' ' + (optim0*a0+b0)/(optim0*a1+b1))
      #
      #            break
      if first_1m2<0:  
             for hz in range(2,len(self.residues[residue])):
               if self.residues[residue][hz][0][7]>=0:
                  a0=(self.residues[residue][hz][0][7]-self.residues[residue][hz-1][0][7])/(self.residues[residue][hz][0][2]-self.residues[residue][hz-1][0][2])
                  b0=self.residues[residue][hz][0][7]-a0*self.residues[residue][hz][0][2]
                  optim0=-b0/a0

                  a0=(self.residues[residue][hz][0][6]-self.residues[residue][hz-1][0][6])/(self.residues[residue][hz][0][2]-self.residues[residue][hz-1][0][2])
                  b0=self.residues[residue][hz][0][6]-a0*self.residues[residue][hz][0][2]
                  a1=(self.residues[residue][hz][1][6]-self.residues[residue][hz-1][1][6])/(self.residues[residue][hz][0][2]-self.residues[residue][hz-1][0][2])
                  b1=self.residues[residue][hz][1][6]-a1*self.residues[residue][hz][1][2]
                  reached_1m2=1;

                  self.couplings = self.couplings + ( ' ' + ('%9.3f' % optim0) + ' ' + ('%9.3f' % a0) + ' ' + ('%9.3f' % b0) + ' ' + ('%9.3f' % a1)  + ' ' + ('%9.3f' % b1) + ' ' + ('%9.3f' % (optim0*a0+b0)) + ' ' + ' ' + ('%9.3f' % (optim0*a1+b1)) +  ('%9.3f' %  ((optim0*a0+b0)/(optim0*a1+b1))))
      
                  break
             if reached_1m2==0:
                  a0=(self.residues[residue][hz][0][7]-self.residues[residue][hz-1][0][7])/(self.residues[residue][hz][0][2]-self.residues[residue][hz-1][0][2])
                  b0=self.residues[residue][hz][0][7]-a0*self.residues[residue][hz][0][2]
                  optim0=-b0/a0

                  a0=(self.residues[residue][hz][0][6]-self.residues[residue][hz-1][0][6])/(self.residues[residue][hz][0][2]-self.residues[residue][hz-1][0][2])
                  b0=self.residues[residue][hz][0][6]-a0*self.residues[residue][hz][0][2]
                  a1=(self.residues[residue][hz][1][6]-self.residues[residue][hz-1][1][6])/(self.residues[residue][hz][0][2]-self.residues[residue][hz-1][0][2])
                  b1=self.residues[residue][hz][1][6]-a1*self.residues[residue][hz][1][2]

                  self.couplings = self.couplings + ( ' ' + ('%9.3f' % optim0) + ' ' + ('%9.3f' % a0) + ' ' + ('%9.3f' % b0) + ' ' + ('%9.3f' % a1)  + ' ' + ('%9.3f' % b1) + ' ' + ('%9.3f' % (optim0*a0+b0)) + ' ' + ('%9.3f' % (optim0*a1+b1)) + ' ' + ('%9.3f' %  ((optim0*a0+b0)/(optim0*a1+b1))))
      


      if first_1m2>0:  
             for hz in range(2,len(self.residues[residue])):
                if self.residues[residue][hz][0][7]<=0:
                  a0=(self.residues[residue][hz][0][7]-self.residues[residue][hz-1][0][7])/(self.residues[residue][hz][0][2]-self.residues[residue][hz-1][0][2])
                  b0=self.residues[residue][hz][0][7]-a0*self.residues[residue][hz][0][2]
                  optim0=-b0/a0
      
                  a0=(self.residues[residue][hz][0][6]-self.residues[residue][hz-1][0][6])/(self.residues[residue][hz][0][2]-self.residues[residue][hz-1][0][2])
                  b0=self.residues[residue][hz][0][6]-a0*self.residues[residue][hz][0][2]
                  a1=(self.residues[residue][hz][1][6]-self.residues[residue][hz-1][1][6])/(self.residues[residue][hz][0][2]-self.residues[residue][hz-1][0][2])
                  b1=self.residues[residue][hz][1][6]-a1*self.residues[residue][hz][1][2]
                  reached_1m2=1;
      
                  self.couplings = self.couplings + ( ' ' + ('%9.3f' % optim0) + ' ' + ('%9.3f' % a0) + ' ' + ('%9.3f' % b0) + ' ' + ('%9.3f' % a1)  + ' ' + ('%9.3f' % b1) + ' ' + ('%9.3f' % (optim0*a0+b0)) + ' ' + ('%9.3f' % (optim0*a1+b1)) + ' ' + ('%9.3f' %  ((optim0*a0+b0)/(optim0*a1+b1))))
      
                  break
             if reached_1m2==0:
                  a0=(self.residues[residue][hz][0][7]-self.residues[residue][hz-1][0][7])/(self.residues[residue][hz][0][2]-self.residues[residue][hz-1][0][2])
                  b0=self.residues[residue][hz][0][7]-a0*self.residues[residue][hz][0][2]
                  optim0=-b0/a0
      
                  a0=(self.residues[residue][hz][0][6]-self.residues[residue][hz-1][0][6])/(self.residues[residue][hz][0][2]-self.residues[residue][hz-1][0][2])
                  b0=self.residues[residue][hz][0][6]-a0*self.residues[residue][hz][0][2]
                  a1=(self.residues[residue][hz][1][6]-self.residues[residue][hz-1][1][6])/(self.residues[residue][hz][0][2]-self.residues[residue][hz-1][0][2])
                  b1=self.residues[residue][hz][1][6]-a1*self.residues[residue][hz][1][2]
      
                  self.couplings = self.couplings + ( ' ' + ('%9.3f' % optim0) + ' ' + ('%9.3f' % a0) + ' ' + ('%9.3f' % b0) + ' ' + ('%9.3f' % a1)  + ' ' + ('%9.3f' % b1)  + ' ' + ('%9.3f' % (optim0*a0+b0)) + ' ' + ('%9.3f' % (optim0*a1+b1)) + ' ' + ('%9.3f' %  ((optim0*a0+b0)/(optim0*a1+b1))))
      
      


      if first_1m2==0:  
              a0=(self.residues[residue][2][0][6]-self.residues[residue][1][0][6])/(self.residues[residue][2][0][2]-self.residues[residue][1][0][2])
              b0=self.residues[residue][2][0][6]-a0*self.residues[residue][2][0][2]
              a1=(self.residues[residue][2][1][6]-self.residues[residue][1][1][6])/(self.residues[residue][2][0][2]-self.residues[residue][1][0][2])
              b1=self.residues[residue][2][1][6]-a1*self.residues[residue][2][1][2]
              self.couplings = self.couplings + ( ' ' + ('%9.3f' % self.residues[residue][1][0][2]) + ' ' + ('%9.3f' % a0) + ' ' + ('%9.3f' % b0) + ' ' + ('%9.3f' % a1) + ' '  + ('%9.3f' % b1) + ' ' + ('%9.3f' % (self.residues[residue][1][0][6]))  + ' ' + ('%9.3f' % (self.residues[residue][1][1][6])) + ' ' + ('%9.3f' % (self.residues[residue][1][0][6]/self.residues[residue][1][1][6])) )
      
      
      if first_1p2<0:  
             for hz in range(2,len(self.residues[residue])):
                if self.residues[residue][hz][1][7]>=0:
                  a1=(self.residues[residue][hz][1][7]-self.residues[residue][hz-1][1][7])/(self.residues[residue][hz][0][2]-self.residues[residue][hz-1][0][2])
                  b1=self.residues[residue][hz][1][7]-a1*self.residues[residue][hz][1][2]
                  optim1=-b1/a1
      
                  a0=(self.residues[residue][hz][0][6]-self.residues[residue][hz-1][0][6])/(self.residues[residue][hz][0][2]-self.residues[residue][hz-1][0][2])
                  b0=self.residues[residue][hz][0][6]-a0*self.residues[residue][hz][0][2]
                  a1=(self.residues[residue][hz][1][6]-self.residues[residue][hz-1][1][6])/(self.residues[residue][hz][0][2]-self.residues[residue][hz-1][0][2])
                  b1=self.residues[residue][hz][1][6]-a1*self.residues[residue][hz][1][2]
                  reached_1p2=1;
      
                  self.couplings = self.couplings + (' ' + ('%9.3f' % optim1) + ' ' + ('%9.3f' % a0) + ' ' + ('%9.3f' % b0) + ' ' + ('%9.3f' % a1) +  ' ' + ('%9.3f' % b1)  + ' ' + ('%9.3f' % (optim1*a0+b0)) + ' ' + ('%9.3f' % (optim1*a1+b1)) + ' ' + ('%9.3f' % ((optim1*a0+b0)/(optim1*a1+b1))) + '\n')
      
                  break
             if reached_1p2==0:
                  a1=(self.residues[residue][hz][1][7]-self.residues[residue][hz-1][1][7])/(self.residues[residue][hz][0][2]-self.residues[residue][hz-1][0][2])
                  b1=self.residues[residue][hz][1][7]-a1*self.residues[residue][hz][1][2]
                  optim1=-b1/a1
      
                  a0=(self.residues[residue][hz][0][6]-self.residues[residue][hz-1][0][6])/(self.residues[residue][hz][0][2]-self.residues[residue][hz-1][0][2])
                  b0=self.residues[residue][hz][0][6]-a0*self.residues[residue][hz][0][2]
                  a1=(self.residues[residue][hz][1][6]-self.residues[residue][hz-1][1][6])/(self.residues[residue][hz][0][2]-self.residues[residue][hz-1][0][2])
                  b1=self.residues[residue][hz][1][6]-a1*self.residues[residue][hz][1][2]
      
                  self.couplings = self.couplings + (' ' + ('%9.3f' % optim1) + ' ' + ('%9.3f' % a0) + ' ' + ('%9.3f' % b0) + ' ' + ('%9.3f' % a1) +  ' ' + ('%9.3f' % b1) + ' ' + ('%9.3f' % (optim1*a0+b0)) + ' ' + ('%9.3f' % (optim1*a1+b1)) + ' ' + ('%9.3f' % ((optim1*a0+b0)/(optim1*a1+b1))) + '\n')
      


      if first_1p2>0:  
              for hz in range(2,len(self.residues[residue])):
                if self.residues[residue][hz][1][7]<=0:
                  a1=(self.residues[residue][hz][1][7]-self.residues[residue][hz-1][1][7])/(self.residues[residue][hz][0][2]-self.residues[residue][hz-1][0][2])
                  b1=self.residues[residue][hz][1][7]-a1*self.residues[residue][hz][1][2]
                  optim1=-b1/a1
      
                  a0=(self.residues[residue][hz][0][6]-self.residues[residue][hz-1][0][6])/(self.residues[residue][hz][0][2]-self.residues[residue][hz-1][0][2])
                  b0=self.residues[residue][hz][0][6]-a0*self.residues[residue][hz][0][2]
                  a1=(self.residues[residue][hz][1][6]-self.residues[residue][hz-1][1][6])/(self.residues[residue][hz][0][2]-self.residues[residue][hz-1][0][2])
                  b1=self.residues[residue][hz][1][6]-a1*self.residues[residue][hz][1][2]
                  reached_1p2=1;
      
                  self.couplings = self.couplings + (' ' + ('%9.3f' % optim1) + ' ' + ('%9.3f' % a0) + ' ' + ('%9.3f' % b0) + ' ' + ('%9.3f' % a1) + ' ' + ('%9.3f' % b1) + ' ' + ('%9.3f' % (optim1*a0+b0)) + ' ' + ('%9.3f' % (optim1*a1+b1)) + ' ' + ('%9.3f' % ((optim1*a0+b0)/(optim1*a1+b1))) + '\n')
      
                  break
              if reached_1p2==0:
                  a1=(self.residues[residue][hz][1][7]-self.residues[residue][hz-1][1][7])/(self.residues[residue][hz][0][2]-self.residues[residue][hz-1][0][2])
                  b1=self.residues[residue][hz][1][7]-a1*self.residues[residue][hz][1][2]
                  optim1=-b1/a1
      
                  a0=(self.residues[residue][hz][0][6]-self.residues[residue][hz-1][0][6])/(self.residues[residue][hz][0][2]-self.residues[residue][hz-1][0][2])
                  b0=self.residues[residue][hz][0][6]-a0*self.residues[residue][hz][0][2]
                  a1=(self.residues[residue][hz][1][6]-self.residues[residue][hz-1][1][6])/(self.residues[residue][hz][0][2]-self.residues[residue][hz-1][0][2])
                  b1=self.residues[residue][hz][1][6]-a1*self.residues[residue][hz][1][2]
      
                  self.couplings = self.couplings + (' ' + ('%9.3f' % optim1) + ' ' + ('%9.3f' % a0) + ' ' + ('%9.3f' % b0) + ' ' + ('%9.3f' % a1) + ' ' + ('%9.3f' % b1) + ' ' + ('%9.3f' % (optim1*a0+b0)) + ' ' + ('%9.3f' % (optim1*a1+b1)) + ' ' + ('%9.3f' % ((optim1*a0+b0)/(optim1*a1+b1))) + '\n')
      
   


      if first_1p2==0:  
              reached_1p2=1;
              a0=(self.residues[residue][2][0][6]-self.residues[residue][1][0][6])/(self.residues[residue][2][0][2]-self.residues[residue][1][0][2])
              b0=self.residues[residue][2][0][6]-a0*self.residues[residue][2][0][2]
              a1=(self.residues[residue][2][1][6]-self.residues[residue][1][1][6])/(self.residues[residue][2][0][2]-self.residues[residue][1][0][2])
              b1=self.residues[residue][2][1][6]-a1*self.residues[residue][2][1][2]
              self.couplings = self.couplings + ( ' ' + ('%9.3f' % self.residues[residue][1][1][2]) + ' ' + ('%9.3f' % a0) + ' ' + ('%9.3f' % b0) + ' ' + ('%9.3f' % a1)  + ' ' + ('%9.3f' % b1) + ' ' + ('%9.3f' % (self.residues[residue][1][0][6])) + ' ' + ('%9.3f' % (self.residues[residue][1][1][6])) + ' ' + ('%9.3f' % (self.residues[residue][1][0][6]/self.residues[residue][1][1][6])) + '\n')









      for hz in range(1,len(self.residues[residue])):
	self.couplings = self.couplings + (('%9.3f' % self.residues[residue][hz][0][2]) + ' ' + self.residues[residue][hz][0][4] + ' ' + self.residues[residue][hz][0][5] + ' ' + ('%9.3f' % self.residues[residue][hz][0][6]) + ' ' + ('%9.3f' % self.residues[residue][hz][0][7]) + ' ' +
	  ('%9.3f' % self.residues[residue][hz][1][2]) + ' ' + self.residues[residue][hz][1][4] + ' ' + self.residues[residue][hz][1][5] + ' ' + ('%9.3f' % self.residues[residue][hz][1][6]) + ' ' + ('%9.3f' % self.residues[residue][hz][1][7]) + '\n')
      self.couplings = self.couplings + '\n\n'
      
    self.write_file(self.s3e_root + '/s3e_kada',
      'w', self.couplings)
    print (self.s3e_root + '/s3e_kada')

#
# ----------------------------------------------------------------------------
#
  def plot_couplings_cb(self):

    self.evaluate_couplings_cb()

    plot_size = self.get_plot_size()
    script = 'set term postscript landscape enhanced color\n'
    script = script + 'set out \"' + 's3e_kada'
    script = script + '.ps\"\n'
    script = script + 'set ytics nomirror\n'
    script = script + 'set y2tics nomirror\n'
    #script = script + 'set size square\n'
    script = script + 'f(x)=0\n'
    script = script + 'set style line 1 lt 1 lc 1 lw 1 pt 7 ps 1\n'
    script = script + 'set style line 2 lt 1 lc 3 lw 1 pt 7 ps 1\n'
    script = script + 'set style line 3 lt 0 lc 7 lw 1 pt 7 ps 1\n\n\n'
    
    for n in range(len(self.residues)):
      script = script + 'set key box\n'
      #script = script + 'set key left\n'
      script = script + 'set size 1.5,1.0\n'
      script = script + 'set multiplot\n'
      script = script + 'set ytics auto\n'
      script = script + 'set y2tics auto\n'
      script = script + 'set ytics tc lt 7\n'
      script = script + 'set y2tics tc lt 7\n'
      script = script + 'set size 0.6,0.666\n'
      script = script + 'set origin 0,0.333\n'
      script = script + 'set title "' + self.residues[n][1][0][0][0] + ' ' + self.residues[n][1][0][3] + '"\n'
      script = script + 'set ylabel "peak height"\n'
      script = script + 'plot  \"' + self.s3e_root + '/s3e_kada\" index ' + `n` + ' using 1:5  axes x1y1 title \"1p2 position in 1m2 spectrum\" ls 1 w lp ,'
      script = script + '      \"' + self.s3e_root + '/s3e_kada\" index ' + `n` + ' using 6:10 axes x1y1 title \"1m2 position in 1p2 spectrum\" ls 2 w lp ,'
      script = script + '       f(x) ls 3 w l notitle \n'

      script = script + 'unset key\n'
      script = script + '#unset title \n'
      script = script + 'set ytics 0.05\n'
      script = script + 'set y2tics 0.05\n'
      script = script + 'set ytics tc lt 1\n'
      script = script + 'set y2tics tc lt 3\n'
      script = script + 'set size 0.5,0.333\n'
      script = script + 'set origin 0,0\n'
      script = script + 'set ylabel "15N ppm"\n'
      script = script + 'plot  \"' + self.s3e_root + '/s3e_kada\" index ' + `n` + ' using 1:2 axes x1y1 title \"1m2\" ls 1 w lp ,'
      script = script + '      \"' + self.s3e_root + '/s3e_kada\" index ' + `n` + ' using 6:7 axes x1y2 title \"1p2\" ls 2 w lp \n'

      script = script + 'set origin 0.5,0\n'
      script = script + 'set ytics 0.005\n'
      script = script + 'set y2tics 0.005\n'
      script = script + 'set ytics tc lt 1\n'
      script = script + 'set y2tics tc lt 3\n'
      script = script + 'set ylabel "1H ppm"\n'
      script = script + 'plot  \"' + self.s3e_root + '/s3e_kada\" index ' + `n` + ' using 1:3 axes x1y1 title \"1m2\" ls 1 w lp ,'
      script = script + '      \"' + self.s3e_root + '/s3e_kada\" index ' + `n` + ' using 6:8 axes x1y2 title \"1p2\" ls 2 w lp \n'

      script = script + 'set size 0.4,0.666\n'
      script = script + 'set ytics auto\n'
      script = script + 'set y2tics auto\n'
      script = script + 'set ytics tc lt 1\n'
      script = script + 'set y2tics tc lt 3\n'
      script = script + 'set origin 0.6,0.333\n'
      script = script + 'set ylabel "peak height/10^{6}"\n'
      script = script + 'plot  \"' + self.s3e_root + '/s3e_kada\" index ' + `n` + ' using 1:($4/1000000) axes x1y1 title \"1m2\" ls 1 w lp ,'
      script = script + '      \"' + self.s3e_root + '/s3e_kada\" index ' + `n` + ' using 6:($9/1000000) axes x1y2 title \"1p2\" ls 2 w lp \n'

      script = script + 'set size 0.5,1.0\n'
      script = script + 'set ytics 0.1\n'
      script = script + 'set ytics tc lt 1\n'
      script = script + 'unset y2tics \n'
      script = script + 'set origin 1.0,0.0\n'
      script = script + 'set ylabel "ratio/10^{6}"\n'
      script = script + 'plot  \"' + self.s3e_root + '/s3e_kada\" index ' + `n` + ' using 1:($4/$9) axes x1y1 title \"1m2/1p2\" ls 1 w lp \n'
      script = script + 'unset multiplot\n'
      script = script + '\n'

    self.write_file(self.s3e_root + '/s3e_kada.gnu', 'w', script)

# ----------------------------------------------------------------------------
# 
  def get_plot_size(self):
    
    plot_size = [float(self.hz_range_widget[0].get()), float(self.hz_range_widget[1].get())]
    
    if self.residues:
   #  for residue in self.residues:
   #    for hz in residue:
   #      if (float(hz[0][3]) - float(hz[1][3])) < plot_size[0]:
   #        plot_size[0] = (float(hz[0][3]) - float(hz[1][3]))
   #      elif (float(hz[0][3]) - float(hz[1][3])) > plot_size[1]:
   #        plot_size[1] = (float(hz[0][3]) - float(hz[1][3]))
   #  
      return '%i' % (plot_size[0] - 1), '%i' % (int(plot_size[1]) + 1)


# ----------------------------------------------------------------------------
#
  def get_path(self, path):
    
    if path:
      rv = re.compile("(?P<path>.*/)""(?P<filename>.*$)")
      p = rv.search(path).group('path')
      return p

# ----------------------------------------------------------------------------
#
  def get_filename(self, path):
    
    if path:
      rv = re.compile("(?P<path>.*/)""(?P<filename>.*$)")
      p = rv.search(path).group('filename')
      return p

# ----------------------------------------------------------------------------
#
def show_s3e(session):
  sputil.the_dialog(s3e_dialog,session).show_window(1)
