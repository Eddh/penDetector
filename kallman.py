import numpy as np

class kallman:

	def __init__(self, vectorSize, Hk):
		self.xkPriori = np.array(vectorSize, np.dtype('Float64')
		self.PkPriori = np.array((vectorSize, vectorSize), np.dtype('Float64')
		self.Fk = np.array((vectorSize, vectorSize), np.dtyp('Float64')
		# Qk : covariance of external uncertainty
		self.Qk = np.identity(vectorSize)
		self.Hk = Hk 
		# add Bk maybe if necessary

	def initialize(xkInitial, PkInitial):
		prediction(xkInitial, PkInitial)	

	# zK : measurement
	# Rk : covariance of sensor noise	
	def update(zk, Rk):
		correction(zk, Rk)
		prediction()

	def prediction(xkPosteriori, PkPosteriori):
		xkPriori = Fk.dot(xkPosteriori)
		PkPriori = Fk.dot(PkPosteriori.dot(np.transpose(Fk))) + Qk

	def correction(zk, Rk):
		# zk : sensor reading
		# Hk : sensor matrix for units etc
		# Sk : residual covariance
		HkT = np.transpose(Hk)

		yk = zk - Hk.dot(xkPriori)
		Sk = Hk.dot(PkPriori.dot(HkT)) + Rk

		optimalK = PkPriori.dot(HkT.dot(Sk))

		xkPosteriori = xkPriori + optimalK.dot(yk)
		PkPosteriori = PkPriori - optimalK.dot(Hk.dot(PkPriori))

