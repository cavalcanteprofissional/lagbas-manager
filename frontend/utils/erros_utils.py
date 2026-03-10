# Utility functions for error handling
def formatar_erro_supabase(error_str, operacao="operacao"):
    """Converte erros técnicos do Supabase em mensagens amigáveis."""
    
    error_lower = error_str.lower()
    
    if "42501" in error_str or "row-level security" in error_lower or "new row violates row-level" in error_lower:
        return "Você não tem permissão para realizar esta operação. Faça login novamente."
    
    if "23505" in error_str or "duplicate key" in error_lower:
        return "Este registro já existe no sistema."
    
    if "23503" in error_str or "foreign key" in error_lower:
        return "Registro não encontrado ou vinculado a outros dados."
    
    if "P0001" in error_str:
        return "Erro no banco de dados. Tente novamente."
    
    if "connection" in error_lower or "timeout" in error_lower:
        return "Erro de conexão. Verifique sua internet e tente novamente."
    
    if "auth" in error_lower or "unauthorized" in error_lower or "token" in error_lower:
        return "Sessão expirada. Faça login novamente."
    
    return f"Erro ao {operacao}. Tente novamente."
