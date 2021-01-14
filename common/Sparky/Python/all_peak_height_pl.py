import sparky
import tkMessageBox

def all_peak_height(session):

    def residue_number(peak):
        # sort based only on digits extracted from the label
        number = ''
        number_started = False
        for char in peak.label:
            if char.isdigit():
                number_started = True
                number += char
            elif number_started:
                return int(number)

    selected_spectrum = session.selected_spectrum()

    for spectrum in session.project.spectrum_list():
        sfo1 = selected_spectrum.hz_per_ppm[0]
        sfo2 = selected_spectrum.hz_per_ppm[1]
        file = open(sparky.user_sparky_directory + "/Lists/" + spectrum.name + ".list", 'w')
        line = "      User         w1         w2     w1 (Hz)    w2 (Hz)  Data Height \n\n"
        file.write(line)
        peaks_information = []

        #Based on the peaks in the selected spectrum:
        #=================================================================
        for peak in selected_spectrum.peak_list():
            h = spectrum.data_height(peak.position)
            l =  peak.label.text
            w1 = peak.frequency[0]
            w2 = peak.frequency[1]
            hz1 = w1 * sfo1
            hz2 = w2 * sfo2
            peaks_information.append(Peak_information(l,w1,w2,hz1,hz2,h))

        spi = sorted(peaks_information, key=residue_number)

        for peak in spi:
            line = "%11s%17.9f%17.9f%17.9f%17.9f%21.9f \n" % (peak.label, peak.w1, peak.w2, peak.hz1, peak.hz2, peak.height)
            file.write(line)

        file.close()

    n_peaks = len(selected_spectrum.peak_list())
    n_spec = len(session.project.spectrum_list())
    message = 'Successfully written %d peaks\nin %d spectra' % (n_peaks, n_spec)
    tkMessageBox.showinfo('Peak heights', message)



class Peak_information:
   def __init__(self, label, w1, w2, hz1, hz2, height):
      self.label = label
      self.w1 = w1
      self.w2 = w2
      self.hz1 = hz1
      self.hz2 = hz2
      self.height = height

   def __repr__(self):
      return repr((self.label, self.w1, self.w2, self.hz1, self.hz2, self.height))
