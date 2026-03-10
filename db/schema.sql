CREATE SCHEMA finorg_db;

CREATE USER 'finorg'@'localhost' IDENTIFIED BY 'tiopatinhas';

GRANT ALL PRIVILEGES ON finorg_db.* TO 'finorg'@'localhost';

USE finorg_db;

CREATE TABLE family_member (
    family_member_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE earning (
    earning_id INT AUTO_INCREMENT PRIMARY KEY,
    family_member_id INT NOT NULL,
    description VARCHAR(50) NOT NULL,
    value DECIMAL(10,2) NOT NULL,
    dat_received DATE NOT NULL,

    CONSTRAINT fk_earning_family_member
        FOREIGN KEY (family_member_id)
        REFERENCES family_member(family_member_id)
        ON DELETE CASCADE
);

CREATE TABLE spending (
    spending_id INT AUTO_INCREMENT PRIMARY KEY,
    family_member_id INT NOT NULL,
    description VARCHAR(50) NOT NULL,
    value DECIMAL(10,2) NOT NULL,
    dat_spent DATE NOT NULL,
    type ENUM('DEBIT', 'CREDIT', 'PIX') NOT NULL,
    original_spending_id INT NULL,

    CONSTRAINT fk_spending_family_member
        FOREIGN KEY (family_member_id)
        REFERENCES family_member(family_member_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_spending_original
        FOREIGN KEY (original_spending_id)
        REFERENCES spending(spending_id)
        ON DELETE SET NULL
);

CREATE INDEX idx_earning_family_member
ON earning (family_member_id);

CREATE INDEX idx_spending_family_member
ON spending (family_member_id);

INSERT INTO family_member(name) VALUES('Fausto');
INSERT INTO family_member(name) VALUES('Jordana');