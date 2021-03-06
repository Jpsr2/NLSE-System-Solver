'''

Defines the class EQUATION which will be used as an object in the system of NLSE we want to solve.

'''

import numpy as np

class EQUATION:
	def __init__(self,name = '',ground_state = None):
		self.n_terms = 0 #Number of terms in the equation
		self.terms = {} #Dictionary of terms in the equation
		self.name = name #Name of the equation (optional)
		self.L = [] #Part to be solved in the momentum representation
		self.N = [] #Part to be solved in the position representation
		self.V = [] #Binding potential of the equation
		self.solution = ground_state #Solution of the equation
		self.inside = [] #Percentage of the solution inside an area
		self.outside = [] #Outside that area

	def __str__(self): #String conversion
		terms_str = '\n'
		for i in self.terms:
			terms_str += str(self.terms[i]) + '\n'
		return '--EQUATION-- \nName: %s \nNº of Terms: %s \nTerms: %s\n' %(self.name,self.n_terms,terms_str)

	def add_term(self,term): #Adds a term to the equation
		self.terms[self.n_terms] = term  
		self.n_terms += 1

	def parts(self,dt): #Updates the L and N parts of the equation
		momentum_matrix = [] #Matrix with the momentum representation parts
		position_matrix = [] #Matrix with the position representation parts
		for i in self.terms: #Iterate through the terms
			term = self.terms[i]
			if term.time_derivative: #If the term is to be integrated in time
				term.matrix += dt*term.function(**term.variables)
				continue
			if term.time_variant: #If term is time variant, recalculate its value
				term.matrix = term.function(**term.variables)
			if term.representation == 'Momentum':
				if momentum_matrix == []:
					momentum_matrix = np.copy(term.matrix)
				else:
					momentum_matrix += term.matrix
			else:
				if position_matrix == []:
					position_matrix = np.copy(term.matrix).astype(np.complex128)
				else:
					position_matrix += term.matrix.astype(np.complex128)
				if term.name == 'Binding Potential': #If there is a binding potential to represent in the figures
					self.V = term.matrix
		self.L = momentum_matrix
		self.N = position_matrix

	def step(self,dt): #Performs a step of the SSSFM
		psi = self.solution

		#Half step in L
		psi = np.fft.fft2(psi)
		psi = np.exp(0.5j*self.L*dt)*psi

		#Full step in N
		psi = np.fft.ifft2(psi)
		psi = np.exp(1.0j*self.N*dt)*psi

		#Half step in L
		psi = np.fft.fft2(psi)
		psi = np.exp(0.5j*self.L*dt)*psi

		psi = np.fft.ifft2(psi)

		for i in self.terms:
			term = self.terms[i]
			if term.time_derivative and not term.auxiliary:
				psi += term.matrix

		self.solution = psi

	def reflections(self,area):
		#Computes the percentage of the solution inside an area
		index = np.where(area == 1)
		total = np.sum(np.abs(self.solution)**2)
		inside = np.sum(np.abs(self.solution[index])**2)/total*100
		outside = 100-inside
		self.inside.append(inside)
		self.outside.append(outside)