import mujoco
import mujoco.viewer
import numpy as np
import matplotlib.pyplot as plt

model = mujoco.MjModel.from_xml_path("masstendon.xml")
data = mujoco.MjData(model)
viewer = mujoco.viewer.launch(model, data)


def main(model, data):
    forcetrace = []
    postrace = []

    for _ in range(1000):
        viewer.render()
        
        if _>500:
            data.site_xpos[0]=np.array([0, 0, 0.1]) # move tendon origin up a bit
        else:
            pass
    
        mujoco.mj_step(model, data)
        forcetrace.append(data.sensordata[2])
        postrace.append(data.qpos[2])
        
    viewer.close()
    
    return forcetrace, postrace

forces, posns = np.array(main(model, data))
plt.plot(forces)
plt.figure()
plt.plot(posns)
plt.show()