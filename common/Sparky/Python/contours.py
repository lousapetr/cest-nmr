def setCont(session):

 p = session.selected_view()

 from sparky import Spectrum
 s = session.selected_spectrum().noise
 
 from sparky import Contour_Levels

 plev = Contour_Levels()
 plev.lowest = s*4
 plev.factor = 1.3
 plev.levels = 20
 plev.color = 'red-blue'

 nlev = Contour_Levels()
 nlev.lowest = -s*4
 nlev.factor = 1.3
 nlev.levels = 20
 nlev.color = 'green-blue'


 p.positive_levels = plev
 p.negative_levels = nlev




