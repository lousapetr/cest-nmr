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

        # num_peaks = tkutil.entry_field(self.top, 'Number of peaks used for noise determination:', '20000', 6)
        self.num_peaks = tkutil.entry_row(noise_handling_dialog,
                                        'Number of peaks used for noise determination:',
                                        ('', '10000', 6))
        self.num_peaks.frame.pack(side='top', anchor='w')

        self.hz_range_widget = [None, None]
        self.protect = tkutil.entry_row(noise_handling_dialog,
                                        'Ranges [ppm] around peaks, where no peaks for noise determination will be placed:',
                                        ('w1:', '0.5', 3), ('   w2:', '0.1', 3))
        # (self.protect1, self.protect2) = protect.variables
        self.protect.frame.pack(side='top', anchor='w')

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
        pass  # for folding purposes only

    def clear_handling_output_cb(self):
        self.handling_output.delete(1.0, 'end')

    def _random_peaks(self, N):
        """
        Return `N` random peaks uniformly scattered across the `self.spectrum` bounds.

        Returns vertical 2D numpy array - N x 2.
        """
        spectrum = self.session.selected_spectrum()
        return np.random.uniform(low=spectrum.region[0],
                                 high=spectrum.region[1],
                                 size=(N, 2)
                                 )

    def _generate_noise_peaks(self):
        """
        Generate `N = self.num_peaks` new peaks that are far (as defined by protect)
        from all predefined peaks (stored in spectrum.peak_list).

        Returns vertical 2D python list - N x 2.
        """
        spectrum = self.session.selected_spectrum()
        peak_list = np.array([p.frequency for p in spectrum.peak_list()])
        N = int(self.num_peaks.variables[0].get())
        protect = tuple(float(x.get()) for x in self.protect.variables)

        result = self._random_peaks(N)

        collisions = 1
        i = 0  # safety guard against infinite loops
        while collisions > 0 and i < 100:
            # creates 2D matrix N x len(peak_list) with distances in w1 (resp. w2)
            dist_matrix_w1 = np.abs(result[:, [0]] - peak_list[:, 0])
            dist_matrix_w2 = np.abs(result[:, [1]] - peak_list[:, 1])
            # collision occurs if both distances at given pair are less then protect
            collision_matrix = (dist_matrix_w1 < protect[0]) & (dist_matrix_w2 < protect[1])
            collision_array =  np.any(collision_matrix, axis=1)  # find any True in each row
            assert collision_array.shape[0] == N
            collisions = np.sum(collision_array)
            self.handling_output.insert('end', "{}th round; {:d} collisions found.\n".format(i, collisions))

            # generate new peaks at the collision spots
            result[collision_array] = self._random_peaks(collisions)

            i += 1

        return result.tolist()

    def noise(self):
        spectrum_list = self.session.project.spectrum_list()
        spectra_names = [s.name for s in spectrum_list]

        start_time = time.time()
        noise_peaklist = self._generate_noise_peaks()

        # read peak heights
        # matrix "noise peak number" (rows) x "spectrum" (columns)
        noise_heights = np.zeros(shape=(len(noise_peaklist), len(spectrum_list)))
        for i_s, s in enumerate(spectrum_list):
            for i_p, p in enumerate(noise_peaklist):
                noise_heights[i_p, i_s] = s.data_height(p)

        self.handling_output.insert('end', "{:d} random peak positions created.\n".format(len(noise_peaklist)))
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

        ##### PEAK WRITING
        # first delete the directory, then create again
        noise_dir = sparky.user_sparky_directory + "/Lists_noise/"
        try:
            shutil.rmtree(noise_dir)  # try to remove the directory
        except OSError:
            pass  # if does not exist before, do nothing
        os.makedirs(noise_dir)

        np.savetxt(fname=noise_dir+'noise_coords.list',
                   X=np.array(noise_peaklist),
                   fmt='%10.3f')
        np.savetxt(fname=noise_dir+'noise_heights_full.csv',
                   X=noise_heights,
                   fmt='%20.3f',
                   header=''.join('{:>20s}'.format(n) for n in spectra_names))
        self.handling_output.insert('end', 'All peak coordinates written in file {}.\n'.format(noise_dir+'noise_coords.csv'))
        self.handling_output.insert('end', 'All peak heights written in file {}.\n'.format(noise_dir+'noise_heights_full.csv'))
        writing_time = time.time()
        self.handling_output.insert('end', 'The Peak Writing took {:.3f} seconds\n'.format(writing_time - showing_time))
        self.handling_output.insert('end', 'Done\n')
