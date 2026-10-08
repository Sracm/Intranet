-- ============================================================================
-- TABELA DE GOVERNANÇA: Acessos_Usuario_CR
-- Controla os Centros de Resultado permitidos para cada Gestor
-- ============================================================================

CREATE TABLE IF NOT EXISTS Acessos_Usuario_CR (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(100) NOT NULL COMMENT 'Username do gestor (ex: vinicius.resina)',
    codcencus INT NOT NULL COMMENT 'Código numérico do centro de resultado (ex: 24000000)',
    centro_resultado VARCHAR(255) NOT NULL COMMENT 'Descrição completa do centro',
    canal VARCHAR(100) NOT NULL COMMENT 'Canal de responsabilidade do gestor',
    ativo TINYINT(1) DEFAULT 1 COMMENT '1 = Ativo, 0 = Inativo',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_usuario_cr (usuario, codcencus),
    INDEX idx_usuario (usuario),
    INDEX idx_codcencus (codcencus),
    INDEX idx_canal (canal)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
