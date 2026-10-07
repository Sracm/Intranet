-- =========================================================================
-- TABELA DE RELACIONAMENTO: USUÁRIOS DA INTRANET E CENTROS DE CUSTO PERMITIDOS
-- Compatível com MariaDB (produção Linux) e SQLite (desenvolvimento local)
-- =========================================================================

CREATE TABLE IF NOT EXISTS user_cost_centers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    codcencus INT NOT NULL,
    descricao_centro VARCHAR(255),
    canal VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_user_cc (user_id, codcencus),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Índice para consultas ultra-rápidas O(1) pelo ID do usuário logado
CREATE INDEX idx_user_cc_userid ON user_cost_centers (user_id);
