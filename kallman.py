import numpy as np

class Kallman:

	def __init__(self, vectorSize, Hk, Qk, Fk):
		# xkPriori : estimate of the current state from the previous state
		self.xkPriori = np.zeros(vectorSize, dtype = 'Float64')
		# PkPriori : estimate of the covariance of the current state from the previous state
		self.PkPriori = np.zeros((vectorSize, vectorSize), dtype = 'Float64')
		# Fk : matrix modeling the transition between 2 consecutives states
		self.Fk = Fk
		# Qk : covariance of external uncertainty
		self.Qk = Qk
		# Hk : sensor matrix for units etc
		self.Hk = Hk 

	def setFk(self, Fk):
		self.Fk = Fk

	# necessary initialization before starting the prediction/correction loop
	def initialize(self, xkInitial, PkInitial):
		self.prediction(xkInitial, PkInitial)	

	# zK : measurement
	# Rk : covariance of sensor noise	
	def update(self, zk, Rk):
		self.correction(zk, Rk)
		self.prediction(self.xkPosteriori, self.PkPosteriori)
		return self.xkPosteriori

	def prediction(self, xkPosteriori, PkPosteriori):
		self.xkPriori = self.Fk.dot(xkPosteriori)
		FkT = np.transpose(self.Fk)
		self.PkPriori = self.Fk.dot(PkPosteriori.dot(FkT)) + self.Qk

	def correction(self, zk, Rk):
		# zk : sensor reading
		# Hk : sensor matrix for units etc
		# Sk : residual covariance
		HkT = np.transpose(self.Hk)

		yk = zk - self.Hk.dot(self.xkPriori)
		Sk = self.Hk.dot(self.PkPriori.dot(HkT)) + Rk

		optimalK = self.PkPriori.dot(HkT.dot(Sk))

		self.xkPosteriori = self.xkPriori + optimalK.dot(yk)
		self.PkPosteriori = self.PkPriori - optimalK.dot(self.Hk.dot(self.PkPriori))

