-- Pylol Post-init Migration Script
-- Legacy > v0.1
-- This file is written for a PostgreSQL database and contains queries and
-- commands exclusive to PostreSQL, so it likely won't work properly with other
-- DBMS's

-------------------------------------------------------------------------------
-- Make sure you have run pylol-init before continuing!
-------------------------------------------------------------------------------

\c pylol

--
-- Import summoners
--
INSERT INTO summoners (
    "summonerId", "accountId", "region", "name", "internalName", "level",
    "icon", "lastUpdate"
)
SELECT
    "summonerId", "acctId", "region", "name", "internalName",
    "summonerLevel", "profileIconId", 0
FROM summoners_old;

--
-- Import champions
--
INSERT INTO champions ("key", "name")
SELECT "id", "name" FROM champions_old;
-- Import some missing champs
INSERT INTO champions ("key", "name") VALUES
    (154, 'Zac'),
    (127, 'Lissandra'),
    (266, 'Aatrox'),
    (236, 'Lucian');

--
-- Import games
--
INSERT INTO games (
    "gameId", "userId", "region", "adjustedRating", "afk", "boostIpEarned",
    "boostXpEarned", "championId", "createDate", "dataVersion", "difficulty",
    "difficultyString", "eligibleFirstWinOfDay", "eloChange",
    "experienceEarned", "futureData", "gameMapId", "gameMode", "gameType",
    "gameTypeEnum", "id", "invalid", "ipEarned", "KCoefficient", "leaver",
    "level", "predictedWinPct", "premadeSize", "premadeTeam", "queueType",
    "ranked", "rating", "rawStatsJson", "skinIndex", "skinName", "spell1",
    "spell2", "subType", "summonerId", "teamId", "teamRating", "timeInQueue",
    "userServerPing"
)
SELECT
    "gameId", "userId", 'NA', 0, "afk", "boostIpEarned", "boostXpEarned",
    "championId", "createDate", 0, null, null, "eligibleFirstWinOfDay", 0,
    "experienceEarned", null, "gameMapId", "gameMode", "gameType", "gameType",
    null, false, "ipEarned", 0, "leaver", "level", 0, "premadeSize",
    "premadeTeam", "queueType", "ranked", 0, null, "skinIndex", null, "spell1",
    "spell2", "subType", "summonerId", "teamId", 0, "timeInQueue",
    "userServerPing"
FROM games_old;

--
-- Import players
--
INSERT INTO players ("gameId", "summonerId", "championId", "teamId",
                     "dataVersion", "futureData")
SELECT "gameId", "summonerId", "championId", "teamId", 0, null
FROM players_old;

