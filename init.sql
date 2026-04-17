CREATE TABLE IF NOT EXISTS indicadores (
    id         SERIAL PRIMARY KEY,
    cidade     VARCHAR(100) NOT NULL,
    categoria  VARCHAR(100) NOT NULL,
    valor      NUMERIC(5,2),
    unidade    VARCHAR(20) DEFAULT '%',
    criado_em  TIMESTAMP DEFAULT NOW()
);

INSERT INTO indicadores (cidade, categoria, valor) VALUES
    ('São Paulo',    'Energia',  72.4),
    ('Curitiba',     'Água',     88.1),
    ('Manaus',       'Resíduos', 45.3),
    ('Porto Alegre', 'Energia',  91.0);
