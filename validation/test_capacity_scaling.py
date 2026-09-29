import numpy as np
from controls.droop import DroopController
from controls.voltage_droop import VoltageDroopController
from models.synchronous_generator import SynchronousGenerator
from models.grid_forming_inverter import GridFormingInverter
from models.grid_following_inverter import GridFollowingInverter
OMEGA0=2*np.pi*50
def test_sg_common_base_scaling():
    sg=SynchronousGenerator("SG",H=5,D=10,Pm=.2,omega0=OMEGA0,E_internal=1.05,Xd_prime=.20,Sr=.5,S_base=1)
    assert abs(sg.H_system-2.5)<1e-14 and abs(sg.Xd_prime-.4)<1e-14 and abs(sg.D-5)<1e-14
    assert abs(2*sg.H_system/OMEGA0 - 2*5*.5/(OMEGA0*1))<1e-14
def test_gfm_common_base_scaling():
    g=GridFormingInverter("GFM",Hv=2.5,Dv=8,omega0=OMEGA0,power_controller=DroopController(.2,.05,OMEGA0),voltage_controller=VoltageDroopController(1.03,0,.12),X_filter=.15,Imax=3,Sr=.5,S_base=1)
    assert abs(g.Hv_system-1.25)<1e-14 and abs(g.X_filter-.30)<1e-14 and abs(g.Dv-4)<1e-14 and abs(g.Imax-1.5)<1e-14
def test_gfl_rating_scales_current_capability():
    g=GridFollowingInverter("GFL",.2,.05,Sr=.5,S_base=1,Imax=2,Kp_pll=30,Ki_pll=200); assert abs(g.Imax-1)<1e-14
