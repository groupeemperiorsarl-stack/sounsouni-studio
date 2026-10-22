"""Ambiances de fond fabriquées en code (pas d'enregistrement, pas de boucle qui se répète).
Grillons / cigales de nuit : des insectes discrets, à des hauteurs et des rythmes différents, sur un fond de nuit très doux.
Règle d'Issa (22/10/2026) : le cri des insectes ne doit jamais être stressant → aigus adoucis, chants espacés et irréguliers,
et le niveau final est réglé par audio.py pour rester toujours sous les voix (oreille : earshot, voir docs/OREILLE.md)."""
import numpy as np
SR = 44100

def _passe_bas(x, fc):   # filtre doux d'ordre 1 (adoucit les aigus)
    a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); z = 0.0
    for i in range(len(x)): z = (1 - a) * x[i] + a * z; y[i] = z
    return y

def _bruit_doux(n, rng, fc):   # bruit filtré par blocs (rapide), sans grésillement
    w = rng.standard_normal(n // 64 + 2); w = np.interp(np.arange(n) / 64, np.arange(len(w)), w)
    return _passe_bas(w.astype(np.float64), fc)

def grillons(dur, seed=1):
    """Fond de nuit : 3 à 4 grillons discrets + souffle très léger. Renvoie un signal mono à 44,1 kHz, crête 0,5."""
    rng = np.random.default_rng(seed); n = int(dur * SR); out = np.zeros(n)
    for k in range(rng.integers(3, 5)):   # chaque grillon a sa note, son rythme, son volume, et se tait parfois
        f0 = rng.uniform(3900, 4600) * (1 + 0.06 * k); g = rng.uniform(0.25, 1.0) * (0.75 ** k)
        t = rng.uniform(0, 1.5)
        while t < dur:
            nb = rng.integers(3, 7); pul = rng.uniform(0.012, 0.02); gap = rng.uniform(0.012, 0.022)
            for p in range(nb):   # un « cri-cri » : quelques petites impulsions arrondies
                i = int((t + p * (pul + gap)) * SR); m = int(pul * SR)
                if i + m >= n: break
                tt = np.arange(m) / SR; env = np.sin(np.pi * tt / pul) ** 2
                out[i:i + m] += g * env * np.sin(2 * np.pi * f0 * (1 + rng.uniform(-0.01, 0.01)) * tt)
            t += nb * (pul + gap) + rng.uniform(0.35, 1.6) + (rng.uniform(2, 5) if rng.random() < 0.12 else 0)
    out = out - 0.35 * (out - _passe_bas(out, 6000))   # les aigus perçants (au-dessus de 6 kHz) sont adoucis
    out += 0.012 * _bruit_doux(n, rng, 700)   # souffle de nuit, très bas
    fondu = min(n // 2, int(0.8 * SR))   # début et fin en douceur (pas de coupure nette entre deux scènes)
    if fondu: r = np.linspace(0, 1, fondu); out[:fondu] *= r; out[-fondu:] *= r[::-1]
    return (out / (np.abs(out).max() + 1e-9) * 0.5).astype(np.float32)

if __name__ == '__main__':   # python studio/ambiances.py sortie.wav [secondes]
    import sys, soundfile as sf
    sf.write(sys.argv[1], grillons(float(sys.argv[2]) if len(sys.argv) > 2 else 20), SR)
