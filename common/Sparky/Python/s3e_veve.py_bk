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

    SOL = '-fn SOL'
    POLY = '-fn POLY -time'
    BC_POLY = '-fn POLY -auto'
    SP = '-fn SP -off 0.5 -end 0.98 -pow 2 -c 0.5'
    EM = '-fn EM -lb '
    ZF_Auto = '-fn ZF -auto'
    ZF1_Size = '-fn ZF -size 8192'
    ZF2_Size = '-fn ZF -size 1024'
    FT_ONLY = '-fn FT'
    FT_ALT = '-fn FT -alt'
    FT_AUTO = '-fn FT -auto'
    FT_INV = '-fn FT -inv'
    FT_NEG = '-fn FT -neg'
    FT_REAL = '-fn FT -real'
    EXT_LEFT = '-fn EXT -left'
    EXT_RIGHT = '-fn EXT -right'
    EXT_MID = '-fn EXT -mid'
    EXT_XN = '-fn EXT -xn '
    EXT_X1XN = '-fn EXT -x1  -xn '

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

    asp = tkutil.file_field(f, 'Alpha ser-file: ', 'serfile', width = 60)
    asp.frame.grid(row = r, column = '0', sticky = 'e')
    asp.set(os.getcwd() + '/ser')
    self.a_ser_path = asp
    r = r + 1

    bsp = tkutil.file_field(f, 'Beta ser-file:  ', 'serfile', width = 60)
    bsp.frame.grid(row = r, column = '0', sticky = 'e')
    bsp.set(os.getcwd() + '/ser')
    self.b_ser_path = bsp
    r = r + 1

# ----------------------------------------------------------------------------
# BEGIN CONVERSION DIALOG
# ----------------------------------------------------------------------------
#
    cbutton = tkutil.checkbutton(self.top, 'Show conversion dialog', 0)
    cbutton.button.pack(side = 'top', anchor = 'w')

    conversion_dialog = Tkinter.Frame(self.top)
    conversion_dialog.pack(side = 'top', anchor = 'w')

    w2 = Tkinter.Label(conversion_dialog, text = 'Conversion script for NMRPipe')
    w2.grid(row = r, column = 0)

    w3 = Tkinter.Label(conversion_dialog, text = 'Output from conversion')
    w3.grid(row = r, column = 1)
    r = r + 1

    fc = tkutil.scrolling_text(conversion_dialog, height = 13, width = 80)
    fc.frame.grid(row = r, column = 0)
    self.fid_com = fc.text

    co = tkutil.scrolling_text(conversion_dialog, height = 13)
    co.frame.grid(row = r, column = 1)
    self.conversion_output = co.text
    r = r + 1

    fcbr = tkutil.button_row(conversion_dialog,
                             ('Load script', self.load_fid_com_cb),
                             ('Save script as', self.save_fid_com_cb),
			     ('Read bruker', self.read_parameters_cb),
			     ('Clear script', self.clear_fid_com_cb),
			     ('Apply', self.apply_cb),
			     ('Quit', self.close_cb))
    fcbr.frame.grid(row = r, column = 0)

    cobr = tkutil.button_row(conversion_dialog,
			     ('Clear output', self.clear_conversion_output_cb),
			     ('Quit', self.close_cb))
    cobr.frame.grid(row = r, column = 1)
    r = r + 1

    cbutton.show_widget_cb(conversion_dialog, None)
    cbutton.map_widget(conversion_dialog)
#
# ----------------------------------------------------------------------------
# END CONVERSION DIALOG
# ----------------------------------------------------------------------------
    
# ----------------------------------------------------------------------------
# BEGIN PROCESSING DIALOG
# ----------------------------------------------------------------------------
#    
    pbutton = tkutil.checkbutton(self.top, 'Show processing dialog', 0)
    pbutton.button.pack(side = 'top', anchor = 'w')

    processing_dialog = Tkinter.Frame(self.top)
    processing_dialog.pack(side = 'top', anchor = 'w')
    pdr = 0
   
# ----------------------------------------------------------------------------
# first column
    w4 = Tkinter.Label(processing_dialog, text = 'Processing paramaters:')
    w4.grid(row = pdr, column = 0, columnspan = 3)
    pdr = pdr + 1

    w5 = Tkinter.Label(processing_dialog, text = 'Direct dimension:')
    w5.grid(row = pdr, column = 0, columnspan = 2)
    pdr = pdr + 1

    sf = radio.button_field(processing_dialog, 'Solvent filtration method:', 0,
                             ('None', None),
			     ('SOL', SOL),
			     ('POLY', POLY))
    sf.frame.grid(row = pdr, column = 0, sticky = 'nw')
    pdr = pdr + 1
    self.solvent_filter_dialog = sf
    self.solvent_filter = sf.entry_field.variable

    ps1 = radio.phase_correction_dialog2(processing_dialog, 'Phase correction:')
    ps1.frame.grid(row = pdr, column = 0, sticky = 'nw')
    self.phase1_dialog = ps1
    pdr = pdr + 1
  
    ext0 = radio.button_field(processing_dialog, 'FID truncation:', 0,
			     ('None', None),
                             ('to xn', EXT_XN),
			     ('from x1 to xn', EXT_X1XN))
    ext0.frame.grid(row = pdr, column = 0, sticky = 'nw')
    pdr = pdr + 1
    self.extract_region0_dialog = ext0
    self.extract_region0 = ext0.entry_field.variable

    pod = Tkinter.Frame(processing_dialog)
    pod.grid(row = pdr, column = 0, rowspan = 2)
    pdr = pdr + 1
    
    w6 = Tkinter.Label(pod, text = 'Processing output:')
    w6.pack(side = 'top', anchor = 'nw')
    
    po = tkutil.scrolling_text(pod, height = 9)
    po.frame.pack(side = 'top', anchor = 'nw')
    self.processing_output = po.text
    
# ----------------------------------------------------------------------------
# second column
    pdr = 2
    
    bc1 = radio.button_field(processing_dialog, 'Baseline correction method:', 0,
                             ('None', None),
			     ('POLY', BC_POLY))
    bc1.frame.grid(row = pdr, column = 1, sticky = 'nw')
    pdr = pdr + 1
    self.baseline_correction1_dialog = bc1
    self.baseline_correction1 = bc1.entry_field.variable

    af1 = radio.button_field(processing_dialog, 'Apodization function:', 1,
                             ('None', None),
			     ('SP', SP),
			     ('EM', EM))
    af1.frame.grid(row = pdr, column = 1, sticky = 'nw')
    pdr = pdr + 1
    self.apodization_function1_dialog = af1
    self.apodization_function1 = af1.entry_field.variable

    zf1 = radio.button_field(processing_dialog, 'Zero fill options:', 1,
			     ('None', None),
                             ('auto', ZF_Auto),
			     ('size (eg. 4096, 8192)', ZF1_Size))
    zf1.frame.grid(row = pdr, column = 1, sticky = 'nw')
    pdr = pdr + 1
    self.zero_fill1_dialog = zf1
    self.zero_fill1 = zf1.entry_field.variable

    ft1 = radio.button_field(processing_dialog, 'Fourier transform options:', 0,
                             ('None', FT_ONLY),
			     ('alt', FT_ALT),
			     ('auto', FT_AUTO),
			     ('inv', FT_INV),
			     ('neg', FT_NEG),
			     ('real', FT_REAL))
    ft1.frame.grid(row = pdr, column = 1, sticky = 'nw')
    pdr = pdr + 1
    self.fourier_transform1_dialog = ft1
    self.fourier_transform1 = ft1.entry_field.variable

    ext1 = radio.button_field(processing_dialog, 'Extract region options:', 0,
			     ('None', None),
                             ('left', EXT_LEFT),
                             ('right', EXT_RIGHT),
                             ('mid', EXT_MID),
                             ('to xn', EXT_XN),
			     ('from x1 to xn', EXT_X1XN))
    ext1.frame.grid(row = pdr, column = 1, sticky = 'nw')
    pdr = pdr + 1
    self.extract_region1_dialog = ext1
    self.extract_region1 = ext1.entry_field.variable

