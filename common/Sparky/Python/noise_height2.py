import os
import sys
import sparky
import string
import shutil

import Tkinter
import popen2
import pyutil
import sputil
import tkutil
import random


def noise_height(session):
    sputil.the_dialog(NoiseDialog, session).show_window(1)


class NoiseDialog(tkutil.Dialog, tkutil.Stoppable):
    def __init__(self, session):

        self.session = session
        self.project = session.project

        tkutil.Dialog.__init__(self, session.tk, 'Noise specification')

        f = Tkinter.Frame(self.top)
        f.pack(side='top', anchor='w')

        #    hbutton = tkutil.checkbutton(self.top, 'Show spectra handling dialog', 0)
        #    hbutton.button.pack(side = 'top', anchor = 'w')

        # ----------------------------------------------------------------------------
        # BEGIN NOISE HANDLING DIALOG
        # ----------------------------------------------------------------------------
        #
        # hbutton = tkutil.checkbutton(self.top, 'Show spectra handling dialog', 0)
        # hbutton.button.pack(side = 'top', anchor = 'w')

        noise_handling_dialog = Tkinter.Frame(self.top)
        noise_handling_dialog.pack(side='top', anchor='w')

        montecarlo = tkutil.entry_field(self.top, 'Number of peaks used for noise determination:', '5000', 6)
        self.mc = montecarlo.variable
        montecarlo.frame.pack(side='top', anchor='w')

        self.hz_range_widget = [None, None]
        protect = tkutil.entry_row(noise_handling_dialog,
                                   'Ranges [ppm] around peaks, where no peaks for noise determination will be placed:',
                                   ('w1:', '0.5', 3), ('   w2:', '0.5', 3))
        (self.protect1,
         self.protect2) = protect.variables
        protect.frame.pack(side='top', anchor='w')

        hod = Tkinter.Frame(noise_handling_dialog)
        hod.pack(side='top', anchor='w')

        # w6 = Tkinter.Label(hod, text = 'Spectra handling output:')
        # w6.pack(side = 'top', anchor = 'nw')

        ho = tkutil.scrolling_text(hod, height=9, width=100)
        ho.frame.pack(side='top', anchor='nw')
        self.handling_output = ho.text

        #
        spectra_assign_dialog = Tkinter.Frame(self.top)
        spectra_assign_dialog.pack(side='top', anchor='w')

        spectra_assign_widget = Tkinter.Frame(spectra_assign_dialog)
        spectra_assign_widget.pack(side='top', anchor='w')

        # aod = Tkinter.Frame(spectra_assign_widget)
        # aod.pack(side = 'top', anchor = 'w')

        # ao = tkutil.scrolling_text(aod, height = 9, width = 77)
        # ao.frame.pack(side = 'top', anchor = 'nw')
        # self.assign_output = ao.text
        #

        pobr = tkutil.button_row(noise_handling_dialog,
                                 ('place peaks for noise determination', self.noise),
                                 ('Clear handling output', self.clear_handling_output_cb),
                                 ('Quit', self.close_cb))
        pobr.frame.pack()

    # ----------------------------------------------------------------------------
    # END NOISE HANDLING DIALOG
    # ----------------------------------------------------------------------------

    # hbutton.show_widget_cb(noise_handling_dialog, None)
    # hbutton.map_widget(noise_handling_dialog)

    def clear_handling_output_cb(self):

        self.handling_output.delete(1.0, 'end')

    # class All_peak_height:
    def noise(self):
        # self.session = sparky.self.session_list[0]
        peaks_information = []
        accepted = 0
        pro1 = float(self.protect1.get())
        pro2 = float(self.protect2.get())
        num_mc = float(self.mc.get())
        tried = 0
        while accepted < num_mc:
            tried += 1
            rejected = 0
            new1 = (self.session.selected_spectrum().region[1][0] - self.session.selected_spectrum().region[0][
                0]) * random.random() + self.session.selected_spectrum().region[0][0]
            new2 = (self.session.selected_spectrum().region[1][1] - self.session.selected_spectrum().region[0][
                1]) * random.random() + self.session.selected_spectrum().region[0][1]
            for j in range(len(self.session.selected_spectrum().peak_list())):
                w1 = self.session.selected_spectrum().peak_list()[j].frequency[0]
                w2 = self.session.selected_spectrum().peak_list()[j].frequency[1]
                leftlimitw1 = w1 - pro1
                rightlimitw1 = w1 + pro1
                leftlimitw2 = w2 - pro2
                rightlimitw2 = w2 + pro2
                if leftlimitw1 < new1 < rightlimitw1 and leftlimitw2 < new2 < rightlimitw2:
                    rejected = 1
                    break
            if rejected == 0:
                peaks_information.append(NoisePeakInformation(new1, new2))
                accepted = accepted + 1

        self.handling_output.insert('end', "{:d} random peak positions created.\n".format(len(peaks_information)))
        self.handling_output.insert('end', 'Writing output into the directory Sparky/Lists_noise in progress.\n')
        self.handling_output.insert('end', 'In total {:d} peaks were tried,'
                                           'total acceptance rate was {:.3f}%\n'.format(tried, 1.0 * accepted / tried * 100))
        # print len(peaks_information)
        # print peaks_information[0]
        # print peaks_information[0].new1
        # print peaks_information[0].new2

        ########################################################################################################
        #    THIS IS USED FOR THE CASE YOU WANT TO VIEW, WHERE THE PEAKS WERE PLACED                           #
        #    BUT RE-RUN IS NOT POSSIBLE, BECAUSE NEXT TIME THEESE PEAKS WILL CONSIDERED AS REAL ONE            #
        ########################################################################################################
        for j in range(len(peaks_information)):
            self.session.selected_spectrum().place_peak((peaks_information[j].new1, peaks_information[j].new2))
            ########################################################################################################

        # first delete the directory, then create again
        noise_dir = sparky.user_sparky_directory + "/Lists_noise/"
        try:
            shutil.rmtree(noise_dir)  # try to remove the directory
        except OSError:
            pass  # if not exists before, do nothing
        os.makedirs(noise_dir)
        for i in range(len(self.session.project.spectrum_list())):
            output_file = open(noise_dir + self.session.project.spectrum_list()[i].name + ".list", 'w')
            # line="      User         w1         w2   Data Height \n"
            # output_file.write(line)
            # line="\n"
            # output_file.write(line)
            # noise_information=[]
            # Based on peak position in each spectrum (based on its own peaks)
            # =================================================================
            # for j in range(len(self.session.project.spectrum_list()[i].peak_list())):
            #   h=self.session.project.spectrum_list()[i].data_height(self.session.project.spectrum_list()[i].peak_list()[j].position)
            #   l=self.session.project.spectrum_list()[i].peak_list()[j].label.text
            #   w1=self.session.project.spectrum_list()[i].peak_list()[j].frequency[0]
            #   w2=self.session.project.spectrum_list()[i].peak_list()[j].frequency[1]

            # Based on the peaks in the selected spectrum:
            # =================================================================
            for j in range(len(peaks_information)):
                # h=self.session.project.spectrum_list()[i].data_height(self.session.project.spectrum_list()[i].peak_list()[j].position)
                h = self.session.project.spectrum_list()[i].data_height(
                    (peaks_information[j].new1, peaks_information[j].new2))
                # l= self.session.selected_spectrum().peak_list()[j].label.text
                # w1=self.session.selected_spectrum().peak_list()[j].frequency[0]
                # w2=self.session.selected_spectrum().peak_list()[j].frequency[1]
                #
                w1 = peaks_information[j].new1
                w2 = peaks_information[j].new2
                line = "%11.3f%11.3f%16.3f \n" % (w1, w2, h)
                output_file.write(line)
                # noise_information.append(self.PeakInformation(w1,w2,h))

            # spi=sort_peaks_information
            # spi=sorted(peaks_information, key=lambda a:a.label)

            # Based on peak position in each spectrum (based on its own peaks)
            # =================================================================
            # for j in range(len(self.session.project.spectrum_list()[i].peak_list())):

            # Based on the peaks in the selected spectrum:
            # =================================================================
            # for j in range(len(self.session.selected_spectrum().peak_list())):
            #   line="%11.3f%11.3f%16.3f \n" % (noise_information[j].w1, noise_information[j].w2, noise_information[j].height)
            #   output_file.write(line)

            output_file.close()
        self.handling_output.insert('end', 'Done\n')

    #      for i in range(len(self.session.project.spectrum_list())):
    #         file=open(sparky.user_sparky_directory + "/Lists_noise/" + self.session.project.spectrum_list()[i].name + ".list", 'w')
    #         #line="      User         w1         w2   Data Height \n"
    #         #file.write(line)
    #         #line="\n"
    #         #file.write(line)
    #         peaks_information=[]
    #         #Based on peak position in each spectrum (based on its own peaks)
    #         #=================================================================
    #         #for j in range(len(self.session.project.spectrum_list()[i].peak_list())):
    #         #   h=self.session.project.spectrum_list()[i].data_height(self.session.project.spectrum_list()[i].peak_list()[j].position)
    #         #   l=self.session.project.spectrum_list()[i].peak_list()[j].label.text
    #         #   w1=self.session.project.spectrum_list()[i].peak_list()[j].frequency[0]
    #         #   w2=self.session.project.spectrum_list()[i].peak_list()[j].frequency[1]
    #
    #         #Based on the peaks in the selected spectrum:
    #         #=================================================================
    #         for j in range(len(self.session.selected_spectrum().peak_list())):
    #            h=self.session.project.spectrum_list()[i].data_height(self.session.selected_spectrum().peak_list()[j].position)
    #            #l= self.session.selected_spectrum().peak_list()[j].label.text
    #            #w1=self.session.selected_spectrum().peak_list()[j].frequency[0]
    #            #w2=self.session.selected_spectrum().peak_list()[j].frequency[1]
    #            #
    #            peaks_information.append(self.PeakInformation(h))
    #
    #         #spi=sort_peaks_information
    #         #spi=sorted(peaks_information, key=lambda a:a.label)
    #
    #
    #         #Based on peak position in each spectrum (based on its own peaks)
    #         #=================================================================
    #         #for j in range(len(self.session.project.spectrum_list()[i].peak_list())):
    #
    #
    #         #Based on the peaks in the selected spectrum:
    #         #=================================================================
    #         for j in range(len(self.session.selected_spectrum().peak_list())):
    #            line="%16.3f \n" % (peaks_information[j].height)
    #            file.write(line)
    #
    #         file.close()

    # self.close_cb
    class PeakInformation:
        def __init__(self, height):
            self.height = height

        def __repr__(self):
            return repr(self.height)


