import time
import pulp
import pandas as pd
import matplotlib.pyplot as plt

# Definição das instâncias
INSTANCIAS = {
    "Grafo C6": (list(range(1, 7)),
                 [(1,2),(2,3),(3,4),(4,5),(5,6),(6,1)]),
    "Grafo Estrela": (list(range(1, 8)),
                      [(1,2),(1,3),(1,4),(1,5),(1,6),(1,7)]),
    "Grafo Aleatorio G(10, 0.3), seed 42": (list(range(1, 11)),
        [(1,3),(1,4),(1,5),(1,9),(2,3),(2,4),(2,6),(2,7),(2,10),
         (3,6),(3,10),(4,7),(4,8),(7,10),(8,9),(8,10),(9,10)]),
}

def guloso(V, E):
    vizinhos = {v: set() for v in V}
    for a, b in E:
        vizinhos[a].add(b)
        vizinhos[b].add(a)
    S = []
    for v in V:                      
        if not (vizinhos[v] & set(S)):   
            S.append(v)
    return S

def eh_independente(S, E):
    return all(not (a in S and b in S) for a, b in E)

def medir(f, *args):                 
    t0 = time.perf_counter()
    r = f(*args)
    return r, (time.perf_counter() - t0) * 1000

def exato_pli(V, E):
    modelo = pulp.LpProblem("indep_max", pulp.LpMaximize)
    x = {v: pulp.LpVariable(f"x{v}", cat="Binary") for v in V}
    
    # Função objetivo: maximizar a soma de todas as variáveis
    modelo += pulp.lpSum([x[v] for v in V])
    
    # Restrição: para cada aresta, no máximo 1 vértice pode ser escolhido
    for i, j in E:
        modelo += x[i] + x[j] <= 1
        
    modelo.solve(pulp.PULP_CBC_CMD(msg=False))
    return [v for v in V if x[v].value() > 0.5]

# Executar medições 3 vezes e calcular médias
resultados = []

for nome, (V, E) in INSTANCIAS.items():
    tempos_guloso = []
    tempos_exato = []
    
    # Rodar 3 vezes
    for _ in range(3):
        Sg, tg = medir(guloso, V, E)
        Se, te = medir(exato_pli, V, E)
        tempos_guloso.append(tg)
        tempos_exato.append(te)
        
    media_tg = sum(tempos_guloso) / 3
    media_te = sum(tempos_exato) / 3
    
    assert eh_independente(Sg, E) and eh_independente(Se, E)
    
    resultados.append({
        "Instância": nome,
        "Z Guloso": len(Sg),
        "Z Exato": len(Se),
        "Tempo Médio Guloso (ms)": round(media_tg, 4),
        "Tempo Médio Exato (ms)": round(media_te, 4)
    })

# Converter para DataFrame para gerar a tabela formatada
df_resultados = pd.DataFrame(resultados)
display(df_resultados)

# --- GERAR GRÁFICOS ---

# Gráfico 1: Comparação do Tamanho Z (Ótimo vs Guloso)
plt.figure(figsize=(8, 5))
df_resultados.plot(x="Instância", y=["Z Guloso", "Z Exato"], kind="bar", color=["#FFA500", "#4682B4"])
plt.title("Comparação: Tamanho do Conjunto Independente (Z)")
plt.ylabel("Número de Barracas (Z)")
plt.xticks(rotation=15)
plt.legend(["Heurística Gulosa", "Exato PLI"])
plt.tight_layout()
plt.show()

# Gráfico 2: Comparação de Tempo de Execução (Escala Logarítmica por causa da diferença de tempo)
plt.figure(figsize=(8, 5))
df_resultados.plot(x="Instância", y=["Tempo Médio Guloso (ms)", "Tempo Médio Exato (ms)"], kind="bar", logy=True, color=["#FF6347", "#32CD32"])
plt.title("Comparação: Tempo de Execução (Escala Logarítmica)")
plt.ylabel("Tempo (ms)")
plt.xticks(rotation=15)
plt.legend(["Guloso (ms)", "Exato (ms)"])
plt.tight_layout()
plt.show()
