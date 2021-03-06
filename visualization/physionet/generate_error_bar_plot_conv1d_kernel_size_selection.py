import os

from main import ROOT_DIR
from visualization.error_bar_plot_helper import plot_error_bar

x_tick_labels = ["3, 3, 3",
                 "5, 5, 5",
                 "10, 10, 10",
                 "20, 20, 20",
                 "40, 40, 40",
                 "80, 80, 80",
                 "20, 40, 80",
                 "80, 40, 20",
                 "160, 160, 160",
                 "40, 80, 160",
                 "160, 80, 40"]

averages = [0.8279393970966339,
            0.8248888909816742,
            0.830767673254013,
            0.8285252451896667,
            0.8284646451473237,
            0.8240606009960174,
            0.8263232350349426,
            0.8280000030994416,
            0.8259797930717468,
            0.8264646470546723,
            0.8235959589481354]
standard_deviations = [0.03954583526706644,
                       0.032140370226530816,
                       0.03555372341872865,
                       0.02874170928497593,
                       0.03787254822372284,
                       0.03690334115689723,
                       0.031214180483460433,
                       0.03448967185976378,
                       0.03582919921046598,
                       0.03841508929736076,
                       0.03525687402023222]

figure_filepath = os.path.join(ROOT_DIR, "results", "physionet", "results-conv1d-kernel-size-selection.png")
plot_error_bar(x_tick_labels, averages, standard_deviations, figure_filepath,
               x_label="Kernel 1º camada, Kernel 2º camada, Kernel 3º camada",
               x_ticks_rotation=45, fig_size=(12, 8))
