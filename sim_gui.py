"""Displays real-time sonic boom data for the sim."""

import sys

import pyqtgraph as pg
import numpy as np

from pyqtgraph.Qt import QtCore, QtGui

class BoomDataGUI:
    """A sonic boom data visualization GUI"""

    def __init__(self):

        # Initialize window
        self._win = pg.GraphicsLayoutWidget(show=True, border=0.5)
        self._win.setWindowTitle('BoomSim Data')

        # Set up window layout
        self._main_layout = QtGui.QGridLayout()
        self._win.setLayout(self._main_layout)

        # Initialize data
        self._initialize_atmos_data()
        self._initialize_flight_data()

        # Set up plots
        self._arrange_plots()
        self._initialize_atmos_plot()
        self._initialize_flight_plot()


    def _initialize_atmos_data(self):

        # Read in file
        with open("data/seattle_T_H_W_distributions.input", 'r') as input_handle:

            # Initialize storage
            curr_val = ""
            self._h = []
            self._T = []
            self._u = []
            self._v = []
            self._RH = []

            # Loop through lines
            for line in input_handle.readlines():

                # Split up line
                split_line = line.split()

                # Skip empty lines
                if len(line)==0 or len(split_line)==0:
                    continue

                # Check for new value
                try:
                    float(split_line[0])
                except:
                    curr_val = split_line[1]
                    continue

                # Store
                if curr_val == "Temperature":
                    self._h.append(float(split_line[0]))
                    self._T.append(float(split_line[1]))
                elif curr_val == "X-Wind":
                    self._u.append(float(split_line[1]))
                elif curr_val == "Y-Wind":
                    self._v.append(float(split_line[1]))
                elif curr_val == "Relative":
                    self._RH.append(float(split_line[1]))

        # Convert data to numpy arrays
        self._h = np.array(self._h)
        self._T = np.array(self._T)
        self._u = np.array(self._u)
        self._v = np.array(self._v)
        self._RH = np.array(self._RH)


    def _initialize_flight_data(self):

        # Initialize flight data
        self._flight_data = np.zeros((5, 300))


    def _arrange_plots(self):

        # Top row
        self._near_field_view = self._win.addViewBox(row=1, col=1, rowspan=1, colspan=1)
        self._geom_view = self._win.addViewBox(row=1, col=2, rowspan=1, colspan=2)

        # Middle row
        self._atmos_plot = self._win.addPlot(title="Atmospheric Profile", row=2, col=1, rowspan=2, colspan=1)
        self._flight_data_layout = self._win.addLayout(row=2, col=2, rowspan=2, colspan=2)

        # Bottom row
        self._boom_view = self._win.addViewBox(row=4, col=1, rowspan=1, colspan=1)
        self._pldb_view = self._win.addViewBox(row=4, col=2, rowspan=1, colspan=1)
        self._boom_carpet_view = self._win.addViewBox(row=4, col=3, rowspan=1, colspan=1)


    def _initialize_atmos_plot(self):

        # Initialize plot
        self._atmos_plot.setLabel('left', 'Altitude [m]')
        self._atmos_plot.addLegend()
        self._atmos_plot.setRange(xRange=[-150, 150])

        # Plot data
        self._T_curve = self._atmos_plot.plot(self._T, self._h, pen=(255, 0, 0), name='T')
        self._u_curve = self._atmos_plot.plot(self._u, self._h, pen=(0, 255, 0), name='Wind x-Velocity')
        self._v_curve = self._atmos_plot.plot(self._v, self._h, pen=(155, 255, 55), name='Wind y-Velocity')
        self._RH_curve = self._atmos_plot.plot(self._RH, self._h, pen=(0, 0, 255), name='Relative Humidity')


    def _initialize_flight_plot(self):

        # Initialize scrolling parameter
        self._ptr = 0

        # Create Mach axis
        self._M_axis = pg.AxisItem('left')
        self._M_axis.setLabel('Mach')
        self._M_view = pg.ViewBox()
        self._M_curve = pg.PlotCurveItem(self._flight_data[1], pen=(0, 255, 0), name='Mach Number')
        self._flight_data_layout.addItem(self._M_axis, col=3)

        # Create base plot (altitude)
        self._h_plot = pg.PlotItem()
        self._h_view = self._h_plot.vb
        self._flight_data_layout.addItem(self._h_plot, col=4)
        self._h_plot.setLabel('bottom', 'Time', units='s')
        self._h_plot.setLabel('left', 'Altitude', units='m')
        self._h_plot.addLegend()
        self._h_curve = pg.PlotCurveItem(self._flight_data[2], pen=(0, 0, 255), name='Altitude')

        # Add viewboxes to layout
        self._flight_data_layout.scene().addItem(self._M_view)

        # Link axis with viewboxes
        self._M_axis.linkToView(self._M_view)

        # Link viewboxes
        self._M_view.setXLink(self._h_view)

        # Add data plots to viewboxes
        self._h_view.addItem(self._h_curve)
        self._M_view.addItem(self._M_curve)

        # Update views when resized
        def update_flight_data_views():
            self._M_view.setGeometry(self._h_view.sceneBoundingRect())

        self._h_view.sigResized.connect(update_flight_data_views)

        # Autorange at start
        self._M_view.enableAutoRange(axis=pg.ViewBox.XYAxes, enable=True)

        ## Initialize flight data curves
        #self._a_curve = self._h_plot.plot(self._flight_data[0], pen=(255, 255, 0), name='Angle of Attack')
        #self._pldb_base_curve = self._h_plot.plot(self._flight_data[3], pen=(255, 0, 0), name='PL dB Baseline')
        #self._pldb_opt_curve = self._h_plot.plot(self._flight_data[4], pen=(255, 128, 128), name='PL dB Modified')


    def start(self):
        """Starts the GUI."""

        # Set timer
        self._timer = QtCore.QTimer()
        self._timer.timeout.connect(self._update_graphics)
        self._timer.start(50)

        # Run loop
        if sys.flags.interactive != 1 or not hasattr(QtCore, 'PYQT_VERSION'):
            app = QtGui.QApplication([])
            app.exec_()


    def _update_graphics(self):
        # Updates all graphics

        # Update data
        self._update_atmos_data()
        self._update_flight_data()

        # Update plots
        self._update_atmos_plot()
        self._update_flight_plot()


    def _update_atmos_data(self):
        # Updates the data shown in the atmospheric profile plot

        self._h += np.random.normal(size=len(self._h), scale=0.1)
        self._T += np.random.normal(size=len(self._T), scale=0.1)
        self._u += np.random.normal(size=len(self._u), scale=0.1)
        self._v += np.random.normal(size=len(self._v), scale=0.1)
        self._RH += np.random.normal(size=len(self._RH), scale=0.1)


    def _update_flight_data(self):
        # Updates the flight data

        ptr_peak = 1000

        # Cycle
        self._flight_data[:,:-1] = self._flight_data[:,1:]

        # Angle of attack
        if self._ptr < ptr_peak:
            self._flight_data[0,-1] = 6.0+np.random.normal(size=1, scale=0.1)
        else:
            self._flight_data[0,-1] = 2.3+np.random.normal(size=1, scale=0.1)

        # Mach number
        if self._ptr < ptr_peak:
            self._flight_data[1,-1] = 1.6*self._ptr/ptr_peak+np.random.normal(size=1, scale=0.01)
        else:
            self._flight_data[1,-1] = 1.6+np.random.normal(size=1, scale=0.01)

        # Altitude
        if self._ptr < ptr_peak:
            self._flight_data[2,-1] = 10000*self._ptr/ptr_peak+np.random.normal(size=1, scale=3000.0/ptr_peak)
        else:
            self._flight_data[2,-1] = 10000+np.random.normal(size=1, scale=10.0)

        # PL dB
        M = self._flight_data[1,-1]
        if M > 1.0:
            self._flight_data[3,-1] = 83.0*M**0.5+np.random.normal(size=1, scale=0.5)
            self._flight_data[4,-1] = 80.0*M**0.5+np.random.normal(size=1, scale=0.5)
        else:
            self._flight_data[3,-1] = 0.0
            self._flight_data[4,-1] = 0.0


    def _update_atmos_plot(self):
        # Updates the atmospheric profile plot

        self._T_curve.setData(self._T, self._h)
        self._u_curve.setData(self._u, self._h)
        self._v_curve.setData(self._v, self._h)
        self._RH_curve.setData(self._RH, self._h)

    
    def _update_flight_plot(self):
        # Updates the flight data plot

        # Scroll
        self._ptr += 1

        # Mach number
        self._M_curve.setData(self._flight_data[1])
        self._M_curve.setPos(self._ptr, 0)

        # Altitude
        self._h_curve.setData(self._flight_data[2])
        self._h_curve.setPos(self._ptr, 0)

        #self._a_curve.setData(self._flight_data[0])
        #self._a_curve.setPos(self._ptr, 0)
        #self._pldb_base_curve.setData(self._flight_data[3])
        #self._pldb_base_curve.setPos(self._ptr, 0)
        #self._pldb_opt_curve.setData(self._flight_data[4])
        #self._pldb_opt_curve.setPos(self._ptr, 0)


if __name__=="__main__":

    # Initialize GUI and run
    gui = BoomDataGUI()
    gui.start()