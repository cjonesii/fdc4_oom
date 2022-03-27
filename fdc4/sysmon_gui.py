#
# sysmon_gui.py - a GUI for FDC4 SYSMON
# Copyright 2022 Adnacom Inc
#
from tkinter import *
from turtle import width
from oom import *

def draw_reading(master, stype, label, actual):
    parms = {'TEMP': ("C", "%.2f"),
             'VCC': ("V", "%.2f")
             }
    unit, formstr = parms[stype]
    if stype == 'TEMP':
        ctop = master.tmeastop
        master.tmeastop += 20
    elif stype == 'VCC':
        ctop = master.vmeastop
        master.vmeastop += 20
    cright = master.right
    master.create_text(cright, ctop, anchor=W, font=("Calibri", 10), text=label)
    master.create_text(cright+180, ctop, font=("Calibri", 10), text=formstr % actual)
    master.create_text(cright+205, ctop, font=("Calibri", 10), text=unit)


def draw_section( master, stype ):
    parms = {'TEMP': ("Temperature Readings"),
             'VCC': ("Voltage Readings")
             }
    label = parms[stype]
    # adjust top spacing due to change in font size
    ctop = master.top + 30
    # Label this container
    master.create_text(master.right, ctop, anchor=W, font=("Calibri", 10, "bold"), text=label)
    # prepare offset of next section
    master.top += 250
    master.vmeastop = 54
    master.tmeastop = 304

def draw_container( master, header, SYSMONclass ):
    # what will be created
    cwidth = 230
    c = Canvas( master, width=cwidth, height=375, bd=0, highlightbackground="grey" )
    # actual creation
    master.create_window( SYSMONclass.leftedge, 0, window=c, anchor=NW ) # create the space
    # adjust the starting offset for the next container
    SYSMONclass.leftedge += cwidth

    c.top = 4
    c.right = 5
    # Label this container
    c.create_text( c.right, c.top, anchor=NW, font=("Calibri", 14, "bold"), text=header )

    return c