# ----------------------------------------------------------------------------
# third column
    pdr = 1
   
    w5 = Tkinter.Label(processing_dialog, text = 'Indirect dimension:')
    w5.grid(row = pdr, column = 2)
    pdr = pdr + 1
    
    bc2 = radio.button_field(processing_dialog, 'Baseline correction method:', 0,
                             ('None', None),
			     ('POLY', BC_POLY))
    bc2.frame.grid(row = pdr, column = 2, sticky = 'nw')
    pdr = pdr + 1
    self.baseline_correction2_dialog = bc2
    self.baseline_correction2 = bc2.entry_field.variable

    af2 = radio.button_field(processing_dialog, 'Apodization function:', 1,
                             ('None', None),
			     ('SP', SP),
			     ('EM', EM))
    af2.frame.grid(row = pdr, column = 2, sticky = 'nw')
    pdr = pdr + 1
    self.apodization_function2_dialog = af2
    self.apodization_function2 = af2.entry_field.variable

    zf2 = radio.button_field(processing_dialog, 'Zero fill options:', 1,
			     ('None', None),
                             ('auto', ZF_Auto),
			     ('size (eg. 4096, 8192)', ZF2_Size))
    zf2.frame.grid(row = pdr, column = 2, sticky = 'nw')
    pdr = pdr + 1
    self.zero_fill2_dialog = zf2
    self.zero_fill2 = zf2.entry_field.variable

    ft2 = radio.button_field(processing_dialog, 'Fourier transform options:', 1,
                             ('None', FT_ONLY),
			     ('alt', FT_ALT),
			     ('auto', FT_AUTO),
			     ('inv', FT_INV),
			     ('neg', FT_NEG),
			     ('real', FT_REAL))
    ft2.frame.grid(row = pdr, column = 2, sticky = 'nw')
    pdr = pdr + 1
    self.fourier_transform2_dialog = ft2
    self.fourier_transform2 = ft2.entry_field.variable

    ext2 = radio.button_field(processing_dialog, 'Extract region options:', 0,
			     ('None', None),
                             ('left', EXT_LEFT),
                             ('right', EXT_RIGHT),
                             ('mid', EXT_MID),
                             ('to xn', EXT_XN),
			     ('from x1 to xn', EXT_X1XN))
    ext2.frame.grid(row = pdr, column = 2, sticky = 'nw')
    pdr = pdr + 1
    self.extract_region2_dialog = ext2
    self.extract_region2 = ext2.entry_field.variable
    
    pobr = tkutil.button_row(processing_dialog,
			     ('Test processing parameters', self.test_processing_parameters_cb),
			     ('Run nmrDraw', self.run_nmrdraw_cb),
			     ('Process spectra', self.process_spectra_cb),
			     ('Clear processing output', self.clear_processing_output_cb),
			     ('Reset to defaults', self.reset_processing_dialog_cb),
			     ('Quit', self.close_cb))
    pobr.frame.grid(row = pdr, column = 0, columnspan = 3)

    pbutton.show_widget_cb(processing_dialog, None)
    pbutton.map_widget(processing_dialog)
#
# ----------------------------------------------------------------------------
# END PROCESSING DIALOG
# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# BEGIN SPECTRA HANDLING DIALOG
# ----------------------------------------------------------------------------
#    
    hbutton = tkutil.checkbutton(self.top, 'Show spectra handling dialog', 0)
    hbutton.button.pack(side = 'top', anchor = 'w')

    spectra_handling_dialog = Tkinter.Frame(self.top)
    spectra_handling_dialog.pack(side = 'top', anchor = 'w')

    self.hz_range_widget = [None, None]
    cr = tkutil.entry_row(spectra_handling_dialog, 'Coupling range [Hz]: ',
                          ('min', '10', 3), ('max', '15', 3), ('step', '0.5', 3), ('J0', '', 4))
    (self.hz_range_widget[0],
     self.hz_range_widget[1],
     self.hz_step_widget,
     self.cnst5_widget) = cr.variables
    self.cnst5_entry = cr.entries[3]
    cr.frame.pack(side = 'top', anchor = 'w')

    sigma_dialog = Tkinter.Frame(spectra_handling_dialog)
    sigma_dialog.pack(side = 'top', anchor = 'w')
    
    refocusing_pulse = tkutil.entry_field(sigma_dialog, 'Refocusing pulse: length ', '', 9, 'ms ')
    self.refocusing_pulse_length = refocusing_pulse.variable
    refocusing_pulse.frame.grid(row = 0, column = 0, sticky = 'e')

    rpp = tkutil.file_field(sigma_dialog, 'shape ', 'shapefile', width = 50)
    rpp.frame.grid(row = 0, column = 1, sticky = 'e', columnspan=2)
    self.refocusing_pulse_path = rpp
    
    inversion_pulse = tkutil.entry_field(sigma_dialog, 'Inversion pulse: length ', '', 9, 'ms ')
    self.inversion_pulse_length = inversion_pulse.variable
    inversion_pulse.frame.grid(row = 1, column = 0, sticky = 'e')

    ipp = tkutil.file_field(sigma_dialog, 'shape ', 'shapefile', width = 50)
    ipp.frame.grid(row = 1, column = 1, sticky = 'e', columnspan=2)
    self.inversion_pulse_path = ipp
    
    clz = tkutil.entry_field(sigma_dialog, 'correction in pulse sequence ', '0', 9, '%   ')
    self.correction = clz.variable
    clz.frame.grid(row = 2, column = 0)
 
    sbr = tkutil.button_row(sigma_dialog,
        		     ('Calculate sigmaopt', self.calculate_sigma_cb))
    sbr.frame.grid(row = 2, column = 1, sticky = 'e')
    
    s = tkutil.entry_field(sigma_dialog, 'optimal sigma = ', '', 9, 'ms')
    s.variable.set('11.409')
    self.sigma_widget = s
    self.sigma = s.variable
    s.frame.grid(row = 2, column = 2, sticky = 'w')

    hod = Tkinter.Frame(spectra_handling_dialog)
    hod.pack(side = 'top', anchor = 'w')
    
    w6 = Tkinter.Label(hod, text = 'Spectra handling output:')
    w6.pack(side = 'top', anchor = 'nw')
    
    ho = tkutil.scrolling_text(hod, height = 9, width = 100)
    ho.frame.pack(side = 'top', anchor = 'nw')
    self.handling_output = ho.text
    
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
# BEGIN SPECTRA ASSIGNEMENT DIALOG
# ----------------------------------------------------------------------------
#    
    hbutton = tkutil.checkbutton(self.top, 'Show spectra assign dialog', 0)
    hbutton.button.pack(side = 'top', anchor = 'w')

    spectra_assign_dialog = Tkinter.Frame(self.top)
    spectra_assign_dialog.pack(side = 'top', anchor = 'w')

    spectra_assign_widget = Tkinter.Frame(spectra_assign_dialog)
    spectra_assign_widget.pack(side = 'top', anchor = 'w')

    sbr = radio.button_col(spectra_assign_widget,
			     ('Assign alpha-spectrum + Save', self.assign_alpha_cb),
			     ('Copy alpha assignement', self.copy_alpha_assignement_cb),
			     ('Assign beta-spectrum', self.assign_beta_cb),
			     ('Copy beta assignement', self.copy_beta_assignement_cb),
			     ('Save spectra', self.save_spectra_cb)
			     )
    sbr.frame.pack(side = 'left', anchor ='w')
    
    aod = Tkinter.Frame(spectra_assign_widget)
    aod.pack(side = 'top', anchor = 'w')

    w7 = Tkinter.Label(aod, text = 'Spectra assign output:')
    w7.pack(side = 'top', anchor = 'nw')
    
    ao = tkutil.scrolling_text(aod, height = 9, width = 77)
    ao.frame.pack(side = 'top', anchor = 'nw')
    self.assign_output = ao.text
    
    aobr = tkutil.button_row(spectra_assign_dialog,
			     ('Clear assign output', self.clear_assign_output_cb),
			     ('Quit', self.close_cb))
    aobr.frame.pack()

    hbutton.show_widget_cb(spectra_assign_dialog, None)
    hbutton.map_widget(spectra_assign_dialog)