--
-- Import stats
--
INSERT INTO stats (
    "gameId", "userId", "TOTAL_TIME_SPENT_DEAD", "TOTAL_HEAL",
    "MAGIC_DAMAGE_DEALT_PLAYER", "GOLD_EARNED", "PHYSICAL_DAMAGE_TAKEN",
    "ASSISTS", "LEVEL", "LARGEST_CRITICAL_STRIKE", "ITEM0", "ITEM1",
    "LARGEST_KILLING_SPREE", "WIN", "LARGEST_MULTI_KILL", "CHAMPIONS_KILLED",
    "TOTAL_DAMAGE_TAKEN", "SIGHT_WARDS_BOUGHT_IN_GAME",
    "VISION_WARDS_BOUGHT_IN_GAME", "PHYSICAL_DAMAGE_DEALT_TO_CHAMPIONS",
    "TOTAL_DAMAGE_DEALT_TO_CHAMPIONS", "MAGIC_DAMAGE_TAKEN", "NUM_DEATHS",
    "TURRETS_KILLED", "ITEM2", "ITEM3", "BARRACKS_KILLED",
    "PHYSICAL_DAMAGE_DEALT_PLAYER",
    "ITEM5", "ITEM4", "NEUTRAL_MINIONS_KILLED",
    "MAGIC_DAMAGE_DEALT_TO_CHAMPIONS", "MINIONS_KILLED", "TOTAL_DAMAGE_DEALT",
    "LOSE", "dataVersion"
)
SELECT
    "gameId", "userId", "TOTAL_TIME_SPENT_DEAD", "TOTAL_HEAL",
    "MAGIC_DAMAGE_DEALT_PLAYER", "GOLD_EARNED", "PHYSICAL_DAMAGE_TAKEN",
    "ASSISTS", "LEVEL", "LARGEST_CRITICAL_STRIKE", "ITEM0", "ITEM1",
    "LARGEST_KILLING_SPREE", (CASE WHEN "WIN"=1 THEN true ELSE false END),
    "LARGEST_MULTI_KILL", "CHAMPIONS_KILLED", "TOTAL_DAMAGE_TAKEN",
    "SIGHT_WARDS_BOUGHT_IN_GAME", "VISION_WARDS_BOUGHT_IN_GAME",
    "PHYSICAL_DAMAGE_DEALT_TO_CHAMPIONS", "TOTAL_DAMAGE_DEALT_TO_CHAMPIONS",
    "MAGIC_DAMAGE_TAKEN", "NUM_DEATHS", "TURRETS_KILLED", "ITEM2", "ITEM3",
    "BARRACKS_KILLED", "PHYSICAL_DAMAGE_DEALT_PLAYER", "ITEM5", "ITEM4",
    "NEUTRAL_MINIONS_KILLED", "MAGIC_DAMAGE_DEALT_TO_CHAMPIONS",
    "MINIONS_KILLED", "TOTAL_DAMAGE_DEALT",
    -- LOSE is the inverse of WIN
    (CASE WHEN "WIN"=1 THEN false ELSE true END),
    -- Set dataVersion to 0
    0
FROM stats_old;

--
-- Put all existing summoners into a new mumblecrew group
--
INSERT INTO groups ("id", "internalName", "name")
VALUES (1, 'mumble-crew', 'Mumble Crew');
INSERT INTO group_mem ("groupId", "summonerId")
SELECT 1, "summonerId"
FROM summoners;

--
-- Add new summoners epicboak.OC and Polyester.OC and then add them
-- to a new Oceania Bros group
--
INSERT INTO summoners (
    "summonerId", "accountId", "region", "name", "internalName", "level",
    "icon", "lastUpdate")
VALUES
    (305337, 200051804, 'OC', 'epicboak', 'epicboak', 30, 506, 0),
    (235628, 200012044, 'OC', 'Polyester', 'polyester', 30, 539, 0);
INSERT INTO groups ("id", "internalName", "name")
VALUES (2, 'oceania-bros', 'Oceania Bros');
INSERT INTO group_mem
SELECT 2, "summonerId"
FROM summoners
WHERE "region" = 'OC';

--
-- Remove the old tables
--
DROP TABLE champions_old;
DROP TABLE stats_old;
DROP TABLE games_old;
DROP TABLE players_old;
DROP TABLE pylol_old;
DROP TABLE summoners_old;

--
-- Recreate views
--
CREATE VIEW gameresults AS
SELECT
    g."gameId", g."userId",
    s."name" || '.' || s."region" AS "summoner",
    c."name" AS "champion",
    timestamp with time zone
        'epoch' + g."createDate" * INTERVAL '1 second' as "date",
    CASE WHEN st."WIN" = true THEN 'W'::text ELSE 'L'::text END AS "result"
FROM games AS g
INNER JOIN stats AS st USING ("gameId", "userId")
INNER JOIN summoners AS s ON g."userId" = s."accountId"
INNER JOIN champions AS c ON g."championId" = c."key"
ORDER BY g."createDate" DESC;

