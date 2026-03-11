-- Script SQL para implementar sistema de admin e compartilhamento

-- ============================================
-- TABELA PERFIL (gerenciamento de usuários)
-- ============================================
CREATE TABLE IF NOT EXISTS perfil (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    role VARCHAR(20) DEFAULT 'usuario' CHECK (role IN ('admin', 'usuario')),
    ativo BOOLEAN DEFAULT true,
    nome VARCHAR(100),
    email VARCHAR(255),
    habilitar_abas JSONB DEFAULT '{"cilindro": true, "elemento": true, "amostra": true, "historico": true}',
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- HABILITAR RLS
-- ============================================
ALTER TABLE perfil ENABLE ROW LEVEL SECURITY;

-- ============================================
-- POLICIES RLS
-- ============================================

-- Policy: Usuários podem ver seu próprio perfil
CREATE POLICY "Users can view own perfil" ON perfil
    FOR SELECT USING (auth.uid() = id);

-- Policy: Usuários podem atualizar seu próprio perfil
CREATE POLICY "Users can update own perfil" ON perfil
    FOR UPDATE USING (auth.uid() = id);

-- Policy: Admins podem fazer tudo no perfil
CREATE POLICY "Admins can manage all perfil" ON perfil
    FOR ALL USING (
        EXISTS (SELECT 1 FROM perfil WHERE id = auth.uid() AND role = 'admin')
    );

-- ============================================
-- ÍNDICES
-- ============================================
CREATE INDEX IF NOT EXISTS idx_perfil_role ON perfil(role);
CREATE INDEX IF NOT EXISTS idx_perfil_ativo ON perfil(ativo);

-- ============================================
-- CRIAR PRIMEIRO ADMIN
-- ============================================
-- Transforma o usuário tsandre967@gmail.com em admin
INSERT INTO perfil (id, role, ativo)
SELECT id, 'admin', true 
FROM auth.users 
WHERE email = 'tsandre967@gmail.com'
ON CONFLICT (id) DO UPDATE SET role = 'admin', ativo = true;
