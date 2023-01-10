

class Hydrogen:
	def __init__(self, max_capacity, max_power_FC, max_power_El, Eff_FC, Eff_El):
		self.max_capacity = max_capacity        # MWh
		self.max_power_FC = max_power_FC        # MW
		self.Eff_FC = Eff_FC                    # -
		self.max_power_El = max_power_El        # MW
		self.Eff_El = Eff_El                    # -
		self.filled_capacity = 0                # MWh
	
	def store(self, P_residual, E_reserve, Battery_system, P_sell_aim_hydrogen):
		P_not_used = 0
		P_shortage = 0
		P_stored = 0
		P_sold_H2 = 0
		
		# Check if energy needs to be taken out or stored
		# filled_capacity_total = self.filled_capacity * self.Eff_FC + Battery_system.filled_capacity * Battery_system.eff
		
		if P_residual > 0:
			# Check is residual available power is bigger than maximum power available
			if P_residual > self.max_power_El:
				# Check if enough storage is available
				if self.filled_capacity + self.max_power_El * self.Eff_El <= self.max_capacity:
					P_stored = self.max_power_El
				# If not enough storage available, store whatever we can
				else:
					P_stored = (self.max_capacity - self.filled_capacity) / self.Eff_El
					P_not_used = P_residual - P_stored
			# If residual power is smaller than max power El
			else:
				# Check if enough storage is available
				if self.filled_capacity + P_residual * self.Eff_El <= self.max_capacity:
					P_stored = P_residual
				else:
					P_stored = (self.max_capacity - self.filled_capacity) / self.Eff_El
					
					P_not_used = P_residual - P_stored
					
			self.filled_capacity += P_stored * self.Eff_El
		
		# Try to take out energy
		elif P_residual < 0:
			# Check if needed power is smaller than max electrolysis power
			if -P_residual < self.max_power_FC:
				# If not enough in storage
				if self.filled_capacity * self.Eff_FC + P_residual < 0:
					# Shortage = Power created + Power needed       (Power needed is negative)
					P_shortage = self.filled_capacity * self.Eff_FC + P_residual
					self.filled_capacity = 0
				# If there is enough in storage
				else:
					# Power out = Power needed / eff_el
					self.filled_capacity += P_residual / self.Eff_FC
			# If more power than maximum is needed, take out maximum
			else:
				# If not enough in storage:
				if self.filled_capacity * self.Eff_FC - self.max_power_FC < 0:
					# Shortage = Power created + Power needed       (Power needed is negative)
					P_shortage = self.filled_capacity * self.Eff_FC + P_residual
					self.filled_capacity = 0
				# If there is enough in storage
				else:
					# Power out = Power needed / eff_el
					P_shortage = self.max_power_FC + P_residual
					self.filled_capacity -= self.max_power_FC / self.Eff_FC
		
		# If there is power left to store and not all capacity of FC is used, then try to make hydrogen for selling
		filled_capacity_total = self.filled_capacity * self.Eff_FC + Battery_system.filled_capacity * Battery_system.eff
		if filled_capacity_total - P_sell_aim_hydrogen >= E_reserve:
			P_sold_H2 = P_sell_aim_hydrogen
			self.filled_capacity -= P_sold_H2
		elif filled_capacity_total >= E_reserve:
			P_sold_H2 = filled_capacity_total - E_reserve
			self.filled_capacity -= P_sold_H2
		
		return P_not_used, P_shortage, P_stored, P_sold_H2
	
		
class Battery:
	def __init__(self, max_capacity, max_power, discharge_rate, eff):
		self.max_capacity = max_capacity        # MWh
		self.max_power = max_power              # MW
		self.filled_capacity = 0                # MWh
		self.discharge_rate = discharge_rate    # %/day
		self.eff = eff                          # -
	
	def store(self, P_available, E_reserve):
		P_stored = 0
		
		self.filled_capacity = self.filled_capacity * self.discharge_rate ** (1 / 24)  # Every hour
		
		# Check if energy needs to be taken out or stored
		if P_available > 0 and self.filled_capacity * self.eff <= E_reserve:
			# check if available power is larger than maximum power
			if P_available > self.max_power:
				# Check if enough storage is available
				if self.filled_capacity + self.max_power <= self.max_capacity:
					P_stored = self.max_power

				# If not enough storage available, use whatever we can
				else:
					P_stored = self.max_capacity - self.filled_capacity

			# If the available power is smaller than maximum
			else:
				# Check if enough storage is available
				# Additional check to make sure filled_capacity doesn't exceed capacity
				if self.filled_capacity + P_available <= self.max_capacity:
					# Store the available power
					P_stored = P_available

				# If not enough storage available, use whatever we can
				# Here there is always zero or positive power going into the system
				else:
					P_stored = self.max_capacity - self.filled_capacity
					
			self.filled_capacity += P_stored
		
		# If power needs to be taken out
		# P_available < 0
		elif P_available < 0:
			# Check if enough is in storage:
			if self.filled_capacity + P_available / self.eff >= 0:
				P_stored = P_available
				self.filled_capacity += P_stored / self.eff
			# If there is not enough power available, empty the battery
			else:
				P_stored = -self.filled_capacity * self.eff
				self.filled_capacity = 0
		
		# Positive when there is power left for the hydrogen system
		# Negative when power needs to be taken out of the hydrogen system
		residual_power = P_available - P_stored
		
		return residual_power, P_stored if P_stored > 0 else 0
	