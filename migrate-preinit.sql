-- Pylol Pre-init Migration Script
-- Legacy > v0.1
-- This file is written for a PostgreSQL database and contains queries and
-- commands exclusive to PostreSQL, so it likely won't work properly with other
-- DBMS's

--
-- Copy original data over to a new database
--
\c postgres
DROP DATABASE pylol;

CREATE DATABASE pylol WITH
    TEMPLATE lmundydb
    ENCODING 'UTF8'
    LC_COLLATE 'en_AU.UTF-8'
    LC_CTYPE 'en_AU.UTF-8';
\c pylol

--
-- Remove the old views, we'll recreate them later
--
DROP VIEW gameresults;
DROP VIEW matchdata;
DROP VIEW matchhistory;

-- Rename old tables
ALTER TABLE champions RENAME TO champions_old;
ALTER TABLE games RENAME TO games_old;
ALTER TABLE players RENAME TO players_old;
ALTER TABLE pylol RENAME TO pylol_old;
ALTER TABLE stats RENAME TO stats_old;
ALTER TABLE summoners RENAME TO summoners_old;

-------------------------------------------------------------------------------
-- You should now run pylol-init and then continue the migration with
-- migrate-postinit.sql
-------------------------------------------------------------------------------
