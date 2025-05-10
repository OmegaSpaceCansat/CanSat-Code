import numpy as np
from scipy.ndimage import zoom

def process_temperature_string(temp_string):
    values = [float(x) if '.' in x else int(x) for x in temp_string.split(',')]

    temp_matrix = np.array(values[-64:]).reshape(8, 8)

    return temp_matrix


datos = "2500,101000,23.5,0.02,-0.04,0.06, 2, 1, 4, 5, -1,2,3,4,5,6,7,8,9,10,11,12,-1,-2,-3,-4,-5,0,1,2,3,4,5,-1,1,-2,6,7,8,-3,-4,5,6,-2,4,0,1,8,-5,3,0,4,-4,-1,2,3,7,6,1,-5,9,10,-3,2,-1,0,5,6"

temp_matrix = process_temperature_string(datos)

scaled_matrix = zoom(temp_matrix, (2, 2), order=3)

import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.imshow(scaled_matrix, cmap='jet', interpolation='nearest')
ax.set_xticks([])
ax.set_yticks([])
plt.show()
