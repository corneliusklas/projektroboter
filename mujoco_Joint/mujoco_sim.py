import mujoco
import mujoco.viewer
import matplotlib.pyplot as plt
#xml = """
#<mujoco>
#  <worldbody>
#    <geom name="red_box" type="box" size=".2 .2 .2" rgba="1 0 0 1"/>
#    <geom name="green_sphere" pos=".2 .2 .2" size=".1" rgba="0 1 0 1"/>
#  </worldbody>
#</mujoco>
#"""

# Make model and data
#model = mujoco.MjModel.from_xml_string(xml)
model = mujoco.MjModel.from_xml_path("model/defaultrobot.xml") #tendonjoint.xml") 
data = mujoco.MjData(model)

print(model.ngeom)

#show the model in plt
if False:
  renderer = mujoco.Renderer(model)

  mujoco.mj_forward(model, data)
  renderer.update_scene(data)

  img=renderer.render()
  plt.imshow(img)
  plt.show()
  
import time

#show the model in mujoco viewer
m=model
d=data
with mujoco.viewer.launch_passive(m, d) as viewer:
 
  start = time.time()

  # Set initial control values for the actuators
  d.ctrl[0] = 0.044
  d.ctrl[1] = 0.044

  while viewer.is_running(): #and time.time() - start < 30: # Close the viewer automatically after 30 wall-seconds.
    step_start = time.time()

    # mj_step can be replaced with code that also evaluates
    # a policy and applies a control signal before stepping the physics.
    mujoco.mj_step(m, d)

    # Example modification of a viewer option: toggle contact points every two seconds.
    #with viewer.lock():
    #  viewer.opt.flags[mujoco.mjtVisFlag.mjVIS_CONTACTPOINT] = int(d.time % 2)

    # Pick up changes to the physics state, apply perturbations, update options from GUI.
    viewer.sync()

    # Rudimentary time keeping, will drift relative to wall clock.
    time_until_next_step = m.opt.timestep - (time.time() - step_start)
    if time_until_next_step > 0:
      time.sleep(time_until_next_step)
    #time.sleep(.001)
    #show the simulation time
    #print(d.time)


