'''

Tests the solver for a single Schrodinger equation of the type H psi = E psi with H = P²/2 + V

'''

from EQUATION import *
from SYSTEM import *
from TERM import *

import scipy as sc
import numpy as np
from scipy import special

def V(x,y,V0,R0):
	V_ = np.zeros((len(x),len(y))) + V0
	index = np.where(x**2 + y**2 < R0**2)
	V_[index] = 0
	return V_

def V_barrier(x,y,V0,R0):
	V_ = np.zeros((len(x),len(y)))
	index = np.where(np.abs(x) < R0)
	V_[index] = V0
	return V_

def psi_0(X,Y):
	return np.exp(-(((X+0.3)**2 + Y**2)/0.1**2))*np.exp(-1.j*10000.*X)

#Initializing system and equation
system = SYSTEM()
eq1 = EQUATION('eq1')

system.add_equation(eq1) #Adding equation to the system

Z = 8
N = 2**Z

L = 1.
dh = 2.*L/(N-1)

X, Y = np.mgrid[-L:L+dh:dh,-L:L+dh:dh]

k_line = np.fft.fftfreq(N,dh)
k_x, k_y = np.meshgrid(k_line,k_line)
K2 = k_x**2 + k_y**2

V0 = 4e2
R0 = 0.005

dt = 1e-4
N_stride = 100
N_steps = 10

term1 = TERM(0.5*K2,'Momentum','P_squared')
eq1.add_term(term1)

V_ = V_barrier(X,Y,V0,R0)
term2 = TERM(V_,'Position','Binding Potential')
eq1.add_term(term2)

eq1.solution = psi_0(X,Y)
system.area = np.zeros([N,N])
system.area[0:N//2,:] += 1
system.solve(X,Y,dt,N_stride,N_steps)