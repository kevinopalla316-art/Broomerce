USE broomerce;

INSERT INTO users (first_name, last_name, email, password_hash, role, phone, is_active, created_at, updated_at)
VALUES ('Admin', 'Demo', 'admin@broomerce.local', 'scrypt:32768:8:1$8DtEvyXyq7Mwr8AR$68e8ef82b7c578fb43ddc158d6d88ef685a5742a44ab4b7500b800779008cdd1a61d5f38d0b434a74910945b305633d6d0d38a4947235bd4468c386b00dfef55', 'admin', '09999999999', 1, NOW(), NOW())
ON DUPLICATE KEY UPDATE
    first_name = VALUES(first_name),
    last_name = VALUES(last_name),
    password_hash = VALUES(password_hash),
    role = VALUES(role),
    phone = VALUES(phone),
    is_active = VALUES(is_active),
    updated_at = NOW();

-- Development-only demo data. Change or remove these records before production deploys.
-- Demo categories and products are already inserted by broomerce.sql.
-- This file is intentionally small and safe to run only during local development.