#
# ----------------------------------------------------------------------------
# END SPECTRA ASSIGNEMENT DIALOG
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
			     ('Evaluate couplings', self.evaluate_couplings_cb),
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
  def save_fid_com_cb(self):
  
    self.save_widget(self.fid_com, 'Save conversion script As')

# ----------------------------------------------------------------------------
#
  def save_ft2_com_cb(self):
  
    self.save_widget(self.ft2_com, 'Save processing script As')

# ----------------------------------------------------------------------------
#
  def save_widget(self, widget, title):
  
    path = tkutil.save_file(self.top, title, 'Any')
    self.write_file(path, 'w', widget.get(1.0, 'end'))

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
  def load_fid_com_cb(self):

    self.load2widget(self.fid_com, 'Load conversion script')

# ----------------------------------------------------------------------------
#
  def load_ft2_com_cb(self):

    self.load2widget(self.ft2_com, 'Load processing script')

# ----------------------------------------------------------------------------
#
  def load2widget(self, widget, title):

    path = tkutil.load_file(self.top, title, 'Any')
    if path:
      script = self.read_file(path, 'r')
      widget.insert('end', script)

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
  def read_parameters(self):

    rv = re.compile("(?P<path>.*/)""(?P<ser>.*$)")
    self.acqus_path = self.get_path(self.a_ser_path.get()) + 'acqus'
    self.acqu2s_path = self.get_path(self.a_ser_path.get()) + 'acqu2s'
   
    if self.acqus_path:
      self.acqus = self.find_parameters(self.acqus_path, 'DECIM', 'TD', 'SFO1', 'SW', 'O1', 'AQ_mod')
      self.acqus['CNST5'] = self.find_cnst5(self.acqus_path)
    if self.acqu2s_path:
      self.acqu2s = self.find_parameters(self.acqu2s_path, 'TD', 'FnMODE', 'SFO1', 'SW', 'O1')

    if self.acqus and self.acqu2s:
      script = self.create_conversion_script()
      self.fid_com.insert('end', script)

# ----------------------------------------------------------------------------
#
  def find_parameters(self, path, *patterns):
    
    parameters={}
    
    if path:
      file = self.read_file(path, 'r')
      for pattern in patterns:
        search_result = re.compile("(?<=\$" + pattern + "= )\d+(.\d+)?").search(file)
        if search_result:
          parameters[pattern] = search_result.group(0)

      if int(float(parameters['SFO1'])) == 600 or int(float(parameters['SFO1'])) == 500:
        parameters['LAB'] = '1H'
      elif int(float(parameters['SFO1'])) == 150 or int(float(parameters['SFO1'])) == 125:
        parameters['LAB'] = '13C'
      elif int(float(parameters['SFO1'])) == 60 or int(float(parameters['SFO1'])) == 50:
        parameters['LAB'] = '15N'
    
    return parameters
    
# ----------------------------------------------------------------------------
#
  def find_cnst5(self, path):

    if path:
      file = self.read_file(path, 'r')

    search_result = re.compile("(?<=\$CNST= \(0....\))(?P<CNST14>(.)?\n\d+(\.\d+)? \d+(\.\d+)? \d+(\.\d+)? \d+(\.\d+)? \d+(\.\d+)? )(?P<CNST5>\d+(\.\d+)?)(?P<CNST6> .*)").search(file)
    if search_result:
      cnst5 = search_result.group('CNST5')
      self.cnst5_entry.entry.delete('0', 'end')
      self.cnst5_entry.entry.insert('end', '%4.1f' % float(cnst5))
      
    return cnst5

# ----------------------------------------------------------------------------
#
  def create_conversion_script(self):
    
#    script = '#!/bin/csh\n'
    script = '#!/bin/bash\n'
    script = script + 'bruk2pipe -in ser -bad 0.0 -swap -DMX'
    script = script +  ' -decim ' + self.acqus['DECIM'] + ' -dspfvs 12   '
    script = script + '\\\n'
    
    xn = xt = float(self.acqus['TD']) / 2  # begin bruker feature
    while (xn%32) != 0:
      xn = xn + 1
    xn = xn * 2                       # end bruker feature
    script = script + string.ljust(' -xN', 16) + string.ljust(`int(xn)`, 15)
    script = script + string.ljust('-yN', 15) + string.ljust(self.acqu2s['TD'], 15)
    script = script + '\\\n'
    
    yt=float(self.acqu2s['TD']) / 2
    script = script + string.ljust(' -xT', 16) + string.ljust(`int(xt)`, 15)
    script = script + string.ljust('-yT', 15) + string.ljust(`int(yt)`, 15)
    script = script + '\\\n'
    
    script = script + string.ljust(' -xMODE', 16)
    if self.acqus['AQ_mod'] == '3':
      script = script + string.ljust('DQD', 15)
    script = script + string.ljust('-yMODE', 15)
    if self.acqu2s.has_key('FnMODE'):
      if self.acqu2s['FnMODE'] == '5':
        script = script + string.ljust('States-TPPI', 15)
      elif self.acqu2s['FnMODE'] == '6':
        script = script + string.ljust('Echo-Antiecho', 15)
    # defaults FnMODE to States-TPPI
    else:
      script = script + string.ljust('States-TPPI', 15)
    script = script + '\\\n'

    xsw = float(self.acqus['SW']) * float(self.acqus['SFO1'])
    ysw = float(self.acqu2s['SW']) * float(self.acqu2s['SFO1'])
    script = script + string.ljust(' -xSW', 16) + string.ljust("%8.3f" % xsw, 15)
    script = script + string.ljust('-ySW', 15) + string.ljust("%8.3f" % ysw, 15)
    script = script + '\\\n'
    
    script = script + string.ljust(' -xOBS', 16) + string.ljust("%7.3f" % float(self.acqus['SFO1']), 15)
    script = script + string.ljust('-yOBS', 15) + string.ljust("%7.3f" % float(self.acqu2s['SFO1']), 15)
    script = script + '\\\n'
    
    xcar = float(self.acqus['O1']) / float(self.acqus['SFO1']) + self.reference(self.acqus)
    ycar = float(self.acqu2s['O1']) / float(self.acqu2s['SFO1']) + self.reference(self.acqu2s)
    script = script + string.ljust(' -xCAR', 16) + string.ljust("%1.3f" % xcar, 15)
    script = script + string.ljust('-yCAR', 15) + string.ljust("%7.3f" % ycar, 15)
    script = script + '\\\n'
    
    script = script + string.ljust(' -xLAB', 16) + string.ljust(self.acqus['LAB'], 15)
    script = script + string.ljust('-yLAB', 15) + string.ljust(self.acqu2s['LAB'], 15)
    script = script + '\\\n'
    
    script = script + string.ljust(' -ndim', 16) + string.ljust('2', 15)
    script = script + string.ljust('-aq2D', 15) + string.ljust('States', 15)
    script = script + '\\\n'
    
    script = script + ' -out test.fid -verb -ov \n'

    return script

