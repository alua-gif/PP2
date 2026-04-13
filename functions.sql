-- Function 1: return all records matching a pattern
CREATE OR REPLACE FUNCTION records(p TEXT)
RETURNS TABLE(
    out_id INTEGER,
    out_name VARCHAR,
    out_phone VARCHAR
)
AS $$
BEGIN
    RETURN QUERY
    SELECT id, username, phone
    FROM phonebook
    WHERE username ILIKE '%' || p || '%'
       OR phone ILIKE '%' || p || '%';
END;
$$ LANGUAGE plpgsql;


-- Function 2: pagination with LIMIT and OFFSET
CREATE OR REPLACE FUNCTION pagination(lim INT, offs INT)
RETURNS TABLE(
    out_id INTEGER,
    out_name VARCHAR,
    out_phone VARCHAR
)
AS $$
BEGIN
    RETURN QUERY
    SELECT id, username, phone
    FROM phonebook
    ORDER BY id
    LIMIT lim OFFSET offs;
END;
$$ LANGUAGE plpgsql;