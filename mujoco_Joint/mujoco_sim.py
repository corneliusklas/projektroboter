import mujoco
import mujoco.viewer
print(mujoco.__version__) 
import matplotlib.pyplot as plt
import os
MODEL=  "IK" # "IK" or "FK""Patent"
MOVE = False

# === Dynamixel Setup ===
if MOVE:
  #load dynamixel calibration file


  from pypot.dynamixel import DxlIO
  dxl_port = 'COM17'
  motor_id = 4
  dxl = DxlIO(dxl_port)
  dxl.enable_torque([motor_id])
  dxl.set_torque_limit({motor_id: 1023}) # geht nicht?
  #read AND PRINT torque limit
  print(dxl.get_torque_limit([motor_id]))
  dxl.set_max_torque({motor_id: 1023})

   # 🛠️ USB-Latenz-Tipp:
    # (nur Windows): Öffne den Geräte-Manager → Anschlüsse (COM & LPT) → „Silicon Labs CP210x USB to UART Bridge“ (oder dein Adapter)
    # → Rechtsklick → Eigenschaften → Erweitert → „Wartezeit (ms)“ auf **1** setzen (Standard ist 16)
    # Gutes USB-Kabel verwenden, um Latenz zu minimieren.

# === Hilfsfunktion: radians → degrees → goal_pos
def rad_to_dxl_angle(rad):   
  deg = rad * 180 / 3.1416
  deg = max(min(deg, 150), -150)  # Clamp auf realistische Winkel
  return deg

# === Make model and data ====
if MODEL == "IK":
  model_path = os.path.join(os.getcwd(), "mujoco_Joint\model\IK.xml")
  
elif MODEL == "FK":
  model_path = os.path.join(os.getcwd(), "mujoco_Joint\model\FK.xml")

elif MODEL == "Patent":
  model_path = os.path.join(os.getcwd(), "mujoco_Joint\model\ik_patent.xml")

model = mujoco.MjModel.from_xml_path(model_path)
data = mujoco.MjData(model)
#print all data fields
#print(dir(data))


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
  
 
  #viewer.cam.type = mujoco.mjtCamera.mjCAMERA_FREE
  #viewer.cam.fixedcamid = -1  # Use free camera


  start = time.time()

  if MODEL == "IK":
    #pass
    for i in range(len(d.ten_length)):
      print("d.ten_length[",i,"]=",d.ten_length[i])
  elif MODEL == "FK":
    # Set initial control values for the actuators
    #- Seil 1: bis Schulter       → 0.046 m
    #- Seil 2: bis Ellenbogen 1  → 0.199 m
    #- Seil 3: bis Ellenbogen 2  → 0.276 m
    #- Seil 4: bis Handgelenk    → 0.429 m
    #- x bis Hand (+ 0.05 m)     → 0.479 m
    d.ctrl[0] = 0 #starting z rotation
    d.ctrl[1] = 0.046
    d.ctrl[2] = 0.046
    d.ctrl[3] = 0.199
    d.ctrl[4] = 0.199
    d.ctrl[5] = 0.276
    d.ctrl[6] = 0.276
    d.ctrl[7] = 0.429
    d.ctrl[8] = 0.429
    d.ctrl[9] = 0.454


  while viewer.is_running(): #and time.time() - start < 30: # Close the viewer automatically after 30 wall-seconds.
    step_start = time.time()

    # mj_step can be replaced with code that also evaluates
    # a policy and applies a control signal before stepping the physics.
    mujoco.mj_step(m, d)


    # Pick up changes to the physics state, apply perturbations, update options from GUI.
    viewer.sync()


    # === Steuerung aus der Simulation auf Dynamixel übertragen ===
    if MOVE:
      sim_rad = d.qpos[0]  # <- oder passenden Index des Gelenks wählen!
      goal_angle = rad_to_dxl_angle(sim_rad)
      dxl.set_goal_position({motor_id: goal_angle})

    # Rudimentary time keeping, will drift relative to wall clock.
    #time_until_next_step = m.opt.timestep - (time.time() - step_start)
    #if time_until_next_step > 0:
    #  time.sleep(time_until_next_step)

    #read the joint angles
    #print("d.qpos[0]=",d.qpos[0])
    #time.sleep(.001)
    #show the simulation time
    #print(d.time)