# ----------------------------------------------------------------------------
#
  def reference(self, parameters):

   nucleus = parameters['LAB']
   if nucleus == '1H':
     result = 0.0
   elif nucleus == '13C':
     result = 2.7
   elif nucleus == '15N':
     result = -0.61
   else:
     result = 0.0

   return result
   
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
  def execute_script(self, path, name, script, command='./'):

    os.chdir(path)
    self.write_file(name, 'w', script)
    os.chmod(name, 448)
    
    r, w, e = popen2.popen3('bash')
#    r, w, e = popen2.popen3('csh')
    
#    w.write('source /home/nmr/software/nmrpipe/com/nmrInit.linux.com\n')
    w.write('. /packages/run/modules-2.0/init/bash\n')
    w.write('module add nmrpipe\n')
    w.write('cd ' + path + '\n')
    w.write(command + name + '\n')
    w.write('exit\n')
    
    w.close()
    
    stdout = r.read()
    stderr = e.read()
    
    r.close()
    e.close()
    
    return stdout, stderr
    
# ----------------------------------------------------------------------------
#
  def execute_command(self, command, path='', arguments=''):

    r, w, e = popen2.popen3('bash')
#    r, w, e = popen2.popen3('csh')
    
    if path:
      w.write('cd ' + path + '\n')
    w.write(command + ' ' + arguments + '\n')
    w.write('exit\n')
    
    w.close()
    
    stdout = r.read()
    stderr = e.read()
    
    r.close()
    e.close()
    
    return stdout, stderr
    
# ----------------------------------------------------------------------------
#
  def clear_fid_com_cb(self):
    
    self.fid_com.delete(1.0, 'end')

# ----------------------------------------------------------------------------
#
  def clear_conversion_output_cb(self):
    
    self.conversion_output.delete(1.0, 'end')

# ----------------------------------------------------------------------------
#
  def test_processing_parameters_cb(self):

    if self.a_ser_path.get():
      if os.access(self.get_path(self.a_ser_path.get()) + 'test.fid', os.R_OK) == True:
        self.test_processing_parameters()

# ----------------------------------------------------------------------------
#
  def test_processing_parameters(self):
    
    output = self.execute_script(self.get_path(self.a_ser_path.get()), 'ft2.com', 
                                   self.create_processing_script())

    self.processing_output.insert('end', output[0] + output[1])

# ----------------------------------------------------------------------------
#
  def run_nmrdraw_cb(self):
    
    self.run_nmrdraw()
      
# ----------------------------------------------------------------------------
#
  def run_nmrdraw(self):
    
#    r, w, e = popen2.popen3('csh')
    r, w, e = popen2.popen3('bash')
#    w.write('source /home/nmr/software/nmrpipe/com/nmrInit.linux.com\n')
    w.write('. /packages/run/modules-2.0/init/bash\n')
    w.write('module add nmrpipe\n')
    w.write('ulimit -n 1000\n')
    if self.a_ser_path.get():
      w.write('cd ' + self.get_path(self.a_ser_path.get()) + '\n')
    w.write('nmrDraw\n')
    w.write('exit\n')

    w.close()
    r.close()
    e.close()

# ----------------------------------------------------------------------------
#
  def process_spectra_cb(self):

    if self.a_ser_path.get():
      if self.b_ser_path.get():
        if self.a_ser_path.get() != self.b_ser_path.get():
	  if os.access(self.get_path(self.a_ser_path.get()) + 'test.fid', os.R_OK) == True:
	    if os.access(self.get_path(self.b_ser_path.get()) + 'test.fid', os.R_OK) == True:
	      self.process_spectra()
	    else:
              self.processing_output.insert('end', 'Beta test.fid not found\n')
	  else:
              self.processing_output.insert('end', 'Alpha test.fid not found\n')
        else:
          self.processing_output.insert('end', 'WARNING !!! You have specified the same path and filename for the "Alpha ser-file" and the "Beta ser-file"\n')
      else:
        self.processing_output.insert('end', 'Please specify the "Beta ser-file" path\n')
    else:
      self.processing_output.insert('end', 'Please specify the "Alpha ser-file" path\n')

# ----------------------------------------------------------------------------
#
  def process_spectra(self):

    self.process_spectrum(self.processing_output, self.get_path(self.a_ser_path.get()), 0.0, 'Processing of the alpha fid with 0 degree zero-order phase correction in indirect domain')
    self.process_spectrum(self.processing_output, self.get_path(self.a_ser_path.get()), 90.0, 'Processing of the alpha fid with 90 degree zero-order phase correction in indirect domain')
    self.process_spectrum(self.processing_output, self.get_path(self.b_ser_path.get()), 0.0, 'Processing of the beta fid with 0 degree zero-order phase correction in indirect domain')
    self.process_spectrum(self.processing_output, self.get_path(self.b_ser_path.get()), 90.0, 'Processing of the beta fid with 90 degree zero-order phase correction in indirect domain')
    

# ----------------------------------------------------------------------------
#
  def process_spectrum(self, output_dialog, path, ps2p0, text = ''):

    if text:
      output_dialog.insert('end', text + ' ... ')
    output = self.execute_script(path,
      '%1.0f' % ps2p0 + '.com', 
      self.create_processing_script(ps2p0 = ps2p0, output = '%2.0f' % ps2p0 + '.ft2'))
    if output[1]:
      output_dialog.insert('end', 'ERROR:\n' + output[0] + output[1])
    else:
      output_dialog.insert('end', 'OK\n')
      
# ----------------------------------------------------------------------------
#
  def create_processing_script(self, ps2p0 = 0.0, ps2p1 = 0.0, output = 'test.ft2'):

