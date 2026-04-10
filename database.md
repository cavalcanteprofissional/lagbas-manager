-- ============================================
-- SCHEMA DO BANCO DE DADOS - LabGas Manager
-- ============================================

-- ============================================
-- TABELAS PRINCIPAIS
-- ============================================

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

-- Tabela de Perfil (gerenciamento de usuários)
CREATE TABLE perfil (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    role VARCHAR(20) DEFAULT 'usuario' CHECK (role IN ('admin', 'usuario')),
    ativo BOOLEAN DEFAULT true,
    nome VARCHAR(100),
    email VARCHAR(255),
    habilitar_abas JSONB DEFAULT '{"cilindro": true, "elemento": true, "amostra": true, "historico": true, "temperatura": true}',
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de Log de Histórico
CREATE TABLE historico_log (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(20) NOT NULL,
    acao VARCHAR(20) NOT NULL,
    nome VARCHAR(100) NOT NULL,
    user_id UUID REFERENCES auth.users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabela de Temperatura (v1.9.0)
CREATE TABLE temperatura (
    id SERIAL PRIMARY KEY,
    cilindro_id INTEGER REFERENCES cilindro(id),
    temperatura DECIMAL(5,2) NOT NULL,
    data DATE NOT NULL,
    hora TIME NOT NULL,
    user_id UUID REFERENCES auth.users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- ÍNDICES
-- ============================================

-- Índices únicos por usuário
CREATE UNIQUE INDEX idx_cilindro_codigo_user ON cilindro(user_id, codigo);
CREATE UNIQUE INDEX idx_elemento_nome_user ON elemento(user_id, nome);

-- Índices para campos adicionais
CREATE INDEX idx_perfil_role ON perfil(role);
CREATE INDEX idx_perfil_ativo ON perfil(ativo);
CREATE INDEX idx_temperatura_cilindro ON temperatura(cilindro_id);
CREATE INDEX idx_temperatura_user ON temperatura(user_id);

-- ============================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================

-- Habilitar RLS em todas as tabelas
ALTER TABLE cilindro ENABLE ROW LEVEL SECURITY;
ALTER TABLE elemento ENABLE ROW LEVEL SECURITY;
ALTER TABLE amostra ENABLE ROW LEVEL SECURITY;
ALTER TABLE perfil ENABLE ROW LEVEL SECURITY;
ALTER TABLE historico_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE temperatura ENABLE ROW LEVEL SECURITY;

-- ============================================
-- POLÍTICAS RLS - Cilindro
-- ============================================

DROP POLICY IF EXISTS "Anyone can view cilindro" ON cilindro;
DROP POLICY IF EXISTS "Users can insert cilindro" ON cilindro;
DROP POLICY IF EXISTS "Users can update cilindro" ON cilindro;
DROP POLICY IF EXISTS "Users can delete cilindro" ON cilindro;

CREATE POLICY "Anyone can view cilindro" ON cilindro
    FOR SELECT USING (true);

CREATE POLICY "Users can insert cilindro" ON cilindro
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update cilindro" ON cilindro
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete cilindro" ON cilindro
    FOR DELETE USING (auth.uid() = user_id);

-- ============================================
-- POLÍTICAS RLS - Elemento
-- ============================================

DROP POLICY IF EXISTS "Anyone can view elemento" ON elemento;
DROP POLICY IF EXISTS "Users can insert elemento" ON elemento;
DROP POLICY IF EXISTS "Users can update elemento" ON elemento;
DROP POLICY IF EXISTS "Users can delete elemento" ON elemento;

CREATE POLICY "Anyone can view elemento" ON elemento
    FOR SELECT USING (true);

CREATE POLICY "Users can insert elemento" ON elemento
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update elemento" ON elemento
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete elemento" ON elemento
    FOR DELETE USING (auth.uid() = user_id);

-- ============================================
-- POLÍTICAS RLS - Amostra
-- ============================================

DROP POLICY IF EXISTS "Anyone can view amostra" ON amostra;
DROP POLICY IF EXISTS "Users can insert amostra" ON amostra;
DROP POLICY IF EXISTS "Users can update amostra" ON amostra;
DROP POLICY IF EXISTS "Users can delete amostra" ON amostra;

CREATE POLICY "Anyone can view amostra" ON amostra
    FOR SELECT USING (true);

CREATE POLICY "Users can insert amostra" ON amostra
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update amostra" ON amostra
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete amostra" ON amostra
    FOR DELETE USING (auth.uid() = user_id);

-- ============================================
-- POLÍTICAS RLS - Perfil
-- ============================================

DROP POLICY IF EXISTS "Users can view own perfil" ON perfil;
DROP POLICY IF EXISTS "Users can update own perfil" ON perfil;
DROP POLICY IF EXISTS "Admins can manage all perfil" ON perfil;

CREATE POLICY "Users can view own perfil" ON perfil
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can insert own perfil" ON perfil
    FOR INSERT WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can update own perfil" ON perfil
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Admins can manage all perfil" ON perfil
    FOR ALL USING (
        EXISTS (SELECT 1 FROM perfil WHERE id = auth.uid() AND role = 'admin')
    );

-- ============================================
-- POLÍTICAS RLS - Historico Log
-- ============================================

DROP POLICY IF EXISTS "Users can view historico_log" ON historico_log;

CREATE POLICY "Users can view historico_log" ON historico_log
    FOR SELECT USING (true);

-- ============================================
-- POLÍTICAS RLS - Temperatura (v1.9.0)
-- ============================================

DROP POLICY IF EXISTS "Anyone can view temperatura" ON temperatura;
DROP POLICY IF EXISTS "Users can insert temperatura" ON temperatura;
DROP POLICY IF EXISTS "Users can update temperatura" ON temperatura;
DROP POLICY IF EXISTS "Users can delete temperatura" ON temperatura;

CREATE POLICY "Anyone can view temperatura" ON temperatura
    FOR SELECT USING (true);

CREATE POLICY "Users can insert temperatura" ON temperatura
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update temperatura" ON temperatura
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete temperatura" ON temperatura
    FOR DELETE USING (auth.uid() = user_id);

-- ============================================
-- CRIAR PRIMEIRO ADMIN
-- ============================================
-- Substitua pelo email desejado para criar o primeiro admin

INSERT INTO perfil (id, role, ativo)
SELECT id, 'admin', true 
FROM auth.users 
WHERE email = 'seu-email@exemplo.com'
ON CONFLICT (id) DO UPDATE SET role = 'admin', ativo = true;

-- ============================================
-- CRIAR PERFIS PARA USUARIOS EXISTENTES
-- ============================================

INSERT INTO perfil (id, role, ativo, nome, email)
SELECT 
    u.id,
    'usuario',
    true,
    COALESCE(u.raw_user_meta_data->>'nome', ''),
    u.email
FROM auth.users u
LEFT JOIN perfil p ON u.id = p.id
WHERE p.id IS NULL;
