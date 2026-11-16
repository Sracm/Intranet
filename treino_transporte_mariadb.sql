-- ==============================================================================
-- BASE DE DADOS: treina
-- TABELA: transporte
-- OBJETIVO: Simulação de dados de frota rodoviária / urbana para testes de SQL
-- ==============================================================================

USE treina;

-- 1. ESTRUTURA DA TABELA CRIADA NO MARIADB:
/*
DESCRIBE transporte;
+--------------------------+---------------+------+-----+---------+----------------+
| Field                    | Type          | Null | Key | Default | Extra          |
+--------------------------+---------------+------+-----+---------+----------------+
| id                       | int(11)       | NO   | PRI | NULL    | auto_increment |
| veiculo_id               | int(11)       | NO   | MUL | NULL    |                |
| placa                    | varchar(10)   | NO   |     | NULL    |                |
| modelo                   | varchar(50)   | NO   |     | NULL    |                |
| tipo_veiculo             | varchar(30)   | YES  |     | NULL    |                |
| linha                    | varchar(100)  | YES  |     | NULL    |                |
| origem                   | varchar(50)   | NO   |     | NULL    |                |
| destino                  | varchar(50)   | NO   |     | NULL    |                |
| data_viagem              | date          | NO   | MUL | NULL    |                |
| distancia_km             | decimal(10,2) | NO   | MUL | NULL    |                |
| litros_combustivel       | decimal(10,2) | NO   |     | NULL    |                |
| capacidade_ofertada      | int(11)       | NO   |     | NULL    |                |
| passageiros_transportados| int(11)       | NO   |     | NULL    |                |
| receita_total            | decimal(10,2) | NO   |     | NULL    |                |
| custo_manutencao         | decimal(10,2) | YES  |     | 0.00    |                |
| motorista_nome           | varchar(100)  | YES  |     | NULL    |                |
| atraso_minutos           | int(11)       | YES  |     | 0       |                |
| status_viagem            | varchar(20)   | YES  |     | CONCLUIDA |              |
+--------------------------+---------------+------+-----+---------+----------------+
*/

-- ==============================================================================
-- QUERY 1: 5 VEÍCULOS COM PIOR MÉDIA DE CONSUMO (ÚLTIMOS 30 DIAS, VIAGENS >= 50 KM)
-- ==============================================================================
SELECT 
    veiculo_id,
    placa,
    modelo,
    ROUND(SUM(distancia_km), 1) AS total_km,
    ROUND(SUM(litros_combustivel), 1) AS total_litros,
    ROUND(SUM(distancia_km) / SUM(litros_combustivel), 2) AS km_por_litro
FROM transporte
WHERE data_viagem >= CURDATE() - INTERVAL 30 DAY
  AND distancia_km >= 50
GROUP BY veiculo_id, placa, modelo
ORDER BY km_por_litro ASC
LIMIT 5;

-- ==============================================================================
-- QUERY 2: LINHAS COM BAIXA TAXA DE OCUPAÇÃO (< 60%) NOS ÚLTIMOS 30 DIAS
-- ==============================================================================
SELECT 
    linha,
    COUNT(*) AS total_viagens,
    SUM(passageiros_transportados) AS passageiros_totais,
    SUM(capacidade_ofertada) AS capacidade_total,
    ROUND((SUM(passageiros_transportados) / SUM(capacidade_ofertada)) * 100, 2) AS taxa_ocupacao_pct
FROM transporte
WHERE data_viagem >= CURDATE() - INTERVAL 30 DAY
GROUP BY linha
HAVING taxa_ocupacao_pct < 60
ORDER BY taxa_ocupacao_pct ASC;

-- ==============================================================================
-- QUERY 3: CUSTO DE MANUTENÇÃO POR KM (CPK) POR MODELO DE VEÍCULO
-- ==============================================================================
SELECT 
    modelo,
    tipo_veiculo,
    COUNT(DISTINCT veiculo_id) AS qtd_veiculos,
    ROUND(SUM(distancia_km), 1) AS km_rodados,
    ROUND(SUM(custo_manutencao), 2) AS custo_manutencao_total,
    ROUND(SUM(custo_manutencao) / SUM(distancia_km), 4) AS cpk_manutencao
FROM transporte
WHERE data_viagem >= CURDATE() - INTERVAL 30 DAY
GROUP BY modelo, tipo_veiculo
ORDER BY cpk_manutencao DESC;

-- ==============================================================================
-- QUERY 4: ÍNDICE DE PONTUALIDADE (PONTUAL QUANDO ATRASO <= 15 MINUTOS)
-- ==============================================================================
SELECT 
    linha,
    COUNT(*) AS total_viagens,
    SUM(CASE WHEN atraso_minutos <= 15 THEN 1 ELSE 0 END) AS viagens_pontuais,
    ROUND((SUM(CASE WHEN atraso_minutos <= 15 THEN 1 ELSE 0 END) / COUNT(*)) * 100, 2) AS indice_pontualidade_pct
FROM transporte
WHERE data_viagem >= CURDATE() - INTERVAL 30 DAY
GROUP BY linha
ORDER BY indice_pontualidade_pct ASC;

