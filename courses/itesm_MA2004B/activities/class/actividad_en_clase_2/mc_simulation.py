from random import random
import matplotlib.pyplot as plt

iterations = 1000000
current_state = "dry"

states = [current_state]
steps_to_return_dry = []
steps_to_return_rain = []
current_steps_dry = 0
current_steps_rain = 0

for _ in range(1, iterations):
    random_num = random()
    current_steps_dry += 1
    current_steps_rain += 1

    if current_state == "dry":
        if random_num <= 0.8:
            current_state = "dry"
        else:
            current_state = "rain"
    else:
        if random_num <= 0.6:
            current_state = "dry"
        else:
            current_state = "rain"

    states.append(current_state)

    if current_state == "dry" and current_steps_dry >= 1:
        steps_to_return_dry.append(current_steps_dry)
        current_steps_dry = 0

    if current_state == "rain" and current_steps_rain >= 1:
        steps_to_return_rain.append(current_steps_rain)
        current_steps_rain = 0

print("--- State 1 ---")
average_steps = sum(steps_to_return_dry) / len(steps_to_return_dry)
print(f"Average steps to return to state 1: {average_steps:.2f}")
print(f"Steps for each return: {steps_to_return_dry[:10]}...")

print("--- State 2 ---")
average_steps = sum(steps_to_return_rain) / len(steps_to_return_rain)
print(f"Average steps to return to state 2: {average_steps:.2f}")
print(f"Steps for each return: {steps_to_return_rain[:10]}...")
