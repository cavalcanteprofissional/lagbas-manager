-- Tabela de Cilindros
CREATE TABLE cilindro (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) NOT NULL,
    data_compra DATE NOT NULL,
    data_inicio_consumo DATE,
    data_fim DATE,
    gas_kg DECIMAL(5,2) DEFAULT 1.0,
    litros_equivalentes DECIMAL(10,2) DEFAULT 956.0,
    custo DECIMAL(10,2) DEFAULT 290.00,
    status VARCHAR(20) DEFAULT 'ativo',
    user_id UUID REFERENCES auth.users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabela de Elementos
CREATE TABLE elemento (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    consumo_lpm DECIMAL(5,2) NOT NULL,
    user_id UUID REFERENCES auth.users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabela de Amostras
CREATE TABLE amostra (
    id SERIAL PRIMARY KEY,
    data DATE NOT NULL,
    tempo_chama VARCHAR(8) NOT NULL,
    cilindro_id INTEGER REFERENCES cilindro(id),
    elemento_id INTEGER REFERENCES elemento(id),
    quantidade_amostras INTEGER DEFAULT 1,
    user_id UUID REFERENCES auth.users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Habilitar Row Level Security (RLS)
ALTER TABLE cilindro ENABLE ROW LEVEL SECURITY;
ALTER TABLE elemento ENABLE ROW LEVEL SECURITY;
ALTER TABLE amostra ENABLE ROW LEVEL SECURITY;

-- Índices únicos por usuário
CREATE UNIQUE INDEX idx_cilindro_codigo_user ON cilindro(user_id, codigo);
CREATE UNIQUE INDEX idx_elemento_nome_user ON elemento(user_id, nome);

-- Políticas RLS para permitir acesso apenas aos dados do usuário
CREATE POLICY "Users can manage their cilindro" ON cilindro
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can manage their elemento" ON elemento
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can manage their amostra" ON amostra
    FOR ALL USING (auth.uid() = user_id);
