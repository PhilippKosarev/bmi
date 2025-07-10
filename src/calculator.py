# Imports
import math

# Class
class Calculator:

  # Returns BMI
  def bmi(self, inputs: dict):
    return inputs.get('mass') / ((inputs.get('height') / 100) ** 2)


  # Returns Waist To Height Ratio
  def whtr(self, inputs: dict):
    return inputs.get('waist') / inputs.get('height')
  # Returns health thresholds for WHTR
  def whtr_unhealthy(self, inputs: dict):
    age = inputs.get('age')
    if   age > 40: return ((age - 40) / 100) + 0.5
    elif age > 50: return 0.6
    else:          return 0.5


  # Returns Waist to Hip Ratio
  def whr(self, inputs: dict):
    return inputs.get('waist') / inputs.get('hip')
  # Returns overweight threshold for WHR
  def whr_overweight(self, inputs: dict):
    gender = inputs.get('gender')
    if   gender == 0: return 0.85 # Average
    if   gender == 1: return 0.8 # Female
    elif gender == 2: return 0.9 # Male
  # Returns obese thresholds for WHR
  def whr_obese(self, inputs: dict):
    gender = inputs.get('gender')
    if   gender == 0: return 0.925 # Average
    if   gender == 1: return 0.85 # Female
    elif gender == 2: return 1 # Male


  # Returns Body Roundness Index
  def bri(self, inputs: dict):
    waist = inputs.get('waist')
    height = inputs.get('height')
    try:
      bri = 364.2 - (365.5 * math.sqrt((1 - (waist / (math.pi * height)) ** 2)))
    except (ZeroDivisionError, ValueError):
      # Sometimes sqrt() errors out due to trying to sqrt a negative number
      bri = 'Error'
    return bri
