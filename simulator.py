import numpy 
import math
import random
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d import proj3d
import matplotlib.pyplot as plt
from Arrow3D import *
import Rotation

rotation = Rotation.Rotation()

def controlInput(x, y, t):
    if t == 2:
        inc = 1
    else:
        inc = 0

    inp = numpy.zeros((4))
    inp[:] = 288
    inp[0] += inc
    inp[2] += inc
    inp = inp**2;
    return inp
        
def getConvMatrix(theta):
    return numpy.array([[ 1,                   0,                  - math.sin(theta[1])],
                        [ 0,  math.cos(theta[0]), math.cos(theta[1])*math.sin(theta[0])],
                        [ 0, -math.sin(theta[0]), math.cos(theta[1])*math.cos(theta[0])]])

# Compute thrust given current inputs and thrust coefficient.
def thrust( inputs, k):
    # Inputs are values for ${\omega_i}^2$
    T = numpy.array([[0], [0],[ k * sum(inputs)]])
    return T

# Compute torques, given current inputs, length, drag coefficient, and thrust coefficient.
def torques( inputs, L, b, k):
    # Inputs are values for ${\omega_i}^2$
    tau = numpy.array([[ L * k * (inputs[0] - inputs[2])],
                       [L * k * (inputs[1] - inputs[3])],
                       [b * (inputs[0] - inputs[1] + inputs[2] - inputs[3])]])
    return tau

def acceleration( inputs, angles, xdot, m, g, k, kd):
    gravity = [[0], [0], [-g]]
    R = rotation.rotate(angles)
    T = R.dot(thrust(inputs, k))
#     print ("R: ", R)
#     print ("thrust:", thrust(inputs, k))
    print ("T: ", T)
    Fd = -kd * xdot
    a = gravity + 1 / m * T + Fd
    return a

def angular_acceleration(inputs, omega, Inertia, L, b, k):
    tau = torques(inputs, L, b, k)
    print ("tau: ", tau)
#    temp = numpy.cross(numpy.matrix.transpose(omega),numpy.matrix.transpose(Inertia.dot(omega)))
    temp =  numpy.cross(omega,Inertia.dot(omega), axisa=0, axisb=0, axisc=0)
    omegaddot = numpy.linalg.inv(Inertia).dot(tau - temp)
    return omegaddot


def thetadot2omega(thetadot, theta):    
    return getConvMatrix(theta).dot(thetadot)

def omega2thetadot(omega, theta):
    return numpy.linalg.inv(getConvMatrix(theta)).dot(omega)



plt.ion()
enable3d = False

# Simulation times, in seconds.
start_time = 0  #s
end_time = 10   #s
dt = 0.1
      
times = numpy.arange(start_time, end_time, dt)

m = 0.1 #kg
g = 9.81 #m/s^2
k = 3e-6 # Some gain factor for motors? 
kd = 0.25

L = 0.14 #m
b = 1e-7 #is our drag coefficient

I_xx = 5e-3
I_yy = 5e-3
I_zz = 10e-3
I = numpy.array([[I_xx,    0,    0],
                 [   0, I_yy,    0],
                 [   0,    0, I_zz]])

# Initial simulation state.
x = numpy.array([[0], [0], [0]])
xdot = numpy.zeros((3, 1))
theta = numpy.zeros((3, 1))

# Simulate some disturbance in the angular velocity.
# The magnitude of the deviation is in radians / second.
deviation = 100
#thetadot = numpy.radians(2 * deviation * numpy.random.rand(3, 1) - deviation)
thetadot = numpy.zeros((3,1))

print ("thetadot: ", thetadot)

xpos, ypos, zpos = 0,0,0

fig = plt.figure(figsize=(10,16))
ax_xyplane = fig.add_subplot(211)
ax_xzplane = fig.add_subplot(212)
plt.tight_layout(pad=4.0, w_pad=2.0, h_pad=2.0)

if enable3d:
    fig3d = plt.figure(figsize=(10,16))
    ax3d = fig3d.add_subplot(111, projection='3d')
    plt.figure(2)
 
line1_1, = ax_xyplane.plot(xpos, ypos, "b") # vector in x-direction 
line1_2, = ax_xyplane.plot(xpos, ypos, "g") # vector in y-direction 
line2_1, = ax_xzplane.plot(xpos, ypos, "r") # force in z-direction
line2_2, = ax_xzplane.plot(xpos, ypos, "b") # vector in z-direction

ax_xyplane.set_ylim([-5,5])
ax_xyplane.set_xlim([-8,8])
ax_xyplane.set_title("XY - plane")
ax_xyplane.set_xlabel("X")
ax_xyplane.set_ylabel("Y")


ax_xzplane.set_ylim([-5,5])
ax_xzplane.set_xlim([-8,8])
ax_xzplane.set_title("XZ - plane")
ax_xzplane.set_xlabel("X")
ax_xzplane.set_ylabel("Z")