CREATE VIEW matchdata AS
SELECT
    -- Games Table
    g."gameId", g."userId", g."region", g."adjustedRating", g."afk",
    g."boostIpEarned", g."boostXpEarned", g."championId", g."createDate",
    g."dataVersion" AS "dataVersion_game", g."difficulty", g."difficultyString",
    g."eligibleFirstWinOfDay", g."eloChange", g."experienceEarned",
    g."futureData", g."gameMapId", g."gameMode", g."gameType",
    g."gameTypeEnum", g."id", g."invalid", g."ipEarned", g."KCoefficient",
    g."leaver", g."predictedWinPct", g."premadeSize", g."premadeTeam",
    g."queueType", g."ranked", g."rating", g."rawStatsJson", g."skinIndex",
    g."skinName", g."spell1", g."spell2", g."subType", g."teamId",
    g."teamRating", g."timeInQueue",
    g."userServerPing",
    -- Stats Table
    st."dataVersion" AS "dataVersion_stat", st."ASSISTS", st."BARRACKS_KILLED",
    st."CHAMPIONS_KILLED", st."GOLD_EARNED", st."ITEM0", st."ITEM1",
    st."ITEM2", st."ITEM3", st."ITEM4", st."ITEM5",
    st."LARGEST_CRITICAL_STRIKE", st."LARGEST_KILLING_SPREE",
    st."LARGEST_MULTI_KILL", st."LEVEL", st."LOSE",
    st."MAGIC_DAMAGE_DEALT_PLAYER", st."MAGIC_DAMAGE_DEALT_TO_CHAMPIONS",
    st."MAGIC_DAMAGE_TAKEN", st."MINIONS_KILLED", st."NEUTRAL_MINIONS_KILLED",
    st."NEUTRAL_MINIONS_KILLED_ENEMY_JUNGLE", st."NEUTRAL_MINIONS_KILLED_YOUR_JUNGLE",
    st."NUM_DEATHS", st."PHYSICAL_DAMAGE_DEALT_PLAYER",
    st."PHYSICAL_DAMAGE_DEALT_TO_CHAMPIONS", st."PHYSICAL_DAMAGE_TAKEN",
    st."SIGHT_WARDS_BOUGHT_IN_GAME", st."TOTAL_DAMAGE_DEALT",
    st."TOTAL_DAMAGE_DEALT_TO_CHAMPIONS", st."TOTAL_DAMAGE_TAKEN",
    st."TOTAL_HEAL", st."TOTAL_TIME_CROWD_CONTROL_DEALT",
    st."TOTAL_TIME_SPENT_DEAD", st."TRUE_DAMAGE_DEALT_PLAYER",
    st."TRUE_DAMAGE_DEALT_TO_CHAMPIONS", st."TRUE_DAMAGE_TAKEN",
    st."TURRETS_KILLED", st."VISION_WARDS_BOUGHT_IN_GAME",
    st."WARD_KILLED", st."WARD_PLACED", st."WIN",
    -- Summoners Table
    s."summonerId", s."accountId", s."name", s."internalName", s."level",
    s."icon", s."lastUpdate",
    -- Champions Table
    c."name" as "championName"
FROM games AS g
INNER JOIN stats AS st USING ("gameId", "userId")
INNER JOIN summoners AS s ON g."userId" = s."accountId"
INNER JOIN champions AS c ON g."championId" = c."key";

CREATE VIEW matchhistory AS
SELECT
    g."gameId", s."name" AS "summoner", c."name" AS "champion", g."gameType",
    g."subType", g."gameMode",
    CASE
        WHEN g."leaver" = true THEN 'Leaver'::text
        WHEN st."WIN" = true THEN 'Victory'::text
        WHEN ST."LOSE" = true THEN 'Defeat'::text
    END as "outcome",
    (
        COALESCE(st."CHAMPIONS_KILLED", 0)
        || '/'::text ||
        COALESCE(st."NUM_DEATHS", 0)
        || '/'::text ||
        COALESCE(st."ASSISTS", 0)
    ) as "score",
    timestamp with time zone
        'epoch' + g."createDate" * INTERVAL '1 second' as "time"
FROM games AS g
INNER JOIN stats AS st USING ("gameId", "userId")
INNER JOIN summoners AS s ON g."userId" = s."accountId"
INNER JOIN champions AS c ON g."championId" = c."key"
ORDER BY g."createDate" DESC;

--
-- Post-migration tasks
--
ANALYZE champions;
ANALYZE games;
ANALYZE players;
ANALYZE registry;
ANALYZE stats;
ANALYZE summoners;
ANALYZE groups;
ANALYZE group_mem;
