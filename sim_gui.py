"""Displays real-time sonic boom data for the sim."""

import sys

import pyqtgraph as pg
import numpy as np

from pyqtgraph.Qt import QtCore, QtGui

class BoomDataGUI:
    """A sonic boom data visualization GUI"""

    def __init__(self):

        # Initialize window
        self._win = pg.GraphicsLayoutWidget(show=True)
        self._win.setWindowTitle('BoomSim Data')

        # Initialize flight data
        self._data = np.zeros((4, 300))

        # Initialize flight data plot
        self._plot = self._win.addPlot(title="Flight Data")
        self._ptr = 0
        self._plot.setLabel('bottom', 'Time', units='s')
        self._plot.setLabel('left', 'Value')

        # Initialize flight data curves
        self._a_curve = self._plot.plot(self._data[0], pen=(255, 0, 0), name='AoA')
        self._M_curve = self._plot.plot(self._data[1], pen=(0, 255, 0), name='Mach')
        self._h_curve = self._plot.plot(self._data[2], pen=(0, 0, 255), name='Alt')


    def start(self):
        """Starts the GUI."""

        # Set timer
        self._timer = QtCore.QTimer()
        self._timer.timeout.connect(self._update_graphics)
        self._timer.start(50)

        # Run loop
        if sys.flags.interactive != 1 or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()


    def _update_graphics(self):
        # Updates all graphics

        self._update_flight_data_plot()


    def _update_flight_data_plot(self):
        # Updates flight data plot

        # Update data
        self._data[:,:-1] = self._data[:,1:]
        self._data[:,-1] = self._data[:,-2]+np.random.normal(size=4)

        # Update curve
        self._ptr += 1
        self._a_curve.setData(self._data[0])
        self._a_curve.setPos(self._ptr, 0)
        self._M_curve.setData(self._data[1])
        self._M_curve.setPos(self._ptr, 0)
        self._h_curve.setData(self._data[2])
        self._h_curve.setPos(self._ptr, 0)


if __name__=="__main__":

    gui = BoomDataGUI()
    gui.start()