#    script = '#!/bin/csh\n'
    script = '#!/bin/bash\n'
    script = script + 'nmrPipe   -in test.fid \\\n'
    if self.solvent_filter.get():
      script = script + ' | nmrPipe ' + self.solvent_filter.get() + ' \\\n'
    if self.extract_region0.get():
      script = script + ' | nmrPipe ' + self.extract_region0.get() + ' -sw \\\n'
    if self.apodization_function1.get():
      script = script + ' | nmrPipe ' + self.apodization_function1.get() + ' \\\n'
    else:
      script = script + ' | nmrPipe -fn SP -off 0.5 -end 0.98 -pow 2 -c 0.5 \\\n'
    if self.zero_fill1.get():
      script = script + ' | nmrPipe ' + self.zero_fill1.get() + ' \\\n'
    else:
      script = script + ' | nmrPipe -fn ZF -auto \\\n'
    if self.fourier_transform1.get():
      script = script + ' | nmrPipe ' + self.fourier_transform1.get() + ' \\\n'
    else:
      script = script + ' | nmrPipe -fn FT \\\n'
    if self.phase1_dialog.p0:
      script = script + ' | nmrPipe -fn PS -p0 ' + self.phase1_dialog.p0[0].get()
    else:
      script = script + ' | nmrPipe -fn PS -p0 0.0'
    if self.phase1_dialog.p1[0].get():
      script = script + ' -p1 ' + self.phase1_dialog.p1[0].get() + ' -di \\\n'
    else:
      script = script + ' -p1 0.0 -di \\\n'
    script = script + ' | nmrPipe -fn TP \\\n'
    if self.apodization_function2.get():
      script = script + ' | nmrPipe ' + self.apodization_function2.get() + ' \\\n'
    else:
      script = script + ' | nmrPipe -fn SP -off 0.5 -end 0.98 -pow 2 -c 0.5 \\\n'
    if self.zero_fill2.get():
      script = script + ' | nmrPipe ' + self.zero_fill2.get() + ' \\\n'
    else:
      script = script + ' | nmrPipe -fn ZF -auto \\\n'
    if self.fourier_transform2.get():
      script = script + ' | nmrPipe ' + self.fourier_transform2.get() + ' \\\n'
    else:
      script = script + ' | nmrPipe -fn FT -alt \\\n'
    if self.phase1_dialog.p0[1].get():
      script = script + ' | nmrPipe -fn PS -p0 ' + `ps2p0 + float(self.phase1_dialog.p0[1].get())`
    else:
      script = script + ' | nmrPipe -fn PS -p0 ' + `ps2p0`
    if self.phase1_dialog.p1[1].get():
      script = script + ' -p1 ' + `ps2p1 + float(self.phase1_dialog.p1[1].get())` + ' -di \\\n'
    else:
      script = script + ' -p1 ' + `ps2p1` + ' -di \\\n'
    script = script + ' | nmrPipe -fn TP \\\n'
    if self.baseline_correction1.get():
      script = script + ' | nmrPipe ' + self.baseline_correction1.get() + ' \\\n'
    if self.baseline_correction2.get():
      script = script + ' | nmrPipe -fn TP \\\n'
      script = script + ' | nmrPipe ' + self.baseline_correction2.get() + ' \\\n'
      script = script + ' | nmrPipe -fn TP \\\n'
    if self.extract_region1.get():
      script = script + ' | nmrPipe ' + self.extract_region1.get() + ' -sw \\\n'
    if self.extract_region2.get():
      script = script + ' | nmrPipe -fn TP \\\n'
      script = script + ' | nmrPipe ' + self.extract_region2.get() + ' -sw \\\n'
      script = script + ' | nmrPipe -fn TP \\\n'
    script = script + ' | nmrPipe -out ' + output + ' -ov \n'
    
    return script

# ----------------------------------------------------------------------------
#
  def reset_processing_dialog_cb(self):

   self.solvent_filter_dialog.reset_cb()

   self.phase1_dialog.reset_cb()
   self.extract_region0_dialog.reset_cb()
   
   self.baseline_correction1_dialog.reset_cb()
   self.apodization_function1_dialog.reset_cb()
   self.zero_fill1_dialog.reset_cb()
   self.fourier_transform1_dialog.reset_cb()
   self.extract_region1_dialog.reset_cb()
   
   self.baseline_correction2_dialog.reset_cb()
   self.apodization_function2_dialog.reset_cb()
   self.zero_fill2_dialog.reset_cb()
   self.fourier_transform2_dialog.reset_cb()
   self.extract_region2_dialog.reset_cb()

# ----------------------------------------------------------------------------
#
  def clear_processing_output_cb(self):
    
    self.processing_output.delete(1.0, 'end')

# ----------------------------------------------------------------------------
#
  def update_correction_method(self):
    
    pass
    
# ----------------------------------------------------------------------------
#
  def update_peak_fitting_method(self):
    
    pass
    
# ----------------------------------------------------------------------------
#
  def calculate_sigma_cb(self):
    
    if self.refocusing_pulse_length.get() and self.inversion_pulse_length.get():
      if not self.correction.get():
        self.correction.entry.delete('0', 'end')
        self.correction.entry.insert('end', '%4.1f' % float(0))
      if not self.cnst5_widget.get():
        if self.a_ser_path.get():
          self.read_parameters()
        else:
          self.cnst5_entry.entry.delete('0', 'end')
          self.cnst5_entry.entry.insert('end', '%4.1f' % float(0))
      self.calculate_sigma()

# ----------------------------------------------------------------------------
#
  def calculate_sigma(self):
    
    arguments = ' -r ' + self.refocusing_pulse_length.get()
    arguments = arguments + ' -i ' + self.inversion_pulse_length.get()
    if self.refocusing_pulse_path.get() :
      arguments = arguments + ' -R ' + self.refocusing_pulse_path.get()
    else :  
      self.handling_output.insert( 'end', 'WARNING !!! No refocusing pulse shape given. Assuming square shape.\n')
    if self.inversion_pulse_path.get() :
      arguments = arguments + ' -I ' + self.inversion_pulse_path.get()
    else :  
      self.handling_output.insert( 'end', 'WARNING !!! No inversion pulse shape given. Assuming square shape.\n')
    arguments = arguments + ' -J ' + self.cnst5_widget.get()
    stdout, stderr = self.execute_command('sigma', arguments=arguments)
    if stdout[:4] == "nsss" :
      self.handling_output.insert( 'end', stdout )
    if stderr :
      self.handling_output.insert( 'end', stderr )
    else :
      self.handling_output.insert( 'end', 'Calculated efficiency of J-coupling evolution during the pulses is ' + string.strip(stdout) + '%\n')
      sigma = 1.0 / (8.0 * float(self.cnst5_widget.get()) / 1000.0) + ( float( stdout ) - float( self.correction.get() ) ) / 100.0 * max(float(self.refocusing_pulse_length.get()), float(self.inversion_pulse_length.get()))  / 2.0
      self.sigma_widget.entry.delete('0', 'end')
      self.sigma_widget.entry.insert('end', '%6.3f' % sigma)

# ----------------------------------------------------------------------------
#
  def calculate_sigma_RaF_cb(self):

    if self.correction_RaF.get() and self.p14.get():
      if hasattr(self, 'acqus') == False:
       if self.a_ser_path.get():
          self.read_parameters()
          self.calculate_sigma_RaF()
      else:
        self.calculate_sigma_RaF()

# ----------------------------------------------------------------------------
#
  def calculate_sigma_RaF(self):
    
    self.sigma_RaF_widget.entry.delete('0', 'end')
    sigma = 1.0 / (8.0 * float(self.acqus['CNST5']) / 1000.0) - float(self.correction_RaF.get()) * float(self.p14.get()) + 0.5
    self.sigma_RaF_widget.entry.insert('end', '%6.3f' % sigma)

# ----------------------------------------------------------------------------
#
  def handle_spectra_cb(self):

    if self.a_ser_path.get():
      if self.b_ser_path.get():
        if self.a_ser_path.get() != self.b_ser_path.get():
	  if os.access(self.get_path(self.a_ser_path.get()) + '0.ft2', os.R_OK) == True:
	    if os.access(self.get_path(self.a_ser_path.get()) + '90.ft2', os.R_OK) == True:
	      if os.access(self.get_path(self.b_ser_path.get()) + '0.ft2', os.R_OK) == True:
	        if os.access(self.get_path(self.b_ser_path.get()) + '90.ft2', os.R_OK) == True:
	          if self.sigma.get() or self.sigma_RaF.get():
	            self.handle_spectra()
	          else:
                    self.handling_output.insert('end', 'Please enter the length of the "sigma" in [ms] or or enter the correction and pulse length and press <Calculate sigma> button\n')
	        else:
                  self.handling_output.insert('end', 'Beta spectrum with 90 degree phase correction not found\n')
              else:
                self.handling_output.insert('end', 'Beta spectrum with 0 degree phase correction not found\n')
	    else:
              self.handling_output.insert('end', 'Alpha spectrum with 90 degree phase correction not found\n')
          else:
            self.handling_output.insert('end', 'Alpha spectrum with 0 degree phase correction not found\n')
        else:
          self.handling_output.insert('end', 'WARNING !!! You have specified the same path and filename for the "Alpha ser-file" and the "Beta ser-file"\n')
      else:
        self.handling_output.insert('end', 'Please specify the "Beta ser-file" path\n')
    else:
      self.handling_output.insert('end', 'Please specify the "Alpha ser-file" path\n')

