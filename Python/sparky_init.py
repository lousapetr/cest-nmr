def initialize_session(session):

  def wp_command(s = session):
    import write_precisely
    write_precisely.write_precisely(s)

  session.add_command("wp", "Write precisely", wp_command)

  def ha_command(s = session):
    import all_peak_height
    all_peak_height.all_peak_height(s)

  session.add_command("ha", "Height all peaks", ha_command)

  def ho_command(s = session):
    import all_own_peak_height
    all_own_peak_height.all_own_peak_height(s)

  session.add_command("ho", "Height own peaks", ho_command)

#   def hn_command(s = session):
#     import noise_height2
#     noise_height2.show_noise(s)
# 
#   session.add_command("hn", "Height of noise", hn_command)

  def hn_command(s = session):
    import noise_height3
    noise_height3.show_noise(s)

  session.add_command("hn", "Height of noise", hn_command)

  def cont_comm(s = session):
    import contours
    contours.setCont(s)

  session.add_command('cc', 'Set contour levels', cont_comm)

  def sv_command(s = session):
    import s3e_kada
    s3e_kada.show_s3e(s)

  session.add_command("sv", "S3E veve", sv_command)

  def ca_command(s = session):
    import peak_center_all
    peak_center_all.peak_center_all(s)

  session.add_command("ca", "Center all", ca_command)

