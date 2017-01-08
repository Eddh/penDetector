import numpy as np

class Kallman:

	def __init__(self, vectorSize, Hk, Qk, Fk):
		self.xkPriori = np.zeros(vectorSize, dtype = 'Float64')
		self.PkPriori = np.zeros((vectorSize, vectorSize), dtype = 'Float64')
		self.Fk = Fk
		# Qk : covariance of external uncertainty
		self.Qk = Qk
		self.Hk = Hk 
		# add Bk maybe if necessary	

	def setFk(self, Fk):
		self.Fk = Fk

	def initialize(self, xkInitial, PkInitial):
		self.prediction(xkInitial, PkInitial)	

	# zK : measurement
	# Rk : covariance of sensor noise	
	def update(self, zk, Rk):
		self.correction(zk, Rk)
		self.prediction(self.xkPosteriori, self.PkPosteriori)
		return self.xkPosteriori

	def prediction(self, xkPosteriori, PkPosteriori):
		print('ah')
		print(self.xkPriori)
		self.xkPriori = self.Fk.dot(xkPosteriori)
		FkT = np.transpose(self.Fk)
		print(self.Fk)
		print('mul :')
		print(PkPosteriori)
		self.PkPriori = self.Fk.dot(PkPosteriori.dot(np.transpose(self.Fk))) + self.Qk
		#self.PkPriori = FkT.dot(PkPosteriori.dot(self.Fk)) + self.Qk

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
		print('opK')
		print(optimalK)

