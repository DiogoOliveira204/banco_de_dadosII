
import random
from datetime import date, timedelta
from faker import Faker
import mysql.connector

# ===== Config do banco =====
DB = {
    "host": "localhost",
    "user": "root",
    "password": "",     
    "database": "MuseuDB",
}

QTD = 1000     
QTD_EXPO = 200  
QTD_EVENTO = 200 
BATCH = 500 

fake = Faker("pt_BR")
Faker.seed(42)
random.seed(42)

comentarios_pt = [
    "Obra muito interessante, adorei o uso das cores.",
    "A técnica utilizada é incrível, transmite muita emoção.",
    "Achei a composição um pouco confusa, mas criativa.",
    "Excelente trabalho, dá vontade de ver pessoalmente.",
    "Não me conectei muito com a proposta da obra.",
    "Sensacional! A iluminação e textura estão impecáveis.",
    "Gostei da mistura de estilos, algo bem contemporâneo.",
    "A artista conseguiu passar uma mensagem profunda.",
    "O uso das sombras é marcante, cria uma boa atmosfera.",
    "É uma obra que faz pensar, bem conceitual."
]

descricoes_pt = [
    "Obra produzida com tinta acrílica sobre tela, em tons suaves e harmônicos.",
    "Escultura em bronze representando a figura humana em movimento.",
    "Instalação composta por luzes e sons que exploram a percepção sensorial.",
    "Pintura abstrata inspirada nas paisagens do litoral brasileiro.",
    "Obra digital desenvolvida em software 3D, com temática urbana.",
    "Colagem feita com materiais recicláveis, simbolizando sustentabilidade.",
    "Gravura em metal retratando cenas do cotidiano.",
    "Fotografia em preto e branco que destaca a solidão moderna.",
    "Painel em mosaico colorido com influências do modernismo.",
    "Série experimental que combina técnicas tradicionais e digitais."
]

temas_expo = [
    "Arte e Cidade", "Luz e Sombra", "Memória Coletiva", "Formas do Tempo",
    "Contrastes do Cotidiano", "Cores do Brasil", "Expressões do Corpo",
    "Paisagens Imaginárias", "Sons e Imagens", "Tecnologia e Sensibilidade"
]

# ===== Helpers =====
def chunked(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i+n]

def ano_criacao():
    return random.randint(1901, 2024)  # YEAR válido

def titulo_obra():
    tecnicas = ["Série", "Estudo", "Composição", "Paisagem", "Retrato", "Abstrato", "Instalação", "Escultura"]
    temas = ["da Cidade", "da Noite", "de Luz", "de Sombras", "da Memória", "do Mar", "da Montanha", "do Silêncio"]
    return f"{random.choice(tecnicas)} {random.choice(temas)}"

def descricao_curta():
    return random.choice(descricoes_pt)

def inserir(cur, conn, sql, dados):
    total = 0
    for lote in chunked(dados, BATCH):
        cur.executemany(sql, lote)
        conn.commit()
        total += cur.rowcount
    return total

def table_exists(cur, schema, name):
    cur.execute(
        "SELECT COUNT(*) FROM information_schema.tables "
        "WHERE table_schema=%s AND table_name=%s",
        (schema, name)
    )
    return cur.fetchone()[0] == 1

def get_columns(cur, schema, name):
    cur.execute(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_schema=%s AND table_name=%s",
        (schema, name)
    )
    return {r[0] for r in cur.fetchall()}

