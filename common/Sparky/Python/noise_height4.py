import os
import sparky
import shutil
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

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
        self.spectrum_list = self.session.project.spectrum_list()
        self.spectra_names = [s.name for s in self.spectrum_list]
        self.noise_path = 'Lists_noise/'

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

        self.method = Tkinter.IntVar()
        self.method.set(1)
        method_frame = Tkinter.Frame(noise_handling_dialog)
        Tkinter.Label(method_frame, text='Select method for noise calculation:').pack(side='left')
        Tkinter.Radiobutton(method_frame, text='Naive', variable=self.method, value=1).pack(side='left')
        Tkinter.Radiobutton(method_frame, text='Iterative', variable=self.method, value=2).pack(side='left')
        Tkinter.Radiobutton(method_frame, text='Median abs.dev.', variable=self.method, value=3).pack(side='left')
        method_frame.pack(side='top', anchor='w')

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
                                 ('Determine noise', self.noise),
                                 ('Show peaks', self.show_peaks),
                                 ('Quit', self.close_cb))
        pobr.frame.pack()

        # ----------------------------------------------------------------------------
        # END NOISE HANDLING DIALOG
        # ----------------------------------------------------------------------------
        pass  # for folding purposes only

    def clear_handling_output_cb(self):
        self.handling_output.delete(1.0, 'end')

    def show_peaks(self):
        """
        Puts the noise peaks to spectrum.
        Warning: creates real peaks. Next noise generating will try to avoid them.
        """
        for peak in self.noise_peaklist:
            self.session.selected_spectrum().place_peak(peak)
        self.handling_output.insert('end', '{} peaks were shown.\n'.format(len(self.noise_peaklist)))
        self.handling_output.insert('end', 'Warning: The peaks are real now, do NOT rerun the noise determination!\n')

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

    def _generate_noise_peaks(self, N):
        """
        Generate `N = self.num_peaks` new peaks that are far (as defined by protect)
        from all predefined peaks (stored in spectrum.peak_list).

        Returns vertical 2D python list - N x 2.
        """
        spectrum = self.session.selected_spectrum()
        peak_list = np.array([p.frequency for p in spectrum.peak_list()])
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

            # uncomment to see the necessary number of rounds
            # self.handling_output.insert('end', "{}th round; {:d} collisions found.\n".format(i, collisions))

            # generate new peaks at the collision spots
            result[collision_array] = self._random_peaks(collisions)

            i += 1

        return result.tolist()

    def _write_peaks(self):
        noise_dir = sparky.user_sparky_directory + '/' + self.noise_path

        if not os.path.exists(noise_dir):
            os.makedirs(noise_dir)

        np.savetxt(fname=noise_dir+'noise_coords.list',
                   X=np.array(self.noise_peaklist),
                   fmt='%10.3f')

        np.savetxt(fname=noise_dir+'noise_heights_full.csv',
                   X=self.noise_heights,
                   fmt='%20.3f',
                   header=''.join('{:>20s}'.format(n) for n in self.spectra_names))

        self.handling_output.insert('end', 'All peak coordinates written in file {}.\n'.format(self.noise_path+'noise_coords.csv'))
        self.handling_output.insert('end', 'All peak heights written in file {}.\n'.format(self.noise_path+'noise_heights_full.csv'))

        # uncomment for full path writing
        # self.handling_output.insert('end', 'All peak coordinates written in file {}\n'.format(noise_dir+'noise_coords.csv'))
        # self.handling_output.insert('end', 'All peak heights written in file {}\n'.format(noise_dir+'noise_heights_full.csv'))
        pass

    def _write_result(self, filename, data, header=None):
        """
        Write resulting noise - one number for each spectrum.
        """
        full_path = sparky.user_sparky_directory + '/' + self.noise_path + filename
        with open(full_path, 'w') as f:
            if header:
                if header[-1] != '\n':
                    header += '\n'
                f.write(header)

            for i in range(len(data)):
                f.write('{:<20} {:20.3f}\n'.format(self.spectra_names[i], data[i]))

        self.handling_output.insert('end', 'Noise levels written in {}\n'.format(self.noise_path + filename))
        # self.handling_output.insert('end', 'Noise levels written in {}.\n'.format(full_path))
        pass

    def _naive_std(self):
        """
        Calculate standard deviation for peaks from each column (spectrum).

        Return numpy array `len(spectrum_list)` x 1
        """
        # axis=0 calculates by column
        return self.noise_heights.std(axis=0)

    def _iterative_std(self, max_sigma=6, plot=False, verbose=False):
        """
        Iteratively remove outliers beyond `max_sigma` * std.

        If plot=True, create two boxplots - noise heights before and after filtering.
        If verbose=True, print out the intermediate steps.

        Return numpy array `len(spectrum_list)` x 1
        """
        self.handling_output.insert('end', 'Iterative sigma calculation starts.\n')
        noise_filtered = self.noise_heights.copy()

        if plot is True:
            imgpath = sparky.user_sparky_directory + '/' + self.noise_path
            plt.figure(1)
            plt.boxplot(noise_filtered[:,:10])
            plt.savefig(imgpath+'orig.png')
            plt.clf()

        num_rounds = 0
        orig_stddev = np.std(noise_filtered)
        while True:
            stddev = np.std(noise_filtered, axis=0)
            mask = (noise_filtered > max_sigma * stddev) | (noise_filtered < - max_sigma * stddev)
            noise_filtered[mask] = np.nan
            noise_filtered = np.ma.masked_invalid(noise_filtered)
            num_rounds += 1

            if verbose is True:
                self.handling_output.insert('end', '    {} values filtered out'.format(mask.sum()))
                self.handling_output.insert('end', ', {} left.'.format(noise_filtered.count()))
                self.handling_output.insert('end', ' Current overall STD = {}\n'.format(noise_filtered.std()))
            if not np.any(mask):  # no values were filtered
                break

        noise_result = self.noise_heights.copy()
        noise_result[noise_filtered.mask] = np.nan

        final_stddev = np.std(noise_filtered)
        final_stddev_percent = 100.0 * final_stddev / orig_stddev
        num_filtered = noise_filtered.mask.sum()
        percent_filtered = 100.0 * num_filtered / self.noise_heights.size
        self.handling_output.insert('end',
            '    After {} rounds, {} values ({:.3f} %) was filtered out\n'.format(num_rounds, num_filtered, percent_filtered))
        self.handling_output.insert('end',
            '    Sigma dropped from {:.0f} to {:.0f} ({:.2f} %)\n'.format(orig_stddev, final_stddev, final_stddev_percent))

        if plot is True:
            plt.figure(2)
            plt.boxplot(noise_result[:,:10])
            plt.savefig(imgpath+'filtered.png')
            plt.clf()

        return np.std(noise_filtered, axis=0)

    def _median_absolute_deviation(self):
        """
        Calculate Median Average Deviation for noise in each spectra.
        https://en.wikipedia.org/wiki/Median_absolute_deviation

        Return numpy array `len(spectrum_list)` x 1
        """
        noise_median = np.median(self.noise_heights, axis=0)
        deviations = np.abs(self.noise_heights - noise_median)
        return np.median(deviations, axis=0)

    def _plot_histograms(self, spectrum_no=0):
        """
        Create a histogram overlaying noise peak heights and gauss distributions
        calculated using various methods
        """
        naive = self._naive_std()
        iterative = self._iterative_std()
        mad = self._median_absolute_deviation()

        plt.figure(10)
        spect_no = 0
        mean = self.noise_heights[:,spect_no].mean()
        x_lim = 3*naive[spect_no]
        x_scale = np.linspace(-x_lim, x_lim, num=1000)
        gauss = lambda sigma: np.exp(-0.5* (x_scale-mean)**2 / sigma**2) / np.sqrt(2*np.pi * sigma**2)

        plt.hist(self.noise_heights[:,spect_no], bins=1000, normed=True, cumulative=False, alpha=0.5, color='gray')
        plt.plot(x_scale, gauss(naive[spect_no]), '--', c='red', lw=3, label='naive')
        plt.plot(x_scale, gauss(iterative[spect_no]), '--', c='green', lw=3, label='iterative')
        plt.plot(x_scale, gauss(mad[spect_no]), '--', c='blue', lw=3, label='median')
        plt.xlim([-x_lim, x_lim])
        plt.ylim([0, 3e-7])
        plt.legend()
        plt.savefig(sparky.user_sparky_directory+'/'+self.noise_path+'hist.png')
        plt.clf()

    def noise(self):
        # start_time = time.time()
        self.N = int(self.num_peaks.variables[0].get())
        self.noise_peaklist = self._generate_noise_peaks(self.N)
        noise_peaklist = self.noise_peaklist

        # read peak heights
        # matrix "noise peak number" (rows) x "spectrum" (columns)
        self.noise_heights = np.zeros(shape=(len(noise_peaklist), len(self.spectrum_list)))
        for i_s, s in enumerate(self.spectrum_list):
            for i_p, p in enumerate(noise_peaklist):
                self.noise_heights[i_p, i_s] = s.data_height(p)

        self.handling_output.insert('end', "{:d} random peak positions created.\n".format(len(noise_peaklist)))
        # picking_time = time.time()
        # self.handling_output.insert('end', 'The Random Picking took {:.3f} seconds\n'.format(picking_time - start_time))

        self._write_peaks()

        tttttif self.method.get() == 1:
            naive = self._naive_std()
            self._write_result(filename='naive_std.out',
                               data=naive,
                               header='# naive sigma'
                               )
        elif self.method.get() == 2:
            iterative = self._iterative_std()
            self._write_result(filename='iterative_std.out',
                               data=iterative,
                               header='# iterative sigma'
                               )
        elif self.method.get() == 3:
            mad = self._median_absolute_deviation()
            self._write_result(filename='mad.out',
                               data=mad,
                               header='# median absolute deviation'
                               )

        histogram_wanted = False
        if histogram_wanted is True:
            self._plot_histograms()

        # writing_time = time.time()
        # self.handling_output.insert('end', 'The Peak Writing took {:.3f} seconds\n'.format(writing_time - picking_time))
        self.handling_output.insert('end', 'Done\n')
        return
