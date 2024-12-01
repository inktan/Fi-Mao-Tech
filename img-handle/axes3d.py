import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import matplotlib.pyplot as plt

img = Image.open(r'c:\Users\mslne\Desktop\qwe.png')

original_width, original_height = img.size

# new_width = original_width // 10
# new_height = original_height // 10

# img = img.resize((new_width, new_height))

img_array = np.array(img)

img = img.convert('RGB')
data = list(img.getdata())

# data = data[:4000]
data = data
data_array = np.array(data)

normalized_data = (data_array - data_array.min(axis=0)) / (data_array.max(axis=0) - data_array.min(axis=0))

x, y, z = normalized_data[:, 0], normalized_data[:, 1], normalized_data[:, 2]

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

for i in range(len(data)):
    ax.scatter(x[i], y[i], z[i],color=np.array(data[i]) / 255.0, s=1)

ax.set_xlabel('R')
ax.set_ylabel('G')
ax.set_zlabel('B')

plt.show()