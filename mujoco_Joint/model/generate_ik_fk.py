def generate_files_from_template(template_path, ik_path, fk_path):
    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    """Seilanker-Positionen (Sites) für ein Rolling-Contact-Gelenk
    Radius: 20.5 mm = 0.0205 m
    Z-Offset: -0.023 (Start), 0.0 (Ende)

    Berechnung (im XY-Kreis, um Z):
    x = R * cos(theta)
    y = R * sin(theta)
    Alle Winkel in Grad → Radiant: θ [rad] = θ [deg] * π / 180

    Tendon-X Start:
    -25° → x =  0.0186   y = -0.0087   z = -0.023  (gripper)
    -15° → x =  0.0198   y = -0.0053   z = -0.023  
    -5° → x =  0.0204   y = -0.0018   z = -0.023  
    +5° → x =  0.0204   y =  0.0018   z = -0.023  
    +15° → x =  0.0198   y =  0.0053   z = -0.023  

    Tendon-Y Start:
    +75°  → x =  0.0053   y =  0.0198   z = -0.023  
    +85°  → x =  0.0018   y =  0.0204   z = -0.023  
    +95°  → x = -0.0018   y =  0.0204   z = -0.023  
    +105° → x = -0.0053   y =  0.0198   z = -0.023  
    Punkt 1 und 2 wurden im realen roboter vertauscht, daher die Umstellung."""

    sites = {
    "site_gri": '-0.0186 -0.0087 ',
    "site_x_2": '0.0198 -0.0053 ',
    "site_x_1": '0.0204 -0.0018 ',
    "site_x_3": '0.0204  0.0018 ',
    "site_x_4": '0.0198  0.0053 ',
    "site_y_2": '0.0053  0.0198 ',
    "site_y_1": '0.0018  0.0204 ',
    "site_y_3": '-0.0018 0.0204 ',
    "site_y_4": '-0.0053 0.0198 ',
    }  

    # Replace placeholders with actual site definitions
    for key, value in sites.items():
        content = content.replace(f"${key}$", value)

    # IK-Version: $IK$ → "--", $FK$ → ""
    ik_version = content.replace("$IK$", "--").replace("$FK$", "")

    # FK-Version: $FK$ → "--", $IK$ → ""
    fk_version = content.replace("$FK$", "--").replace("$IK$", "")



    with open(ik_path, "w", encoding="utf-8") as f:
        f.write(ik_version)
    with open(fk_path, "w", encoding="utf-8") as f:
        f.write(fk_version)

    print(f"Generated '{ik_path}' and '{fk_path}' from template.")

# Beispielaufruf:
generate_files_from_template("mujoco_Joint/model/template.xml", "mujoco_Joint/model/ik.xml", "mujoco_Joint/model/fk.xml")
