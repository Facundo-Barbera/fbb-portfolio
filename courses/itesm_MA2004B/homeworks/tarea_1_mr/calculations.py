import random
import matplotlib.pyplot as plt

p_transport = 0.6
iterations = 900000

apprehensions = 0
transports = 0
freqs = []

for i in range(1, iterations + 1):
    if random.random() < 0.01:
        apprehensions += 1
        if random.random() < p_transport:
            transports += 1

    if apprehensions > 0:
        freqs.append(transports / apprehensions)
    else:
        freqs.append(0)

plt.plot(freqs, label="Frecuencia relativa de traslado")
plt.axhline(p_transport, color="red", linestyle="--", label="Valor esperado (0.6)")
plt.xlabel("Iteraciones")
plt.ylabel("Frecuencia relativa")
plt.legend()
plt.grid(True)
plt.show()

print(
    "Probabilidad final aproximada:",
    transports / apprehensions if apprehensions > 0 else 0,
)