class NoisePeakInformation:
    def __init__(self, new1, new2):
        self.new1 = new1
        self.new2 = new2

    def __repr__(self):
        return repr((self.new1, self.new2))


# def all_peak_height(self.session):
#   #self.session = sparky.self.session_list[0]
#   for i in range(len(self.session.project.spectrum_list())):
#      file=open(sparky.user_sparky_directory + "/Lists_ha/" + self.session.project.spectrum_list()[i].name + ".list", 'w')
#      line="\tUser\tw1\tw2\tData Height\n"
#      file.write(line)
#      line="\n"
#      file.write(line)
#      for j in range(len(self.session.project.spectrum_list()[i].peak_list())):
#         h=self.session.project.spectrum_list()[i].data_height(self.session.project.spectrum_list()[i].peak_list()[j].position)
#         l=self.session.project.spectrum_list()[i].peak_list()[j].label.text
#         w1=self.session.project.spectrum_list()[i].peak_list()[j].frequency[0]
#         w2=self.session.project.spectrum_list()[i].peak_list()[j].frequency[1]
#
#         line="%11s%11.3f%11.3f\t%13.0f\n" % (l, w1, w2, h)
#         file.write(line)
#
#      file.close()
#

def show_noise(session):
    sputil.the_dialog(NoiseDialog, session).show_window(1)
