<<<<<<< HEAD
from scipy.interpolate import RegularGridInterpolator
from numpy import linspace, zeros, array
from numpy import save, load
folder = "calibration/motionData/"
generate = False
if generate:
    xspan=20
    yspan=20
    zspan=20
    uspan=20
    vspan=20
    wspan=20
    x = linspace(1,3,xspan)
    y = linspace(1,3,yspan)
    z = linspace(1,3,zspan)
    u = linspace(1,3,uspan)
    v = linspace(1,3,vspan)
    w = linspace(1,3,wspan)
    theta1 = zeros((xspan,yspan,zspan,uspan,vspan,wspan))
    for i in range(xspan):
        for j in range(yspan):
            for k in range(zspan):
                for l in range(uspan):
                    for m in range(vspan):
                        for n in range(wspan):
                            theta1[i,j,k] = 100000*x[i] + 10000*y[j] + 1000*z[k] + 100*u[l] + 10*v[m] + w[n]

    save(folder+"theta1.npy",theta1)
    save(folder+"x.npy",x)
    save(folder+"y.npy",y)
    save(folder+"z.npy",z)
    save(folder+"u.npy",u)
    save(folder+"v.npy",v)
    save(folder+"w.npy",w)

else:
    theta1 = load(folder+"theta1.npy")
    x = load(folder+"x.npy")
    y = load(folder+"y.npy")
    z = load(folder+"z.npy")
    u = load(folder+"u.npy")
    v = load(folder+"v.npy")
    w = load(folder+"w.npy")

    #Data:
    """[[[111. 112. 113.]
    [121. 122. 123.]
    [131. 132. 133.]]

    [[211. 212. 213.]
    [221. 222. 223.]
    [231. 232. 233.]]

    [[311. 312. 313.]
    [321. 322. 323.]
    [331. 332. 333.]]]"""

    #print(theta1)

    #meassure time
    import time
    start = time.time()



    for i in range(1000):
        pts = array([[1.1,1.2,1.3,1.4,1.5,1.6]]) #array([[1,2,3],[1.2,2.2,2.8],[1.2,2.3,2.7]])
        fn = RegularGridInterpolator((x,y,z,u,v,w), theta1)
        fn(pts)
    print("time: ",time.time()-start)


=======
from scipy.interpolate import RegularGridInterpolator
from numpy import linspace, zeros, array
from numpy import save, load
folder = "calibration/motionData/"
generate = False
if generate:
    xspan=20
    yspan=20
    zspan=20
    uspan=20
    vspan=20
    wspan=20
    x = linspace(1,3,xspan)
    y = linspace(1,3,yspan)
    z = linspace(1,3,zspan)
    u = linspace(1,3,uspan)
    v = linspace(1,3,vspan)
    w = linspace(1,3,wspan)
    theta1 = zeros((xspan,yspan,zspan,uspan,vspan,wspan))
    for i in range(xspan):
        for j in range(yspan):
            for k in range(zspan):
                for l in range(uspan):
                    for m in range(vspan):
                        for n in range(wspan):
                            theta1[i,j,k] = 100000*x[i] + 10000*y[j] + 1000*z[k] + 100*u[l] + 10*v[m] + w[n]

    save(folder+"theta1.npy",theta1)
    save(folder+"x.npy",x)
    save(folder+"y.npy",y)
    save(folder+"z.npy",z)
    save(folder+"u.npy",u)
    save(folder+"v.npy",v)
    save(folder+"w.npy",w)

else:
    theta1 = load(folder+"theta1.npy")
    x = load(folder+"x.npy")
    y = load(folder+"y.npy")
    z = load(folder+"z.npy")
    u = load(folder+"u.npy")
    v = load(folder+"v.npy")
    w = load(folder+"w.npy")

    #Data:
    """[[[111. 112. 113.]
    [121. 122. 123.]
    [131. 132. 133.]]

    [[211. 212. 213.]
    [221. 222. 223.]
    [231. 232. 233.]]

    [[311. 312. 313.]
    [321. 322. 323.]
    [331. 332. 333.]]]"""

    #print(theta1)

    #meassure time
    import time
    start = time.time()



    for i in range(1000):
        pts = array([[1.1,1.2,1.3,1.4,1.5,1.6]]) #array([[1,2,3],[1.2,2.2,2.8],[1.2,2.3,2.7]])
        fn = RegularGridInterpolator((x,y,z,u,v,w), theta1)
        fn(pts)
    print("time: ",time.time()-start)


>>>>>>> 5a8394f52afdf53d4be1d96fbdf1e105decc4505
    print(fn(pts))