# ----------------------------------------------------------------------------
#
  def handle_spectra(self):
    
    J = float(self.hz_range_widget[0].get())
    

    self.filenames = [[],[]]

    self.combine_spectra(self.handling_output,
             self.get_path(self.a_ser_path.get()) + '90.ft2',
	     self.get_path(self.b_ser_path.get()) + '90.ft2',
	     self.get_path(self.a_ser_path.get()) + 'alpha.ft2')
    self.combine_spectra(self.handling_output,
             self.get_path(self.a_ser_path.get()) + '0.ft2',
	     self.get_path(self.b_ser_path.get()) + '0.ft2',
	     self.get_path(self.a_ser_path.get()) + 'beta.ft2',
	     Action = 'sub')

    while J <= float(self.hz_range_widget[1].get()):
      
      c = tan(0.25 * pi * (8.0 * J * float(self.sigma.get()) / 1000.0 - 1.0))
      
      self.combine_spectra(self.handling_output,
             self.get_path(self.a_ser_path.get()) + 'alpha.ft2',
             self.get_path(self.a_ser_path.get()) + 'beta.ft2',
	     self.get_path(self.a_ser_path.get()) + 'alpha' + string.zfill('%3.1f' % J, 4) + '_' + string.zfill('%5.3f' % c, 4) + '.ft2',
	     c2 = c,
	     trailer = ' for coupling ' + string.zfill('%3.1f' % J, 4) + ' Hz')

      self.filenames[0] = self.filenames[0] + [self.get_path(self.a_ser_path.get()) + 'alpha' + string.zfill('%3.1f' % J, 4) + '_' + string.zfill('%5.3f' % c, 4)]
     
      self.combine_spectra(self.handling_output,
             self.get_path(self.a_ser_path.get()) + 'beta.ft2',
             self.get_path(self.a_ser_path.get()) + 'alpha.ft2',
	     self.get_path(self.a_ser_path.get()) + 'beta' + string.zfill('%3.1f' % J, 4) + '_' + string.zfill('%5.3f' % c, 4) + '.ft2',
	     Action = 'add',
	     c2 = c,
	     trailer = ' for coupling ' + string.zfill('%3.1f' % J, 4) + ' Hz')

      self.filenames[1] = self.filenames[1] + [self.get_path(self.a_ser_path.get()) + 'beta' + string.zfill('%3.1f' % J, 4) + '_' + string.zfill('%5.3f' % c, 4)]

      J = J + float(self.hz_step_widget.get())

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
    w.write('. /packages/run/modules-2.0/init/bash\n')
    w.write('module add nmrpipe\n')
    w.write('cd ' + self.get_path(inName1) + '\n')
    w.write('addNMR -in1 ' + inName1 + ' -in2 ' + inName2 + ' -out ' + outName + ' -' + Action + ' -c1 ' + `c1` + ' -c2 ' + `c2` + '\n')
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
    
    w.write('pipe2ucsf ' + pipe_file + ' ' + ucsf_file + '\n')
    w.write('exit\n')
    
    w.close()
    
    stdout = r.read()
    stderr = e.read()
    
    r.close()
    e.close()
    
    return stdout, stderr
  

# ----------------------------------------------------------------------------
#
  def clear_handling_output_cb(self):
    
    self.handling_output.delete(1.0, 'end')

# ----------------------------------------------------------------------------
#
  def set_contour_level_cb(self):

    if self.a_ser_path.get():
      if self.filenames[0]:
        if os.access(self.filenames[0][0] + '.ucsf', os.R_OK) == True:
	  self.set_contour_level(self.filenames[0][0] + '.ucsf')
        else:
          self.assign_output.insert('end', 'Alpha spectrum save not found\n')
      else:
        self.assign_output.insert('end', 'Please combine the spectra first before making saves\n')
    else:
      self.assign_output.insert('end', 'Please specify the "Alpha ser-file" path\n')

# ----------------------------------------------------------------------------
#
  def set_contour_level(self, spectrum_name):

    self.assign_output.insert('end', 'Set contour level using `ct` and using `fa` save the spectrum as ' + self.filenames[0][0] + '.save\n')
    if os.access(self.filenames[0][0] + '.save', os.R_OK) == True:
      self.session.open_spectrum(self.filenames[0][0] + '.save')
    else:
      self.session.open_spectrum(spectrum_name)

# ----------------------------------------------------------------------------
#
  def make_saves_cb(self):

    if self.a_ser_path.get():
      if self.filenames[0]:
        if os.access(self.filenames[0][0] + '.save', os.R_OK) == True:
	  self.make_saves()
        else:
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
  def assign_alpha_cb(self):

    if self.a_ser_path.get():
      if self.filenames[0]:
        if os.access(self.filenames[0][0] + '.ucsf', os.R_OK) == True:
	  self.assign_alpha()
        else:
          self.assign_output.insert('end', 'Alpha spectrum save not found\n')
      else:
        self.assign_output.insert('end', 'Please combine the spectra first before assignement\n')
    else:
      self.assign_output.insert('end', 'Please specify the "Alpha ser-file" path\n')

# ----------------------------------------------------------------------------
#
  def assign_alpha(self):

    self.assign_output.insert('end', 'Assign spectrum and using `fa` save the spectrum as ' + self.filenames[0][0] + '.save\n')
    if os.access(self.filenames[0][0] + '.save', os.R_OK) == True:
      self.session.open_spectrum(self.filenames[0][0] + '.save')
    else:
      self.session.open_spectrum(self.filenames[0][0] + '.ucsf')

# ----------------------------------------------------------------------------
#
  def copy_alpha_assignement_cb(self):

    if self.a_ser_path.get():
      if self.filenames[0]:
        if os.access(self.filenames[0][0] + '.save', os.R_OK) == True:
	  save = self.read_file(self.filenames[0][0] + '.save', 'r')
 	  self.copy_alpha_assignement()
        else:
          self.assign_output.insert('end', 'Alpha spectrum save not found\n')
      else:
        self.assign_output.insert('end', 'Please combine the spectra first before making saves\n')
    else:
      self.assign_output.insert('end', 'Please specify the "Alpha ser-file" path\n')

