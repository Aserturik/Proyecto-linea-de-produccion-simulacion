#!/usr/bin/env python3
"""
Script para debuggear el generador de números aleatorios
"""

from aleatorios.src.modelos.validated_random import ValidatedRandom

def test_random_generator():
    """Prueba el generador de números aleatorios."""
    
    rng = ValidatedRandom(12345)
    
    print("=== Prueba del Generador de Números Aleatorios ===")
    print("Primeros 20 números aleatorios:")
    
    defect_prob = 0.1
    defectos = 0
    
    for i in range(20):
        num = rng.random()
        es_defecto = num < defect_prob
        if es_defecto:
            defectos += 1
        print(f"{i+1:2d}: {num:.6f} -> {'DEFECTO' if es_defecto else 'OK'}")
    
    print(f"\nTotal defectos: {defectos}/20 ({defectos/20*100:.1f}%)")
    print(f"Esperado: ~{defect_prob*100:.1f}%")

if __name__ == "__main__":
    test_random_generator()