class SYSMON:
    def __init__(self, master):
        # Deletes previous measurement window
        for widget in master.winfo_children():
            widget.destroy()

        master.title("SYSMON Readings")
        frame = Frame(master, bd=2, relief=SUNKEN)
        frame.pack()

        cwidth = 690
        c = Canvas(frame, bd=0, width=cwidth, height=380,
        scrollregion=(0,0,1540,300))
        c.pack_propagate(0)
        c.pack(side=TOP, expand=True, fill=BOTH)

        # the Finisar logo at the bottom of the screen
        logo = PhotoImage(file="adnacom_logo.png")
        self.label = Label(frame, image=logo)
        self.label.image = logo  # kludge required by Tkinter
        self.label.pack(side=BOTTOM)

        self.leftedge = 0

        # Get the SYSMON readings
        # AMS Control
        #vcc_pll0 = sysmon_get_keyvalue('VCC_PSPLL')
        vcc_pll0 = 0
        # vcc_psbatt = sysmon_get_keyvalue('VCC_PSBATT')
        vcc_psbatt = 0
        # vccint = sysmon_get_keyvalue('VCCINT')
        vccint = 0
        # vccbram = sysmon_get_keyvalue('VCCBRAM')
        vccbram = 0
        # vccaux = sysmon_get_keyvalue('VCCAUX')
        vccaux = 0
        # vcc_osddrpll = sysmon_get_keyvalue('VCC_PSDDR_PLL')
        vcc_osddrpll = 0
        # vccpsintfpddr = sysmon_get_keyvalue('VCC_PSINTFP_DDR')
        vccpsintfpddr = 0

        # PS SYSMON
        #in_temp0_ps_temp_raw = sysmon_get_keyvalue('TEMP_PS_LPD')
        in_temp0_ps_temp_raw = 0
        #in_temp1_remote_temp_raw = sysmon_get_keyvalue('TEMP_PS_FPD')
        in_temp1_remote_temp_raw = 0
        # vccpsintlp = sysmon_get_keyvalue('VCC_PS_LPD')
        vccpsintlp = 0
        # vccpsintfp = sysmon_get_keyvalue('VCC_PL_FPD')
        vccpsintfp = 0
        # vccpsaux_3 = sysmon_get_keyvalue('VCC_PS_AUX_1')
        vccpsaux_3 = 0
        # vccpsddr = sysmon_get_keyvalue('DDR_IO_VCC')
        vccpsddr = 0
        # vccpsio3 = sysmon_get_keyvalue('PS_IO_BANK_503_VCC')
        vccpsio3 = 0
        # vccpsio0 = sysmon_get_keyvalue('PS_IO_BANK_500_VCC')
        vccpsio0 = 0
        # vccpsio1 = sysmon_get_keyvalue('VCCO_PSIO1')
        vccpsio1 = 0
        # vccpsio2 = sysmon_get_keyvalue('VCCO_PSIO2')
        vccpsio2 = 0
        # psmgtravcc = sysmon_get_keyvalue('VPS_MGTRAVCC')
        psmgtravcc = 0
        # psmgtravtt = sysmon_get_keyvalue('VPS_MGTRAVTT')
        psmgtravtt = 0

        # PL SYSMON
        #in_temp2_pl_temp_raw = sysmon_get_keyvalue('TEMP_PL')
        in_temp2_pl_temp_raw = 0
        # psvccams = sysmon_get_keyvalue('VCC_PS_ADC')
        psvccams = 0
        # plvccint = sysmon_get_keyvalue('PL_VCCINT')
        plvccint = 0
        # plvccaux = sysmon_get_keyvalue('PL_VCCAUX')
        plvccaux = 0
        # vccvrefp = sysmon_get_keyvalue('PL_VREF_P')
        vccvrefp = 0
        # vccvrefn = sysmon_get_keyvalue('PL_VREF_N')
        vccvrefn = 0
        # plvccbram = sysmon_get_keyvalue('PL_VCCBRAM')
        plvccbram = 0
        # vccplintlp = sysmon_get_keyvalue('VCC_PSINTLP')
        vccplintlp = 0
        # vccplintfp = sysmon_get_keyvalue('VCC_PSINTFP')
        vccplintfp = 0
        # vccpsaux_6 = sysmon_get_keyvalue('VCC_PL_AUX_2')
        vccpsaux_6 = 0
        # plvccams = sysmon_get_keyvalue('VCC_PL_ADC')
        plvccams = 0

        # Format the result
        ams = draw_container( c, "AMS Control", self )
        ams_v = draw_section( ams, "VCC" )
        ps = draw_container( c, "PS SYSMON", self )
        ps_v = draw_section( ps, "VCC" )
        ps_t = draw_section( ps, "TEMP" )
        pl = draw_container( c, "PL SYSMON", self )
        pl_v = draw_section( pl, "VCC" )
        pl_t = draw_section( pl, "TEMP" )

        # Display the SYSMON reading
        draw_reading( ams, "VCC", "VCC_PSPLL", vcc_pll0 )
        draw_reading( ams, "VCC", "VCC_PSBATT", vcc_psbatt )
        draw_reading( ams, "VCC", "VCCINT", vccint )
        draw_reading( ams, "VCC", "VCCBRAM", vccbram )
        draw_reading( ams, "VCC", "VCCAUX", vccaux )
        draw_reading( ams, "VCC", "VCC_PSDDR_PLL", vcc_osddrpll )
        draw_reading( ams, "VCC", "VCC_PSINTFP_DDR", vccpsintfpddr )

        draw_reading( ps, "TEMP", "TEMP_PL", in_temp2_pl_temp_raw )
        draw_reading( ps, "TEMP", "TEMP_PS_FPD", in_temp1_remote_temp_raw )
        draw_reading( ps, "VCC", "VCC_PS_LPD", vccpsintlp )
        draw_reading( ps, "VCC", "VCC_PL_FPD", vccpsintfp )
        draw_reading( ps, "VCC", "VCC_PS_AUX_1", vccpsaux_3 )
        draw_reading( ps, "VCC", "DDR_IO_VCC", vccpsddr )
        draw_reading( ps, "VCC", "PS_IO_BANK_503_VCC", vccpsio3 )
        draw_reading( ps, "VCC", "PS_IO_BANK_500_VCC", vccpsio0 )
        draw_reading( ps, "VCC", "VCCO_PSIO1", vccpsio1 )
        draw_reading( ps, "VCC", "VCCO_PSIO2", vccpsio2 )
        draw_reading( ps, "VCC", "VPS_MGTRAVCC", psmgtravcc )
        draw_reading( ps, "VCC", "VPS_MGTRAVTT", psmgtravtt )

        draw_reading( pl, "TEMP", "TEMP_PS_LPD", in_temp0_ps_temp_raw )
        draw_reading( pl, "VCC", "VCC_PS_ADC", psvccams )
        draw_reading( pl, "VCC", "PL_VCCINT", plvccint )
        draw_reading( pl, "VCC", "PL_VCCAUX", plvccaux )
        draw_reading( pl, "VCC", "PL_VREF_P", vccvrefp )
        draw_reading( pl, "VCC", "PL_VREF_N", vccvrefn )
        draw_reading( pl, "VCC", "PL_VCCBRAM", plvccbram )
        draw_reading( pl, "VCC", "VCC_PSINTLP", vccplintlp )
        draw_reading( pl, "VCC", "VCC_PSINTFP", vccplintfp )
        draw_reading( pl, "VCC", "VCC_PL_AUX_2", vccpsaux_6 )
        draw_reading( pl, "VCC", "VCC_PL_ADC", plvccams )

        # Create new window after 3s
        master.after( 5000, SYSMON, master )

if __name__ == "__main__":
    root = Tk()
    SYSMON( root )
    root.mainloop()