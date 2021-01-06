"""Displays real-time sonic boom data for the sim."""

import sys

import pyqtgraph as pg
import numpy as np
import math as m

from pyqtgraph.Qt import QtCore, QtGui

class BoomDataGUI:
    """A sonic boom data visualization GUI"""

    def __init__(self):

        # Set pyqtgraph options
        pg.setConfigOption('background', 'k')

        # Initialize application
        self._app = QtGui.QApplication([])

        # Initialize window
        self._main_widget = pg.LayoutWidget()
        self._main_widget.setWindowTitle('BoomSim Data')

        # Initialize data
        self._initialize_near_field_data()
        self._initialize_atmos_data()
        self._initialize_flight_data()
        self._initialize_gsig_data()

        # Initialize sub layouts and widgets
        self._geom_widget = pg.PlotWidget(title='Geometry Alteration')
        self._atmos_widget = pg.PlotWidget(title='Atmospheric Profile')
        self._flight_data_widget = pg.GraphicsLayoutWidget(title='Flight Data')
        self._pldb_widget = pg.PlotWidget(title='Boom Loudness')
        self._gsig_widget = pg.PlotWidget(title='Ground Pressure Signature')

        # Arrange window

        # Top row
        self._near_field_widget = self._main_widget.addLayout(row=1, col=1, rowspan=1, colspan=1)
        self._main_widget.addWidget(self._geom_widget, row=1, col=2, rowspan=1, colspan=2)

        # Middle row
        self._main_widget.addWidget(self._atmos_widget, row=2, col=1, rowspan=2, colspan=1)
        self._main_widget.addWidget(self._flight_data_widget, row=2, col=2, rowspan=2, colspan=2)

        # Bottom row
        self._main_widget.addWidget(self._gsig_widget, row=4, col=1, rowspan=1, colspan=1)
        self._main_widget.addWidget(self._pldb_widget, row=4, col=2, rowspan=1, colspan=1)
        self._boom_carpet_widget = self._main_widget.addLayout(row=4, col=3, rowspan=1, colspan=1)

        # Set up individual widgets
        self._initialize_near_field_graphic()
        self._initialize_geom_plot()
        self._initialize_atmos_plot()
        self._initialize_flight_plot()
        self._initialize_gsig_plot()
        self._initialize_pldb_plot()
        self._initialize_boom_carpet()


    def start(self):
        """Starts the GUI."""

        # Set timer
        self._timer = QtCore.QTimer()
        self._timer.timeout.connect(self._update_graphics)
        self._timer.start(50)

        # Show window
        self._main_widget.show()

        # Run loop
        if sys.flags.interactive != 1 or not hasattr(QtCore, 'PYQT_VERSION'):
            self._app.exec_()


    def _initialize_near_field_data(self):
        # Reads in data for the near-field pressure signature

        # Read in file
        with open("data/nf_undertrack.txt", 'r') as input_handle:

            # Get lines
            lines = input_handle.readlines()
            N = len(lines)
            self._nf_press_data = np.zeros((N, 2))
            for i in range(N):
                split_line = lines[i].split()
                self._nf_press_data[i,0] = float(split_line[0])
                self._nf_press_data[i,1] = float(split_line[1])


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


    def _initialize_gsig_data(self):
        # Read in ground signature data

        # Read in file
        with open("data/41N_74W_25D_adapt07_EALINENEW4_gsig", 'r') as input_handle:

            # Get lines
            lines = input_handle.readlines()
            N = len(lines)
            self._gsig_data = np.zeros((N, 2))
            for i in range(N):
                split_line = lines[i].split()
                self._gsig_data[i,0] = float(split_line[0])
                self._gsig_data[i,1] = float(split_line[1])


    def _initialize_flight_data(self):

        # Initialize flight data
        self._flight_data = np.zeros((5, 300))


    def _initialize_near_field_graphic(self):
        # Set up near-field pressure graphic

        # Add aircraft image
        self._mach_line_image = QtGui.QPixmap('image/25D_mach_lines_solid.png')
        self._mach_image_label = self._near_field_widget.addLabel(row=1, col=1)
        self._mach_line_image = self._mach_line_image.scaled(QtCore.QSize(320, 240), QtCore.Qt.KeepAspectRatio)
        self._mach_image_label.setPixmap(self._mach_line_image)
        self._mach_image_label.show()

        # Create plot widget
        self._P_nf_plot = pg.PlotWidget(title='Near-Field Pressure Signature')
        self._near_field_widget.addWidget(self._P_nf_plot, row=2, col=1, colspan=2)

        # Add pressure plot
        self._P_nf_plot.addLegend()
        self._P_nf_plot.setLabel('left', 'Pressure', units="Pa")
        self._P_nf_plot.setLabel('bottom', 'Time', units="s")
        self._P_nf_baseline_curve = self._P_nf_plot.plot(self._nf_press_data[:,0], self._nf_press_data[:,1], name='Baseline', pen="#0000FF")
        self._P_nf_optimum_curve = self._P_nf_plot.plot(self._nf_press_data[:,0], 0.8*self._nf_press_data[:,1], name='Optimum', pen="#7777FF")

        # Add slider
        self._P_nf_silder = QtGui.QSlider(QtCore.Qt.Horizontal)
        self._P_nf_silder.setMinimum(-90)
        self._P_nf_silder.setMaximum(90)
        self._near_field_widget.addWidget(self._P_nf_silder, row=1, col=2)
        
        # Set up slider connection
        self._P_nf_angle = 0.0
        self._P_nf_silder.valueChanged.connect(self._update_near_field_angle)


    def _update_near_field_angle(self):
        # Updates the near-field pressure signature based on the angle of the slider

        # Store value
        self._P_nf_angle = float(self._P_nf_silder.value())

        # Update graphs
        self._update_near_field_graph()
        self._update_gsig_graph()


    def _initialize_geom_plot(self):
        # Sets up the plot to show the altered geometry

        # Get coordinates
        x = np.linspace(0, 100, 1000)
        y_u = 0.000001*x*x*(x-100.0)*(x-100.0)
        y_l = 0.0000005*(x-100.0)*x*x*x
        y_l_opt = y_l-np.exp(-0.1*(x-20.0)**2)

        # Plot
        self._geom_widget.addLegend()
        self._geom_widget.plot(x, y_u, pen='#0000FF', name='Baseline')
        self._geom_widget.plot(x, y_l, pen='#0000FF')
        self._geom_widget.plot(x, y_l_opt, pen='#7777FF', name='Optimum')

        # Set range
        self._geom_widget.setRange(yRange=[-15, 15])


    def _initialize_atmos_plot(self):

        # Initialize plot
        self._atmos_widget.setLabel('left', 'Altitude [m]')
        self._atmos_widget.addLegend()
        self._atmos_widget.setRange(xRange=[-150, 150])

        # Plot data
        self._T_curve = self._atmos_widget.plot(self._T, self._h, pen=(255, 0, 0), name='T [F]')
        self._u_curve = self._atmos_widget.plot(self._u, self._h, pen=(0, 255, 0), name='Wind x-Velocity [m/s]')
        self._v_curve = self._atmos_widget.plot(self._v, self._h, pen=(155, 255, 55), name='Wind y-Velocity [m/s]')
        self._RH_curve = self._atmos_widget.plot(self._RH, self._h, pen=(0, 0, 255), name='Relative Humidity [%]')


    def _initialize_flight_plot(self):

        # Initialize data curve origin (incrementing this leads to the scrolling effect)
        self._ptr = 0

        # Create altitude plot
        h_color = "#0000FF"
        self._h_axis = pg.AxisItem('left')
        self._h_axis.setLabel('Altitude', units='m', color=h_color)
        self._h_view = pg.ViewBox()
        self._h_curve = pg.PlotCurveItem(self._flight_data[2], pen=h_color)

        # Create Mach plot
        M_color = "#00FF00"
        self._M_axis = pg.AxisItem('left')
        self._M_axis.setLabel('Mach Number', color=M_color)
        self._M_view = pg.ViewBox()
        self._M_curve = pg.PlotCurveItem(self._flight_data[1], pen=M_color)

        # Create angle of attack plot
        a_color = "#FFFF00"
        self._a_axis = pg.AxisItem('left')
        self._a_axis.setLabel('Angle of Attack', units='deg', color=a_color)
        self._a_view = pg.ViewBox()
        self._a_curve = pg.PlotCurveItem(self._flight_data[0], pen=a_color)

        # Create baseline PLdB plot
        pldb_base_color = "#FF0000"
        self._pldb_base_axis = pg.AxisItem('left')
        self._pldb_base_axis.setLabel('PL (baseline)', units='dB', color=pldb_base_color)
        self._pldb_base_view = pg.ViewBox()
        self._pldb_base_curve = pg.PlotCurveItem(self._flight_data[3], pen=pldb_base_color)

        # Create optimum PLdB plot
        pldb_opt_color = "#FF5555"
        self._pldb_opt_axis = pg.AxisItem('left')
        self._pldb_opt_axis.setLabel('PL (optimum)', units='dB', color=pldb_opt_color)
        self._pldb_opt_view = pg.ViewBox()
        self._pldb_opt_curve = pg.PlotCurveItem(self._flight_data[4], pen=pldb_opt_color)

        # Create time axis
        self._t_axis = pg.AxisItem('bottom')
        self._t_axis.setLabel('Time', units='s')

        # Create title
        title = pg.LabelItem('Flight Data')
        self._flight_data_widget.addItem(title, row=1, col=1, colspan=6)

        # Add axes to layout (# of col determines axis order; h needs to be last)
        self._flight_data_widget.addItem(self._h_view, row=2, col=6)
        self._flight_data_widget.addItem(self._t_axis, row=3, col=6)
        self._flight_data_widget.addItem(self._h_axis, row=2, col=5)
        self._flight_data_widget.addItem(self._M_axis, row=2, col=4)
        self._flight_data_widget.addItem(self._a_axis, row=2, col=3)
        self._flight_data_widget.addItem(self._pldb_base_axis, row=2, col=2)
        self._flight_data_widget.addItem(self._pldb_opt_axis, row=2, col=1)

        # Add viewboxes to layout
        self._flight_data_widget.scene().addItem(self._M_view)
        self._flight_data_widget.scene().addItem(self._a_view)
        self._flight_data_widget.scene().addItem(self._pldb_base_view)
        self._flight_data_widget.scene().addItem(self._pldb_opt_view)

        # Link axes with viewboxes
        self._t_axis.linkToView(self._h_view)
        self._h_axis.linkToView(self._h_view)
        self._M_axis.linkToView(self._M_view)
        self._a_axis.linkToView(self._a_view)
        self._pldb_base_axis.linkToView(self._pldb_base_view)
        self._pldb_opt_axis.linkToView(self._pldb_opt_view)

        # Link x axis of viewboxes to base plot
        self._M_view.setXLink(self._h_view)
        self._a_view.setXLink(self._h_view)
        self._pldb_base_view.setXLink(self._h_view)
        self._pldb_opt_view.setXLink(self._h_view)

        # Link PL dB y scale
        self._pldb_opt_view.setYLink(self._pldb_base_view)

        # Add data curves to viewboxes
        self._h_view.addItem(self._h_curve)
        self._M_view.addItem(self._M_curve)
        self._a_view.addItem(self._a_curve)
        self._pldb_base_view.addItem(self._pldb_base_curve)
        self._pldb_opt_view.addItem(self._pldb_opt_curve)

        # Update views when resized
        def update_flight_data_views():
            self._M_view.setGeometry(self._h_view.sceneBoundingRect())
            self._a_view.setGeometry(self._h_view.sceneBoundingRect())
            self._pldb_base_view.setGeometry(self._h_view.sceneBoundingRect())
            self._pldb_opt_view.setGeometry(self._h_view.sceneBoundingRect())
        self._h_view.sigResized.connect(update_flight_data_views)


    def _initialize_gsig_plot(self):

        # Initialize plot
        self._gsig_widget.setLabel('left', 'Pressure', units="Pa")
        self._gsig_widget.setLabel('bottom', 'Time', units="s")
        self._gsig_widget.addLegend()

        # Plot data
        self._gsig_base_curve = self._gsig_widget.plot(self._gsig_data[:,0], self._gsig_data[:,1], pen="#0000FF", name='Baseline')
        self._gsig_opt_curve = self._gsig_widget.plot(self._gsig_data[:,0], 0.8*self._gsig_data[:,1], pen="#7777FF", name='Optimum')


    def _initialize_pldb_plot(self):

        # Set up plot item
        self._pldb_plot_item = pg.BarGraphItem(x=[5, 10], height=[83.0, 78.0], width=3, brush='#0000FF', pen='#0000FF')

        # Add to plot
        self._pldb_widget.addItem(self._pldb_plot_item)

        # Format
        self._pldb_widget.setLabel('left', 'Perceived Loudness', units='dB')


    def _initialize_boom_carpet(self):
        # Sets up the boom carpet widget

        # Add title
        self._boom_carpet_widget.addLabel("Boom Carpet", row=1, col=1, colspan=2)

        # Create radio buttons
        self._rb_base = QtGui.QRadioButton("Baseline")
        self._rb_base.setChecked(True)
        self._rb_opt = QtGui.QRadioButton("Optimum")
        self._rb_del = QtGui.QRadioButton("Delta")

        # Add to layout
        self._boom_carpet_widget.addWidget(self._rb_base, row=2, col=2)
        self._boom_carpet_widget.addWidget(self._rb_opt, row=3, col=2)
        self._boom_carpet_widget.addWidget(self._rb_del, row=4, col=2)

        # Create image
        self._boom_carpet_image = QtGui.QPixmap('image/boom_carpet.jpeg')
        self._carpet_image_label = self._boom_carpet_widget.addLabel(row=2, col=1, rowspan=3)
        self._boom_carpet_image = self._boom_carpet_image.scaled(QtCore.QSize(300, 300), QtCore.Qt.KeepAspectRatio)
        self._carpet_image_label.setPixmap(self._boom_carpet_image)
        self._carpet_image_label.show()


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

        self._h += np.random.normal(size=len(self._h), scale=0.01)
        self._T += np.random.normal(size=len(self._T), scale=0.01)
        self._u += np.random.normal(size=len(self._u), scale=0.01)
        self._v += np.random.normal(size=len(self._v), scale=0.01)
        self._RH += np.random.normal(size=len(self._RH), scale=0.01)


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
            self._flight_data[4,-1] = 80.0*M**0.4+np.random.normal(size=1, scale=0.5)
        else:
            self._flight_data[3,-1] = 0.1
            self._flight_data[4,-1] = 0.1


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

        # Altitude
        self._h_curve.setData(self._flight_data[2])
        self._h_curve.setPos(self._ptr, 0)
        self._h_view.setRange(yRange=(0, np.max(self._flight_data[2])))

        # Mach number
        self._M_curve.setData(self._flight_data[1])
        self._M_curve.setPos(self._ptr, 0)
        self._M_view.setRange(yRange=(0, 1.5*np.max(self._flight_data[1])))

        # Angle of attack
        self._a_curve.setData(self._flight_data[0])
        self._a_curve.setPos(self._ptr, 0)
        self._a_view.setRange(yRange=(0, 1.25*np.max(self._flight_data[0])))

        # Baseline PL dB
        self._pldb_base_curve.setData(self._flight_data[3])
        self._pldb_base_curve.setPos(self._ptr, 0)
        self._pldb_base_view.setRange(yRange=(0, np.max(self._flight_data[3])))

        # Optimum PL dB
        self._pldb_opt_curve.setData(self._flight_data[4])
        self._pldb_opt_curve.setPos(self._ptr, 0)


    def _update_near_field_graph(self):
        # Updates the near-field graph

        self._P_nf_baseline_curve.setData(self._nf_press_data[:,0], self._nf_press_data[:,1]*m.cos(m.radians(self._P_nf_angle))+self._nf_press_data[:,1]**2*abs(m.sin(m.radians(self._P_nf_angle))))
        self._P_nf_optimum_curve.setData(self._nf_press_data[:,0], 0.8*self._nf_press_data[:,1]*m.cos(m.radians(self._P_nf_angle))+0.8*self._nf_press_data[:,1]**2*abs(m.sin(m.radians(self._P_nf_angle))))


    def _update_gsig_graph(self):
        # Updates the ground signature plot

        self._gsig_base_curve.setData(self._gsig_data[:,0], self._gsig_data[:,1]*m.cos(m.radians(self._P_nf_angle)))
        self._gsig_opt_curve.setData(self._gsig_data[:,0], 0.8*self._gsig_data[:,1]*m.cos(m.radians(self._P_nf_angle))**2)


if __name__=="__main__":

    # Initialize GUI and run
    gui = BoomDataGUI()
    gui.start()