# Imports
import math

# Class
class Calculator:

  # Returns BMI
  def bmi(self, inputs: dict):
    return inputs.get('mass') / ((inputs.get('height') / 100) ** 2)

  # Returns Waist To Height Ratio
  def whtr(self, inputs: dict) -> float:
    waist = inputs.get('waist')
    height = inputs.get('height')
    return waist / height
  # Returns health thresholds for WHTR
  def whtr_unhealthy(self, inputs: dict):
    age = inputs.get('age')
    if   age > 40: return ((age - 40) / 100) + 0.5
    elif age > 50: return 0.6
    else:          return 0.5


  # Returns Waist to Hip Ratio
  def whr(self, inputs: dict) -> float:
    return inputs.get('waist') / inputs.get('hip')
  # Returns overweight threshold for WHR
  def whr_overweight(self, inputs: dict) -> float:
    gender = inputs.get('gender')
    thresholds_by_gender = {
      0: 0.85,
      1: 0.8,
      2: 0.9,
    }
    return thresholds_by_gender.get(gender)
  # Returns obese threshold for WHR
  def whr_obese(self, inputs: dict) -> float:
    gender = inputs.get('gender')
    thresholds_by_gender = {
      0: 0.925,
      1: 0.85,
      2: 1,
    }
    return thresholds_by_gender.get(gender)

  # Returns Body Roundness Index
  def bri(self, inputs: dict) -> float:
    waist = inputs.get('waist')
    height = inputs.get('height')
    try:
      bri = 364.2 - (365.5 * math.sqrt((1 - (waist / (math.pi * height)) ** 2)))
    except (ZeroDivisionError, ValueError):
      # Sometimes sqrt() errors out due to trying to sqrt a negative number
      bri = 'Error'
    return bri
