import os
import sparky
import shutil
import numpy as np
import Tkinter
import sputil
import tkutil
import random
import time


def show_noise(session):
    sputil.the_dialog(NoiseDialog, session).show_window(1)


class NoiseDialog(tkutil.Dialog, tkutil.Stoppable):
    def __init__(self, session):
        self.session = session
        self.project = session.project

        tkutil.Dialog.__init__(self, session.tk, 'Noise specification')

        f = Tkinter.Frame(self.top)
        f.pack(side='top', anchor='w')

        # ----------------------------------------------------------------------------
        # BEGIN NOISE HANDLING DIALOG
        # ----------------------------------------------------------------------------

        noise_handling_dialog = Tkinter.Frame(self.top)
        noise_handling_dialog.pack(side='top', anchor='w')

        num_peaks = tkutil.entry_field(self.top, 'Number of peaks used for noise determination:', '10000', 6)
        self.num_peaks = num_peaks.variable
        num_peaks.frame.pack(side='top', anchor='w')

        self.hz_range_widget = [None, None]
        protect = tkutil.entry_row(noise_handling_dialog,
                                   'Ranges [ppm] around peaks, where no peaks for noise determination will be placed:',
                                   ('w1:', '0.5', 3), ('   w2:', '0.1', 3))
        (self.protect1, self.protect2) = protect.variables
        protect.frame.pack(side='top', anchor='w')

        hod = Tkinter.Frame(noise_handling_dialog)
        hod.pack(side='top', anchor='w')

        ho = tkutil.scrolling_text(hod, height=9, width=100)
        ho.frame.pack(side='top', anchor='nw')
        self.handling_output = ho.text

        #
        spectra_assign_dialog = Tkinter.Frame(self.top)
        spectra_assign_dialog.pack(side='top', anchor='w')

        spectra_assign_widget = Tkinter.Frame(spectra_assign_dialog)
        spectra_assign_widget.pack(side='top', anchor='w')

        pobr = tkutil.button_row(noise_handling_dialog,
                                 ('Place peaks for noise determination', self.noise),
                                 ('Clear handling output', self.clear_handling_output_cb),
                                 ('Quit', self.close_cb))
        pobr.frame.pack()

        # ----------------------------------------------------------------------------
        # END NOISE HANDLING DIALOG
        # ----------------------------------------------------------------------------
        pass

    def clear_handling_output_cb(self):
        self.handling_output.delete(1.0, 'end')

    def noise(self):
        start_time = time.time()
        noise_peaklist = []
        protect_1 = float(self.protect1.get())
        protect_2 = float(self.protect2.get())
        spectrum = self.session.selected_spectrum()
        peak_list = [p.frequency for p in spectrum.peak_list()]
        range_1_min, range_2_min = spectrum.region[0]
        range_1_max, range_2_max = spectrum.region[1]
        tried = 0
        num_peaks = float(self.num_peaks.get())
        while len(noise_peaklist) < num_peaks:
            tried += 1
            rejected = False
            new1 = random.uniform(range_1_min, range_1_max)
            new2 = random.uniform(range_2_min, range_2_max)
            for w1, w2 in peak_list:
                if abs(new1 - w1) < protect_1 and abs(new2 - w2) < protect_2:
                    rejected = True
                    break
            if not rejected:
                noise_peaklist.append((new1, new2))

        self.handling_output.insert('end', "{:d} random peak positions created.\n".format(len(noise_peaklist)))
        self.handling_output.insert('end', 'Writing output into the directory Sparky/Lists_noise in progress.\n')
        self.handling_output.insert('end',
                                    'In total {:d} peaks were tried, '
                                    'total acceptance rate was {:.3f}%\n'.format(tried, 100 * num_peaks / tried))
        picking_time = time.time()
        self.handling_output.insert('end', 'The Random Picking took {:.3f} seconds\n'.format(picking_time - start_time))

        ########################################################################################################
        #    THIS IS USED FOR THE CASE YOU WANT TO VIEW, WHERE THE PEAKS WERE PLACED                           #
        #    BUT RE-RUN IS NOT POSSIBLE, BECAUSE NEXT TIME THESE PEAKS WILL CONSIDERED AS REAL ONE            #
        ########################################################################################################
        for peak in noise_peaklist:
            self.session.selected_spectrum().place_peak(peak)
        showing_time = time.time()
        self.handling_output.insert('end', 'The Peaks Showing took {:.3f} seconds\n'.format(showing_time - picking_time))
        ########################################################################################################

        # first delete the directory, then create again
        noise_dir = sparky.user_sparky_directory + "/Lists_noise/"
        try:
            shutil.rmtree(noise_dir)  # try to remove the directory
        except OSError:
            pass  # if not exists before, do nothing
        os.makedirs(noise_dir)

        for i in range(len(self.session.project.spectrum_list())):
            spectrum = self.session.project.spectrum_list()[i]
            output_file = open(noise_dir + spectrum.name + ".list", 'w')

            # Based on the peaks in the noise_peaklist list:
            # =================================================================
            for peak in noise_peaklist:
                h = spectrum.data_height(peak)
                output_file.write("%11.3f%11.3f%16.3f \n" % (peak[0], peak[1], h))
            output_file.close()

        writing_time = time.time()
        self.handling_output.insert('end', 'The Peak Writing took {:.3f} seconds\n'.format(writing_time - showing_time))
        self.handling_output.insert('end', 'Done\n')
