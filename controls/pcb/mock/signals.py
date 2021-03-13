import numpy as np

# Fuente de datos 1
interval = 0.01
maxtime1 = 0.5
time1 = np.arange(0, maxtime1, interval)
m1 = 40
flux1 = time1 * m1

maxtime2 = 1.7
time2 = np.arange(0, maxtime2, interval)
flux2 = max(flux1) * np.e ** (-2 * time2)

maxtime3 = 0

maxTime = (maxtime1 * 2 + maxtime2 * 2 + maxtime3 * 1) * 5
flux = np.concatenate([flux1, flux2, -flux1, -flux2])
flux = np.concatenate([flux, flux, flux, flux, flux])
flux = np.concatenate([flux, flux, flux, flux, flux])
flux = flux + (np.random.rand(len(flux)) - 0.5) * 2.5
time = np.arange(0, maxTime * 5, interval)

# Fuente de datos 2
pressure1 = np.ones(len(time1) + len(time2)) * 2
pressure2 = pressure1 + 18
pressure = np.concatenate([pressure2, pressure1])
pressure = np.concatenate([pressure, pressure, pressure, pressure, pressure])
pressure = np.concatenate([pressure, pressure, pressure, pressure, pressure])
pressure = pressure + (np.random.rand(len(pressure)) - 0.5) * 0.75