# ----------------------------------------------------------------------------
#
  def copy_alpha_assignement(self):

    save = self.read_file(self.filenames[0][0] + '.save', 'r')

    ornament = re.compile("(?<=<ornament>\n)(.*\n)*(?=<end ornament>)").search(save).group(0)
    template_save = string.replace(save, ornament, '')
    
    subspectrum = self.filenames[0]
    for filename in subspectrum[1:]:
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

    for id in range(1, len(self.filenames[0])):
      self.session.open_spectrum(self.filenames[0][id] + '.save')
      for peak in self.project.spectrum_list()[id - 1].peak_list():
	new_spectrum = self.session.project.spectrum_list()[id]
        new_spectrum.place_peak(peak.position)
        self.assign_peak(new_spectrum.peak_list()[len(new_spectrum.peak_list()) - 1], peak.assignment)

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

    save = self.read_file(self.filenames[1][0] + '.save', 'r')

    ornament = re.compile("(?<=<ornament>\n)(.*\n)*(?=<end ornament>)").search(save).group(0)
    template_save = string.replace(save, ornament, '')
    
    subspectrum = self.filenames[1]
    for filename in subspectrum[1:]:
      save = string.replace(template_save,
                       self.get_filename(self.filenames[1][0]),
      	         self.get_filename(filename))
      old_pathname = re.compile("(?<=pathname ).*(?=\n)").search(save).group(0)
      save = string.replace(save, old_pathname, filename + '.ucsf')
      save = string.replace(save, 'integrate.methods 1 0 1', 'integrate.methods 1 0 1')
      save = string.replace(save, 'integrate.adjust_linewidths 1', 'integrate.adjust_linewidths 0')
      save = string.replace(save, 'integrate.fit_baseline 0', 'integrate.fit_baseline 0')
      save = string.replace(save, 'integrate.motion_range 0.040 0.010', 'integrate.motion_range 0.40 0.10')
      self.write_file(filename + '.save', 'w', save)

    for id in range(1, len(self.filenames[1])):
      self.session.open_spectrum(self.filenames[1][id] + '.save')
      for peak in self.project.spectrum_list()[id + len(self.filenames[1]) - 1].peak_list():
	new_spectrum = self.project.spectrum_list()[id + len(self.filenames[1])]
        new_spectrum.place_peak(peak.position)
        self.assign_peak(new_spectrum.peak_list()[len(new_spectrum.peak_list()) - 1], peak.assignment)

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
    
    for spectrum_no in range(len(self.filenames[0])):
      for subspectrum_no in range(len(self.filenames)):
	template_save = self.read_file(self.filenames[subspectrum_no][spectrum_no] + '.save', 'r')
        positive_treshold = re.compile("(?<=contour.pos\ )(?P<contourlevel>\d+)\ +(?P<treshold>\d+(\.\d+e(\+|\-)\d+)?)(.*)\n*").search(template_save).group('treshold')
        negative_treshold = re.compile("(?<=contour.neg\ )(?P<contourlevel>\d+)\ +(?P<treshold>-\d+(\.\d+e(\+|\-)\d+)?)(.*)\n*").search(template_save).group('treshold')
	spectrum = self.project.spectrum_list()[spectrum_no + len(self.filenames[0]) * subspectrum_no]
        for peak in spectrum.peak_list():
	  peak_id = spectrum.peak_list().index(peak)
          treshold = peak.data_height * (float(self.fit_peak_height.get()) / 100.0)
          save = string.replace(template_save, positive_treshold, `treshold`, 1)
          save = string.replace(template_save, negative_treshold, `treshold`, 1)
          self.write_file(self.get_path(self.a_ser_path.get()) + peak.spectrum.name + '_' + peak.assignment + '.save', 'w', save)
	  self.session.open_spectrum(self.get_path(self.a_ser_path.get()) + peak.spectrum.name + '_' + peak.assignment + '.save')
          views = self.session.project.view_list()
	  last_view = views[len(views) - 1]
	  fitted_peak = last_view.spectrum.peak_list()[peak_id]
	  fitted_peak.fit(last_view)
	  rv = re.compile("(?P<subspectrum>\D+)(?P<hz>\d+\.\d+)_(?P<ratio>.*$)").search(peak.spectrum.name)
	  peak_info = self.get_peak_assignement(peak.assignment), rv.group('subspectrum'), rv.group('hz'),
          for dimension in range(len(fitted_peak.position)):
	    position = fitted_peak.position[dimension] * fitted_peak.spectrum.hz_per_ppm[dimension]
	    peak_info = peak_info + ('%9.3f' % position,)
          residues[peak_id][spectrum_no].append(peak_info)
          if view_buff: view_buff.destroy()
          view_buff = last_view
    if view_buff: view_buff.destroy()
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
    
    for spectrum_no in range(len(self.filenames[0])):
      for subspectrum_no in range(len(self.filenames)):
	template_save = self.read_file(self.filenames[subspectrum_no][spectrum_no] + '.save', 'r')
        positive_treshold = re.compile("(?<=contour.pos\ )(?P<contourlevel>\d+)\ +(?P<treshold>\d+(\.\d+e(\+|\-)\d+)?)(.*)\n*").search(template_save).group('treshold')
        negative_treshold = re.compile("(?<=contour.neg\ )(?P<contourlevel>\d+)\ +(?P<treshold>-\d+(\.\d+e(\+|\-)\d+)?)(.*)\n*").search(template_save).group('treshold')
	spectrum = self.project.spectrum_list()[spectrum_no + len(self.filenames[0]) * subspectrum_no]
        for peak in spectrum.peak_list():
	  peak_id = spectrum.peak_list().index(peak)
          treshold = peak.data_height * (float(self.fit_peak_height.get()) / 100.0)
          save = string.replace(template_save, positive_treshold, `treshold`, 1)
          save = string.replace(template_save, negative_treshold, `treshold`, 1)
          self.write_file(self.get_path(self.a_ser_path.get()) + peak.spectrum.name + '_' + peak.assignment + '.save', 'w', save)
	  self.session.open_spectrum(self.get_path(self.a_ser_path.get()) + peak.spectrum.name + '_' + peak.assignment + '.save')
          views = self.session.project.view_list()
	  last_view = views[len(views) - 1]
	  fitted_peak = last_view.spectrum.peak_list()[peak_id]
	  fitted_peak.center()
	  rv = re.compile("(?P<subspectrum>\D+)(?P<hz>\d+\.\d+)_(?P<ratio>.*$)").search(peak.spectrum.name)
	  peak_info = self.get_peak_assignement(peak.assignment), rv.group('subspectrum'), rv.group('hz'),
          for dimension in range(len(fitted_peak.position)):
	    position = fitted_peak.position[dimension] * fitted_peak.spectrum.hz_per_ppm[dimension]
	    peak_info = peak_info + ('%9.3f' % position,)
          residues[peak_id][spectrum_no].append(peak_info)
          if view_buff: view_buff.destroy()
          view_buff = last_view
    if view_buff: view_buff.destroy()
    self.residues = residues
 
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

    self.couplings = ('#' + self.residues[0][0][0][0][1][0] + '-'
      + self.residues[0][0][0][0][1][1] + '\n')
    for residue in self.residues:
      self.couplings = self.couplings + ('# ' + residue[0][0][0][0] + ' ' 
        + residue[0][0][0][1][0] + ' ' + residue[0][0][0][1][1] + '\n')
      for hz in residue:
	self.couplings = self.couplings + (hz[0][2] + ' '
	  + `float(hz[0][3])- float(hz[1][3])` + ' '
	  + `float(hz[0][4]) - float(hz[1][4])` + '\n')
      self.couplings = self.couplings + '\n\n'
      
    self.write_file(self.s3e_root + '/' + self.residues[0][0][0][0][1][0] +
      self.residues[0][0][0][0][1][1], 'w', self.couplings)
    print (self.s3e_root + '/' + self.residues[0][0][0][0][1][0] +
      self.residues[0][0][0][0][1][1])