xBody = numpy.array([[1], [0], [0]])
yBody = numpy.array([[0], [1], [0]])
zBody = numpy.array([[0], [0], [1]])


# Step through the simulation, updating the state.
for t in times:
    # Take input from our controller.
    i = controlInput(xpos, ypos, t)
     
    omega = thetadot2omega(thetadot, theta)
     
    # Compute linear and angular accelerations.
    a = acceleration(i, theta, xdot, m, g, k, kd)
    omegadot = angular_acceleration(i, omega, I, L, b, k)
     
    omega = omega + dt * omegadot
    thetadot = omega2thetadot(omega, theta) 
    theta = theta + dt * thetadot
    xdot = xdot + dt * a
    x = x + dt * xdot
    
    xpos, ypos, zpos = x[0][0], x[1][0], x[2][0]
     
    print("a: ", a)
#    print("theta: ", theta)
 
    if enable3d:
        ax3d.cla()
        ax3d.set_ylim([-10, 10])
        ax3d.set_xlim([-10, 10])
        ax3d.set_zlim([ 0, 5])
        ax3d.plot( [xpos], [ypos], [zpos], "bo")
        ax3d.plot( [xpos, xpos + a[0]], [ypos, ypos+a[1]] , [zpos, zpos+a[2]],"g-",linewidth=2)
        ax3d.set_title( "x: " + str(xpos) + "   y: " + str(ypos) + "   z: " + str(zpos) + "  t: " + str(t) )
        ax3d.set_xlabel("X")
        ax3d.set_ylabel("Y")
        ax3d.set_zlabel("Z")
        plt.draw()
    
    R = rotation.rotate(theta)
    xBody_current = R.dot(xBody)
    yBody_current = R.dot(yBody)
    zBody_current = R.dot(zBody)

    ax_xyplane.set_title("XY - plane: " +str(xpos) + ", " + str(ypos) +"    t: " + str(t))
    line1_1.set_xdata([xpos, xpos + xBody_current[0]])
    line1_1.set_ydata([ypos, ypos + xBody_current[1]])
    line1_2.set_xdata([xpos, xpos + yBody_current[0]])
    line1_2.set_ydata([ypos, ypos + yBody_current[1]])

    line2_1.set_xdata([xpos, 4*(xpos + a[0])])
    line2_1.set_ydata([zpos, 4*(zpos + a[2])])
    line2_2.set_xdata([xpos, xpos + zBody_current[0]])
    line2_2.set_ydata([zpos, zpos + zBody_current[2]])
#    ax_xzplane.plot(xpos, zpos, "go")
    #
    fig.canvas.draw()
#    fig.canvas.flush_events() #needed?
    
# --------------------------------------------------------------------------------------------    
    
    
 
 #   ax_xzplane.plot([xpos, xpos + a[0]],[zpos, zpos+a[2]], "r")
 #   ax_xzplane.plot([xpos, xpos + zBody_current[0]],[zpos, zpos+zBody_current[2]],"b")
    #ax_xzplane.plot([xpos, xpos + xBody_current[0]],[zpos, zpos+xBody_current[2]], "g")    
    
    
#    ax_xyplane.plot([xpos, xpos + xBody_current[0]],[ypos, ypos+xBody_current[1]])
#    ax_xyplane.plot([xpos, xpos + yBody_current[0]],[ypos, ypos+yBody_current[1]])  
    
# def rotate(theta):
#     R_x = numpy.array([[               1,               0,                0],
#                        [               0, math.cos(theta[0]), -math.sin(theta[0])],
#                        [               0, math.sin(theta[0]),  math.cos(theta[0])]])
#     
#     R_y = numpy.array([[ math.cos(theta[1]),               0,  math.sin(theta[1])],
#                        [               0,               1,               0],
#                        [-math.sin(theta[1]),               0,  math.cos(theta[1])]])
#     
#     R_z = numpy.array([[ math.cos(theta[2]), -math.sin(theta[2]),               0],
#                        [ math.sin(theta[2]),  math.cos(theta[2]),               0],
#                        [               0,               0,                1]])
#     
#     R = R_x.dot(R_y).dot(R_z)
#     print ("R: ", R)
#     return R

    #a1 = Arrow3D([xpos, xpos + xBody[0]],[ypos, ypos+xBody[1]], [zpos, zpos+xBody[2]], mutation_scale=20, lw=3, arrowstyle="-|>", color="r")
    #a2 = Arrow3D([xpos, xpos + yBody[0]],[ypos, ypos+yBody[1]], [zpos, zpos+yBody[2]], mutation_scale=20, lw=3, arrowstyle="-|>", color="b")
    #ax.add_artist(a1)
    #ax.add_artist(a2)
    
#    x_data.append(xpos)
#    y_data.append(ypos) 
    #ax_xyplane.plot(xpos, ypos, "go")    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