def main():
    conn = mysql.connector.connect(**DB)
    cur = conn.cursor()

    print("🚀 Iniciando população de dados...")

    # ==========================
    # USUÁRIOS (e-mails únicos)
    # ==========================
    print("👤 Inserindo usuários...")
    usuarios = []
    for _ in range(QTD):
        usuarios.append((
            fake.name(),
            fake.unique.email(),            # garante unicidade no lote
            fake.sha256(),                  # hash fictício
            random.choice(["comum", "curador", "admin"])
        ))
    n = inserir(cur, conn,
        "INSERT INTO Usuario (nome, email, senha, tipo) VALUES (%s,%s,%s,%s)",
        usuarios
    )
    print(f"   → {n} usuários")

    # ==========================
    # AUTORES (datas coerentes)
    # ==========================
    print("🖋 Inserindo autores...")
    autores = []
    for _ in range(QTD):
        dnasc = fake.date_of_birth(minimum_age=40, maximum_age=90)
        if random.random() < 0.7:
            dfal = None
        else:
            dfal = dnasc + timedelta(days=random.randint(365*40, 365*90))
            if dfal > date.today():
                dfal = date.today()
        autores.append((
            fake.unique.name(),                 # nome único no lote
            random.choice(descricoes_pt),       # bio curta em PT-BR
            dnasc,
            dfal
        ))
    n = inserir(cur, conn,
        "INSERT INTO Autor (nome, biografia, data_nascimento, data_falecimento) VALUES (%s,%s,%s,%s)",
        autores
    )
    print(f"   → {n} autores")

    # ==========================
    # TIPOS (evita duplicar contra o que já existe)
    # ==========================
    print("🏷 Inserindo tipos (sem duplicar existentes)...")
    cur.execute("SELECT nome FROM Tipo")
    tipos_existentes = {row[0] for row in cur.fetchall()}

    seed_tipos = [
        "Pintura", "Escultura", "Fotografia", "Gravura", "Instalação", "Vídeo",
        "Áudio", "Documento", "Tapeçaria", "Cerâmica", "Desenho", "Arte Digital",
        "Colagem", "Performance", "Mídia Mista", "Vitral", "Aquarela", "Acrílica",
        "Óleo", "Metais"
    ]
    tipos_a_inserir = []
    for nome in seed_tipos:
        if len(tipos_a_inserir) >= 20:
            break
        if nome not in tipos_existentes:
            tipos_a_inserir.append((nome,))
            tipos_existentes.add(nome)

    i = 1
    while len(tipos_a_inserir) < 20:
        nome = f"Tipo {i:04d}"
        if nome not in tipos_existentes:
            tipos_a_inserir.append((nome,))
            tipos_existentes.add(nome)
        i += 1

    n = inserir(cur, conn, "INSERT INTO Tipo (nome) VALUES (%s)", tipos_a_inserir)
    print(f"   → {n} tipos")

    # ==========================
    # ESTILOS (evita duplicar existentes)
    # ==========================
    print("🎨 Inserindo estilos (sem duplicar existentes)...")
    cur.execute("SELECT nome FROM Estilo")
    estilos_existentes = {row[0] for row in cur.fetchall()}

    estilos_base = [
        "Modernismo", "Barroco", "Expressionismo", "Cubismo",
        "Surrealismo", "Realismo", "Abstrato", "Pop Art",
        "Minimalismo", "Futurismo"
    ]
    estilos_a_inserir = []
    for nome in estilos_base:
        if nome not in estilos_existentes:
            estilos_a_inserir.append((nome,))
            estilos_existentes.add(nome)

    n = 0
    if estilos_a_inserir:
        n = inserir(cur, conn, "INSERT INTO Estilo (nome) VALUES (%s)", estilos_a_inserir)
    print(f"   → +{n} estilos (novos) / total agora: {len(estilos_existentes)}")

    # totais reais para FKs
    cur.execute("SELECT COUNT(*) FROM Estilo")
    total_estilos = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM Tipo")
    total_tipos = cur.fetchone()[0]

    # ==========================
    # OBRAS (PT-BR)
    # ==========================
    print("🖼 Inserindo obras...")
    obras = [(titulo_obra(), descricao_curta(), ano_criacao()) for _ in range(QTD)]
    n = inserir(cur, conn, "INSERT INTO Obra (titulo, descricao, ano_criacao) VALUES (%s,%s,%s)", obras)
    print(f"   → {n} obras")

    # ==========================
    # EXPOSIÇÕES (CHECK: data_fim >= data_inicio OU NULL) — descrições PT-BR
    # ==========================
    print("🏛 Inserindo exposições...")
    exposicoes = []
    today = date.today()
    for _ in range(QTD_EXPO):
        di = today - timedelta(days=random.randint(0, 3650))  # até 10 anos atrás
        df = None if random.random() < 0.25 else di + timedelta(days=random.randint(0, 365*3))
        titulo_expo = f"Exposição {random.choice(temas_expo)}"
        desc_expo = random.choice(descricoes_pt)
        exposicoes.append((titulo_expo, desc_expo, di, df))
    n = inserir(cur, conn,
        "INSERT INTO Exposicao (titulo, descricao, data_inicio, data_fim) VALUES (%s,%s,%s,%s)",
        exposicoes
    )
    print(f"   → {n} exposições")

    # ==========================
    # EVENTOS (PT-BR)
    # ==========================
    print("📅 Inserindo eventos...")
    eventos = []
    for _ in range(QTD_EVENTO):
        de = today - timedelta(days=random.randint(0, 365*5))
        titulo_evento = f"Evento {random.choice(temas_expo)}"
        desc_evento = random.choice(descricoes_pt)
        eventos.append((titulo_evento, desc_evento, de))
    n = inserir(cur, conn,
        "INSERT INTO Evento (titulo, descricao, data_evento) VALUES (%s,%s,%s)",
        eventos
    )
    print(f"   → {n} eventos")

    # ==========================
    # RELAÇÕES M:N (INSERT IGNORE para não quebrar UNIQUE)
    # ==========================
    print("🔗 Inserindo relações...")

    # Obra_has_Autor
    pares = set()
    while len(pares) < QTD:
        pares.add((random.randint(1, QTD), random.randint(1, QTD)))
    n = inserir(cur, conn,
        "INSERT IGNORE INTO Obra_has_Autor (Obra_id_obra, Autor_id_autor) VALUES (%s,%s)",
        list(pares)
    )
    print(f"   → {n} Obra_has_Autor")

    # Obra_has_Exposicao
    pares = set()
    while len(pares) < QTD:
        pares.add((random.randint(1, QTD), random.randint(1, QTD_EXPO)))
    n = inserir(cur, conn,
        "INSERT IGNORE INTO Obra_has_Exposicao (Obra_id_obra, Exposicao_id_exposicao) VALUES (%s,%s)",
        list(pares)
    )
    print(f"   → {n} Obra_has_Exposicao")

    # Obra_has_Estilo
    pares = set()
    while len(pares) < QTD:
        pares.add((random.randint(1, QTD), random.randint(1, total_estilos)))
    n = inserir(cur, conn,
        "INSERT IGNORE INTO Obra_has_Estilo (Obra_id_obra, Estilo_id_estilo) VALUES (%s,%s)",
        list(pares)
    )
    print(f"   → {n} Obra_has_Estilo")

    # Estilo_has_Tipo
    pares = set()
    alvo = 50 if total_estilos > 0 and total_tipos > 0 else 0
    while len(pares) < alvo:
        pares.add((random.randint(1, total_estilos), random.randint(1, total_tipos)))
    n = 0
    if pares:
        n = inserir(cur, conn,
            "INSERT IGNORE INTO Estilo_has_Tipo (Estilo_id_estilo, Tipo_id_tipo) VALUES (%s,%s)",
            list(pares)
        )
    print(f"   → {n} Estilo_has_Tipo")

    # Exposicao_has_Evento
    pares = set()
    while len(pares) < QTD_EVENTO:
        pares.add((random.randint(1, QTD_EXPO), random.randint(1, QTD_EVENTO)))
    n = inserir(cur, conn,
        "INSERT IGNORE INTO Exposicao_has_Evento (Exposicao_id_exposicao, Evento_id_evento) VALUES (%s,%s)",
        list(pares)
    )
    print(f"   → {n} Exposicao_has_Evento")

    # ==========================
    # MÍDIA (FK para Obra)
    # ==========================
    print("📸 Inserindo mídias...")
    exts = {"imagem": "jpg", "video": "mp4", "audio": "mp3", "documento": "pdf"}
    midias = []
    for _ in range(QTD):
        t = random.choice(list(exts.keys()))
        url = f"https://example.com/{fake.uuid4()}.{exts[t]}"
        obra_id = random.randint(1, QTD)
        midias.append((t, url, obra_id))
    n = inserir(cur, conn,
        "INSERT INTO Midia (tipo, url_arquivo, Obra_id_obra) VALUES (%s,%s,%s)",
        midias
    )
    print(f"   → {n} mídias")

    # ==========================
    # AVALIAÇÃO (pares únicos Obra x Usuario) – comentários PT-BR
    # ==========================
    print("⭐ Inserindo avaliações...")
    pares = set()
    while len(pares) < QTD:
        pares.add((random.randint(1, QTD), random.randint(1, QTD)))  # (obra, usuario)
    avaliacoes = []
    for (obra_id, user_id) in pares:
        nota = random.randint(0, 5)  # CHECK 0..5
        comentario = random.choice(comentarios_pt)
        data_av = date.today() - timedelta(days=random.randint(0, 365*3))
        avaliacoes.append((nota, comentario, data_av, obra_id, user_id))
    n = inserir(cur, conn,
        "INSERT INTO Avaliacao (nota, comentario, data, Obra_id_obra, Usuario_id_usuario) VALUES (%s,%s,%s,%s,%s)",
        avaliacoes
    )
    print(f"   → {n} avaliações")

    # ==========================
    # FAVORITOS (detecta 'favorito' ou 'favorita' e estrutura)
    # ==========================
    print("❤️ Inserindo favoritos...")

    tbl = "favorito" if table_exists(cur, DB["database"], "favorito") else (
          "favorita" if table_exists(cur, DB["database"], "favorita") else None)

    if not tbl:
        print("   ⚠️ Nenhuma tabela de favoritos encontrada ('favorito'/'favorita'). Pulando etapa.")
    else:
        cols = get_columns(cur, DB["database"], tbl)

        # gera pares únicos (Usuario, Obra)
        pares = set()
        while len(pares) < QTD:
            pares.add((random.randint(1, QTD), random.randint(1, QTD)))  # (Usuario, Obra)

        if {"Usuario_id_usuario", "Obra_id_obra"}.issubset(cols) and (
            "idfavorito" in cols or "idfavoritas" in cols or "id_favorito" in cols
        ):
            # 3 colunas com ID explícito
            idcol = "idfavorito" if "idfavorito" in cols else ("idfavoritas" if "idfavoritas" in cols else "id_favorito")
            favoritos3 = []
            for i, (uid, oid) in enumerate(pares, start=1):
                favoritos3.append((i, uid, oid))
            n = inserir(
                cur, conn,
                f"INSERT IGNORE INTO {tbl} ({idcol}, Usuario_id_usuario, Obra_id_obra) VALUES (%s,%s,%s)",
                favoritos3
            )
            print(f"   → {n} favoritos ({tbl} com 3 colunas)")
        elif {"Usuario_id_usuario", "Obra_id_obra"}.issubset(cols):
            # 2 colunas (PK composta)
            favoritos2 = list(pares)
            n = inserir(
                cur, conn,
                f"INSERT IGNORE INTO {tbl} (Usuario_id_usuario, Obra_id_obra) VALUES (%s,%s)",
                favoritos2
            )
            print(f"   → {n} favoritos ({tbl} com 2 colunas)")
        else:
            print(f"   ⚠️ Estrutura inesperada da tabela '{tbl}': colunas = {sorted(cols)}. Etapa pulada.")

    print("🎉 População concluída com sucesso!")

    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
