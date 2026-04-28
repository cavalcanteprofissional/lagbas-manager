-- =====================================================
-- SCHEMA DO BANCO DE DADOS - LabGas Manager
-- Supabase (PostgreSQL)
-- =====================================================

-- Tabela: cilindro
-- Armazena informações sobre os cilindro de gás
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

-- Tabela: elemento
-- Armazena os elementos analisados no laboratório
CREATE TABLE elemento (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    consumo_lpm DECIMAL(5,2) NOT NULL,
    user_id UUID REFERENCES auth.users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabela: amostra
-- Armazena os registros de análises realizadas
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

-- Tabela: perfil
-- Armazena informações adicionais do usuário
CREATE TABLE perfil (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    role VARCHAR(20) DEFAULT 'usuario' CHECK (role IN ('admin', 'usuario')),
    ativo BOOLEAN DEFAULT true,
    nome VARCHAR(100),
    email VARCHAR(255),
    habilitar_abas JSONB DEFAULT '{"cilindro": false, "elemento": false, "amostra": false, "historico": false}',
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela: pressao
-- Armazena registros de pressão dos cilindro
CREATE TABLE pressao (
    id SERIAL PRIMARY KEY,
    cilindro_id INTEGER REFERENCES cilindro(id),
    pressao NUMERIC NOT NULL,
    temperatura NUMERIC,
    data DATE NOT NULL,
    hora TIME NOT NULL,
    user_id UUID REFERENCES auth.users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabela: historico_log
-- Registra todas as operações do sistema
CREATE TABLE historico_log (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(20) NOT NULL,
    acao VARCHAR(20) NOT NULL,
    nome VARCHAR(100) NOT NULL,
    user_id UUID REFERENCES auth.users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- ÍNDICES
-- =====================================================

CREATE INDEX idx_cilindro_user_id ON cilindro(user_id);
CREATE INDEX idx_cilindro_codigo ON cilindro(codigo);
CREATE INDEX idx_elemento_user_id ON elemento(user_id);
CREATE INDEX idx_elemento_nome ON elemento(nome);
CREATE INDEX idx_amostra_user_id ON amostra(user_id);
CREATE INDEX idx_amostra_cilindro_id ON amostra(cilindro_id);
CREATE INDEX idx_amostra_elemento_id ON amostra(elemento_id);
CREATE INDEX idx_amostra_data ON amostra(data);
CREATE INDEX idx_perfil_id ON perfil(id);
CREATE INDEX idx_perfil_role ON perfil(role);
CREATE INDEX idx_pressao_user_id ON pressao(user_id);
CREATE INDEX idx_pressao_cilindro_id ON pressao(cilindro_id);
CREATE INDEX idx_pressao_data ON pressao(data);
CREATE INDEX idx_historico_log_user_id ON historico_log(user_id);
CREATE INDEX idx_historico_log_tipo ON historico_log(tipo);
CREATE INDEX idx_historico_log_created_at ON historico_log(created_at);
