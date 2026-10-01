[English](README.md) | Español

# Groovn

Letterboxd para música: puntúa y reseña álbumes, y recibe recomendaciones que aprenden tu gusto.

## Estado

En reconstrucción (2026) como proyecto de machine learning. El núcleo es un recomendador
de álbumes entrenado y validado con puntuaciones reales de usuarios (Amazon Reviews 2023,
CDs & Vinyl), comparando paso a paso desde baselines de popularidad hasta factorización
de matrices y un modelo neuronal two-tower.

La versión anterior en Tkinter + MySQL se conserva en el tag [`v0-tkinter`](../../tree/v0-tkinter).

## Resultados

Calidad del ranking top-10 en un conjunto de test separado por tiempo, nunca usado para
ajustar hiperparámetros (ver `notebooks/07_validation.ipynb`). ALS e Item-kNN se ajustaron
antes sobre un conjunto de validación independiente.

| Modelo     | Recall@10 | NDCG@10 | Coverage@10 |
|:-----------|----------:|--------:|------------:|
| Popularity |    0.0014 |  0.0011 |      0.0002 |
| Item-kNN   |    0.0085 |  0.0060 |      0.7514 |
| ALS        |    0.0098 |  0.0066 |      0.0607 |
| Two-Tower  |    0.0035 |  0.0024 |      0.1961 |

ALS ajustado supera a Item-kNN en recall/NDCG general, pero eso esconde una brecha grande:
**ALS nunca recomienda un álbum de larga cola que un usuario realmente haya interactuado
después (Recall@10 = 0.0 en el segmento de ítems de larga cola)**, mientras que Item-kNN
mantiene un recall razonable ahí y cubre ~75% del catálogo frente al ~6% de ALS. Qué modelo
es "mejor" depende de si el objetivo del producto es acertar con el gusto mayoritario o dar
visibilidad a la larga cola — ver el notebook para el desglose completo por segmento (usuarios
fríos vs. activos, ítems populares vs. de larga cola) y por qué importa más que el promedio
general.

## Autor

Lucas Avila Manotas · [LinkedIn](https://www.linkedin.com/in/lucas-avila23)
