import matplotlib.pyplot as plt
import dcmri as dc
#
# Use `fake_tissue` to generate synthetic test data from experimentally-derived concentrations:
#
time, aif, roi, gt = dc.fake_tissue()
xdata, ydata = (time,time), (aif,roi)
#
# Build an aorta-liver model and parameters to match the conditions of the fake tissue data:
#
model = dc.AortaLiver(
    dt = 0.5,
    tmax = 180,
    weight = 70,
    agent = 'gadodiamide',
    dose = 0.2,
    rate = 3,
    field_strength = 3.0,
    t0 = 10,
    TR = 0.005,
    FA = 20,
)
#
# Train the model on the data:
#
model.train(xdata, ydata, xtol=1e-3)
#
# Plot the reconstructed signals and concentrations and compare against the experimentally derived data:
#
model.plot(xdata, ydata)
#
# We can also have a look at the model parameters after training:
#
model.print_params(round_to=3)
# Expected:
## -----------------------------------------
## Free parameters with their errors (stdev)
## -----------------------------------------
## Bolus arrival time (BAT): 17.127 (2.838) sec
## Cardiac output (CO): 211.047 (13.49) mL/sec
## Heart-lung mean transit time (Thl): 12.503 (3.527) sec
## Heart-lung transit time dispersion (Dhl): 0.465 (0.063)
## Organs mean transit time (To): 28.413 (10.294) sec
## Extraction fraction (Eb): 0.01 (0.623)
## Liver extracellular mean transit time (Tel): 2.915 (0.588) sec
## Liver extracellular dispersion (De): 1.0 (0.19)
## Liver extracellular volume fraction (ve): 0.176 (0.015) mL/mL
## Hepatocellular uptake rate (khe): 0.005 (0.001) mL/sec/mL
## Hepatocellular transit time (Th): 600.0 (747.22) sec
## Organs extraction fraction (Eo): 0.261 (0.324)
## Organs extracellular mean transit time (Teb): 81.765 (329.097) sec
## ------------------
## Derived parameters
## ------------------
## Blood precontrast T1 (T10b): 1.629 sec
## Mean circulation time (Tc): 40.916 sec
## Liver precontrast T1 (T10l): 0.752 sec
## Biliary excretion rate (kbh): 0.001 mL/sec/mL
## Hepatocellular tissue uptake rate (Khe): 0.026 mL/sec/mL
## Biliary tissue excretion rate (Kbh): 0.002 mL/sec/mL
