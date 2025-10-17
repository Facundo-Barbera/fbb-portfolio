import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Números aleatorios de TABLA 18.1
columna_1 = [0.0589, 0.6733, 0.4799, 0.9486, 0.6139, 0.5933, 0.9341, 0.1782, 0.3473, 0.5644]
columna_2 = [0.3529, 0.3646, 0.7676, 0.8931, 0.3919, 0.7876, 0.5199, 0.6358, 0.7472, 0.8954]

# Extender para 60 trabajos
columna_1 = columna_1 * 6
columna_2 = columna_2 * 6

n_trabajos = 60
resultados = []
tiempo_actual = 0
tiempo_fin_maquina = 0

for i in range(n_trabajos):
    if i == 0:
        tiempo_llegada = 0
        tiempo_entre_llegadas = 0
        R_llegada = None
    else:
        R_llegada = columna_1[i-1]
        tiempo_entre_llegadas = -2 * np.log(R_llegada)
        tiempo_llegada = tiempo_actual + tiempo_entre_llegadas

    R_proc = columna_2[i]
    tiempo_proc = 1.1 + 0.9 * R_proc

    hora_inicio = max(tiempo_llegada, tiempo_fin_maquina)
    tiempo_espera = hora_inicio - tiempo_llegada
    hora_salida = hora_inicio + tiempo_proc

    resultados.append({
        'numero': i + 1,
        'R_llegada': R_llegada,
        'tiempo_entre_llegadas': tiempo_entre_llegadas,
        'hora_llegada': tiempo_llegada,
        'R_proc': R_proc,
        'tiempo_proc': tiempo_proc,
        'hora_salida': hora_salida,
        'tiempo_espera': tiempo_espera,
        'tiempo_en_sistema': hora_salida - tiempo_llegada
    })

    tiempo_actual = tiempo_llegada
    tiempo_fin_maquina = hora_salida

df = pd.DataFrame(resultados)

# Estadísticas
tiempo_total = df['hora_salida'].max()
utilizacion = df['tiempo_proc'].sum() / tiempo_total
tiempo_prom_sistema = df['tiempo_en_sistema'].mean()
tiempo_prom_espera = df['tiempo_espera'].mean()

print("Estadísticas del sistema:")
print(f"Tiempo total: {tiempo_total:.4f} horas")
print(f"Utilización de máquina: {utilizacion:.4f} ({utilizacion*100:.2f}%)")
print(f"Tiempo promedio en sistema: {tiempo_prom_sistema:.4f} horas")
print(f"Tiempo promedio de espera: {tiempo_prom_espera:.4f} horas")

df.to_csv('resultados_simulacion.csv', index=False)

# Gráficas
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

axes[0, 0].plot(df['numero'], df['hora_llegada'], 'o-', label='Llegada', markersize=4)
axes[0, 0].plot(df['numero'], df['hora_salida'], 's-', label='Salida', markersize=4)
axes[0, 0].set_xlabel('Número de cliente')
axes[0, 0].set_ylabel('Tiempo (horas)')
axes[0, 0].set_title('Tiempos de Llegada y Salida')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)

axes[0, 1].bar(df['numero'], df['tiempo_espera'], color='orange', alpha=0.7)
axes[0, 1].set_xlabel('Número de cliente')
axes[0, 1].set_ylabel('Tiempo de espera (horas)')
axes[0, 1].set_title('Tiempo de Espera por Cliente')
axes[0, 1].grid(True, alpha=0.3)

axes[1, 0].plot(df['numero'], df['tiempo_en_sistema'], 'g-', linewidth=2)
axes[1, 0].axhline(y=tiempo_prom_sistema, color='r', linestyle='--',
                   label=f"Promedio: {tiempo_prom_sistema:.2f}")
axes[1, 0].set_xlabel('Número de cliente')
axes[1, 0].set_ylabel('Tiempo en sistema (horas)')
axes[1, 0].set_title('Tiempo Total en el Sistema')
axes[1, 0].legend()
axes[1, 0].grid(True, alpha=0.3)

axes[1, 1].hist(df['tiempo_proc'], bins=15, color='purple', alpha=0.7, edgecolor='black')
axes[1, 1].set_xlabel('Tiempo de procesamiento (horas)')
axes[1, 1].set_ylabel('Frecuencia')
axes[1, 1].set_title('Distribución de Tiempos de Procesamiento')
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('simulacion_taller.png', dpi=300, bbox_inches='tight')