# ----------------------------------------------------------------------------
#
  def plot_couplings_cb(self):

    plot_size = self.get_plot_size()
    script = 'set term postscript landscape enhanced color\n'
    script = script + 'set out \"' + self.residues[0][0][0][0][1][0]
    script = script + self.residues[0][0][0][0][1][1] + '.ps\"\n'
    script = script + 'set key out\n'
    script = script + 'set size square\n'
    script = script + 'set style line 1 lt 1 lw 1 pt 7 ps 1\n\n\n'
    
    for n in range(len(self.residues)):
      script = script + ('f(x)=a' + self.residues[n][0][0][0][0] + self.residues[n][0][0][0][1][0] + self.residues[n][0][0][0][1][1] + ' + b' +
        self.residues[n][0][0][0][0] + self.residues[n][0][0][0][1][0] + self.residues[n][0][0][0][1][1] + '*x + c' + self.residues[n][0][0][0][0] + self.residues[n][0][0][0][1][0] + self.residues[n][0][0][0][1][1]
	+ '*x**2\n')
      script = script + 'a' + self.residues[n][0][0][0][0] + self.residues[n][0][0][0][1][0] + self.residues[n][0][0][0][1][1] + '=1.0\n'
      script = script + 'b' + self.residues[n][0][0][0][0] + self.residues[n][0][0][0][1][0] + self.residues[n][0][0][0][1][1] + '=1.0\n'
      script = script + 'c' + self.residues[n][0][0][0][0] + self.residues[n][0][0][0][1][0] + self.residues[n][0][0][0][1][1] + '=1.0\n'
      script = script + 'fit f(x) \"' + self.residues[0][0][0][0][1][0]
      script = script + self.residues[0][0][0][0][1][1]
      script = script + '\" index ' + `n` + ' using 1:2:(0.1*$2) via a'
      script = script + self.residues[n][0][0][0][0] + self.residues[n][0][0][0][1][0] + self.residues[n][0][0][0][1][1] + ', b'
      script = script + self.residues[n][0][0][0][0] + self.residues[n][0][0][0][1][0] + self.residues[n][0][0][0][1][1] + ', c'
      script = script + self.residues[n][0][0][0][0] + self.residues[n][0][0][0][1][0] + self.residues[n][0][0][0][1][1] + '\n\n'
      script = script + 'plot [' + plot_size[0] + ':' + plot_size[1] + ']['
      script = script + plot_size[0] + ':' + plot_size[1] + '] x notitle,\\\n'
      script = script + 'f(x) notitle,\\\n'
      script = script + '\"' + self.residues[0][0][0][0][1][0]
      script = script + self.residues[0][0][0][0][1][1] + '\" index '
      script = script + `n` + ' using 1:2 title "'
      script = script + self.residues[n][0][0][0][0] + self.residues[n][0][0][0][1][0] + self.residues[n][0][0][0][1][1] + '" ls 1\n'
      script = script + '\n'
      script = script + ('f(x)=d' + self.residues[n][0][0][0][0] + self.residues[n][0][0][0][1][0] + self.residues[n][0][0][0][1][1] + ' + e' +
        self.residues[n][0][0][0][0] + self.residues[n][0][0][0][1][0] + self.residues[n][0][0][0][1][1] + '*x + f' + self.residues[n][0][0][0][0] + self.residues[n][0][0][0][1][0] + self.residues[n][0][0][0][1][1]
	+ '*x**2\n')
      script = script + 'd' + self.residues[n][0][0][0][0] + self.residues[n][0][0][0][1][0] + self.residues[n][0][0][0][1][1] + '=1.0\n'
      script = script + 'e' + self.residues[n][0][0][0][0] + self.residues[n][0][0][0][1][0] + self.residues[n][0][0][0][1][1] + '=1.0\n'
      script = script + 'f' + self.residues[n][0][0][0][0] + self.residues[n][0][0][0][1][0] + self.residues[n][0][0][0][1][1] + '=1.0\n'
      script = script + 'fit f(x) \"' + self.residues[0][0][0][0][1][0]
      script = script + self.residues[0][0][0][0][1][1]
      script = script + '\" index ' + `n` + ' using 1:3:(0.1*$3) via d'
      script = script + self.residues[n][0][0][0][0] + self.residues[n][0][0][0][1][0] + self.residues[n][0][0][0][1][1] + ', e'
      script = script + self.residues[n][0][0][0][0] + self.residues[n][0][0][0][1][0] + self.residues[n][0][0][0][1][1] + ', f'
      script = script + self.residues[n][0][0][0][0] + self.residues[n][0][0][0][1][0] + self.residues[n][0][0][0][1][1] + '\n\n'
      script = script + 'plot [' + plot_size[0] + ':' + plot_size[1] + '] f(x) notitle,\\\n'
      script = script + '\"' + self.residues[0][0][0][0][1][0]
      script = script + self.residues[0][0][0][0][1][1] + '\" index '
      script = script + `n` + ' using 1:3 title "'
      script = script + self.residues[n][0][0][0][0] + self.residues[n][0][0][0][1][0] + self.residues[n][0][0][0][1][1] + '" ls 1\n'
      script = script + '\n\n'

    for n in range(len(self.residues)):
      script = script + 'root1=(-(b' + self.residues[n][0][0][0][0] + self.residues[n][0][0][0][1][0] + self.residues[n][0][0][0][1][1]
      script = script + '-1.0)+((b' + self.residues[n][0][0][0][0] + self.residues[n][0][0][0][1][0] + self.residues[n][0][0][0][1][1] + '-1.0)**2-4.0*a'
      script = script + self.residues[n][0][0][0][0] + self.residues[n][0][0][0][1][0] + self.residues[n][0][0][0][1][1] + '*c' + self.residues[n][0][0][0][0] + self.residues[n][0][0][0][1][0] + self.residues[n][0][0][0][1][1]
      script = script + ')**0.5)*0.5/c' + self.residues[n][0][0][0][0] + self.residues[n][0][0][0][1][0] + self.residues[n][0][0][0][1][1] + '\n'
      script = script + 'root2=(-(b' + self.residues[n][0][0][0][0] + self.residues[n][0][0][0][1][0] + self.residues[n][0][0][0][1][1]
      script = script + '-1.0)-((b' + self.residues[n][0][0][0][0] + self.residues[n][0][0][0][1][0] + self.residues[n][0][0][0][1][1] + '-1.0)**2-4.0*a'
      script = script + self.residues[n][0][0][0][0] + self.residues[n][0][0][0][1][0] + self.residues[n][0][0][0][1][1] + '*c' + self.residues[n][0][0][0][0] + self.residues[n][0][0][0][1][0] + self.residues[n][0][0][0][1][1]
      script = script + ')**0.5)*0.5/c' + self.residues[n][0][0][0][0] + self.residues[n][0][0][0][1][0] + self.residues[n][0][0][0][1][1] + '\n'
      script = script + 'print "' + self.residues[n][0][0][0][0] + self.residues[n][0][0][0][1][0] + self.residues[n][0][0][0][1][1] + ' ", '
      script = script + 'root1, d' + self.residues[n][0][0][0][0] + self.residues[n][0][0][0][1][0] + self.residues[n][0][0][0][1][1]
      script = script + ' + e' + self.residues[n][0][0][0][0] + self.residues[n][0][0][0][1][0] + self.residues[n][0][0][0][1][1] + '*root1'
      script = script + ' + f' + self.residues[n][0][0][0][0] + self.residues[n][0][0][0][1][0] + self.residues[n][0][0][0][1][1] + '*root1**2\n'
      script = script + 'print "' + self.residues[n][0][0][0][0] + self.residues[n][0][0][0][1][0] + self.residues[n][0][0][0][1][1] + ' ", '
      script = script + 'root2, d' + self.residues[n][0][0][0][0] + self.residues[n][0][0][0][1][0] + self.residues[n][0][0][0][1][1]
      script = script + ' + e' + self.residues[n][0][0][0][0] + self.residues[n][0][0][0][1][0] + self.residues[n][0][0][0][1][1] + '*root2'
      script = script + ' + f' + self.residues[n][0][0][0][0] + self.residues[n][0][0][0][1][0] + self.residues[n][0][0][0][1][1] + '*root2**2\n\n'
    
    self.write_file(self.s3e_root + '/' + self.residues[0][0][0][0][1][0]
      + self.residues[0][0][0][0][1][1] + '.gnu', 'w', script)

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
