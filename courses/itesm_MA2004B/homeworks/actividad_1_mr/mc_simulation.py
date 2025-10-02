from random import random
import matplotlib.pyplot as plt

iterations = 70000
current_state = "dry"

states = [current_state]

for _ in range(1, iterations):
    random_num = random()

    if current_state == "dry":
        if random_num <= 0.8:
            current_state = "dry"
        else:
            current_state = "rain"
    else:  # current_state == "rain"
        if random_num <= 0.6:
            current_state = "dry"
        else:
            current_state = "rain"

    states.append(current_state)


dry_counts = []
count_dry = 0

for i, state in enumerate(states, start=1):
    if state == "dry":
        count_dry += 1
    dry_counts.append(count_dry / i)


# Plot
plt.figure(figsize=(10, 5))
plt.plot(
    range(1, iterations + 1),
    dry_counts,
    label="Relative frequency of Dry",
)
plt.xlabel("iterations")
plt.ylabel("relative frequency")
plt.legend()
plt.grid(True)
plt.savefig("mc_simulation.png")

absolute_frequency = count_dry
relative_frequency = dry_counts[-1]

print(f"Frecuencia absoluta en la última iteración: {absolute_frequency}")
print(f"Frecuencia relativa en la última iteración: {relative_frequency}")
