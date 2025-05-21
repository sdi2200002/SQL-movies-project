#1115202200002-NIKOLAOS ANGELOPOULOS 
#1115202200055-MYRTO KALAITZI

#1 
SELECT m.title
FROM movie m
WHERE m.movie_id IN
    (SELECT r.movie_id
     FROM role r
     WHERE r.actor_id IN
         (SELECT a.actor_id
          FROM actor a
          WHERE a.last_name = "Allen"))
AND
m.movie_id IN
    (SELECT gr.movie_id
     FROM movie_has_genre gr
     WHERE gr.genre_id IN
        (SELECT g.genre_id
         FROM genre g 
         WHERE g.genre_name = "Comedy"))
ORDER BY m.title;

#2
SELECT d.last_name, m.title
FROM movie m, director d, actor a, movie_has_director md, role r
WHERE m.movie_id = md.movie_id AND d.director_id = md.director_id AND m.movie_id = r.movie_id AND a.actor_id = r.actor_id AND a.last_name = "Allen" 
AND EXISTS
	(SELECT * FROM movie_has_genre mg, movie_has_genre mg2, genre g , genre g2, movie m2, movie_has_director md2
	 WHERE m.movie_id = mg.movie_id AND mg.genre_id = g.genre_id AND m2.movie_id = mg2.movie_id AND mg2.genre_id = g2.genre_id AND m2.movie_id =md2.movie_id AND md2.director_id = d.director_id AND g.genre_id <> g2.genre_id)
ORDER BY d.last_name;

#3
SELECT DISTINCT a.last_name
FROM actor a
WHERE a.last_name IN(
        SELECT DISTINCT a1.last_name
        FROM actor a1, role r, movie_has_director md, director d1
        WHERE a1.actor_id = r.actor_id AND md.movie_id = r.movie_id AND md.director_id = d1.director_id AND a1.last_name = d1.last_name)
AND a.last_name IN(
        SELECT DISTINCT a2.last_name
        FROM actor a2, role r, movie_has_director md1, director d2, movie_has_genre mg1
        WHERE a2.actor_id = r.actor_id AND md1.movie_id = r.movie_id AND md1.director_id = d2.director_id AND mg1.movie_id = r.movie_id AND a2.last_name != d2.last_name AND r.movie_id  IN
			(SELECT md2.movie_id
			FROM movie_has_director md2, movie_has_genre mg2, director d3
			WHERE md2.movie_id = mg2.movie_id AND md2.director_id = d3.director_id AND mg1.genre_id = mg2.genre_id AND d3.last_name = a2.last_name )
);

#4
SELECT 
    'yes' AS answer
WHERE EXISTS (
    SELECT * FROM movie_has_genre mg
    WHERE mg.movie_id IN (
        SELECT m.movie_id
        FROM movie m
        WHERE m.year = 1995
    )
    AND mg.genre_id IN (
        SELECT g.genre_id
        FROM genre g
        WHERE g.genre_name = 'Drama'
    )
);

#5
SELECT DISTINCT d1.last_name AS director_1, d2.last_name AS director_2
FROM  director d1, director d2
WHERE d1.director_id < d2.director_id AND 
    EXISTS (
        SELECT * FROM  movie_has_director md1, movie_has_director md2, movie m
        WHERE md1.director_id = d1.director_id AND md2.director_id = d2.director_id AND md1.movie_id = md2.movie_id AND md1.movie_id = m.movie_id AND m.year BETWEEN 2000 AND 2006 AND
            (SELECT COUNT(DISTINCT mg.genre_id)
                FROM movie_has_genre mg
                WHERE mg.movie_id = m.movie_id) >= 6
    );


#6
SELECT a.first_name, a.last_name, count(DISTINCT md.director_id) AS 'count' 
FROM actor a, role r, movie_has_director md
WHERE a.actor_id = r.actor_id AND r.movie_id = md.movie_id
GROUP BY a.first_name, a.last_name
HAVING count(DISTINCT r.movie_id) = 3
ORDER BY last_name;

#7
SELECT mg.genre_id, COUNT(DISTINCT md.director_id) AS 'count'
FROM movie_has_genre mg, movie_has_director md  
WHERE mg.movie_id = md.movie_id AND mg.genre_id IN (
    SELECT DISTINCT mg1.genre_id
    FROM movie_has_genre mg1
    WHERE mg1.movie_id IN (
        SELECT mg.movie_id
        FROM movie_has_genre mg
        GROUP BY mg.movie_id
        HAVING COUNT(*) = 1
    )
)
GROUP BY mg.genre_id
ORDER BY mg.genre_id;

#8
SELECT a.actor_id 
FROM actor a
WHERE NOT EXISTS (
	SELECT g.genre_id 
    FROM genre g
    WHERE  NOT EXISTS (
		SELECT r.movie_id 
        FROM role r, movie_has_genre mg
        WHERE r.actor_id = a.actor_id AND r.movie_id = mg.movie_id AND mg.genre_id = g.genre_id
	)
);

#9
SELECT mg1.genre_id AS genre_id_1, mg2.genre_id AS genre_id_2, COUNT(DISTINCT md.director_id) AS 'count'
FROM movie_has_genre mg1, movie_has_genre mg2, movie_has_director md, movie m
WHERE mg1.genre_id < mg2.genre_id AND md.movie_id = m.movie_id AND m.movie_id IN(
	SELECT m1.movie_id
    FROM movie m1
    WHERE m1.movie_id = mg1.movie_id AND EXISTS(
		SELECT * FROM movie m2, movie_has_director md2
        WHERE m2.movie_id = mg2.movie_id AND md2.movie_id = m2.movie_id AND md2.director_id = md.director_id
        )
)
GROUP BY mg1.genre_id, mg2.genre_id
ORDER BY mg1.genre_id, mg2.genre_id;

#10 
SELECT DISTINCT g.genre_id, a.actor_id, COUNT(*) AS 'count'
FROM genre g, actor a, movie m, movie_has_genre mg, role r
WHERE g.genre_id = mg.genre_id AND mg.movie_id = m.movie_id AND m.movie_id = r.movie_id AND r.actor_id = a.actor_id
AND NOT EXISTS (
	SELECT * FROM director d, movie_has_director md
	WHERE d.director_id = md.director_id AND m.movie_id = md.movie_id
	AND EXISTS (
		SELECT * FROM movie_has_director md2, movie_has_genre mg2, genre g2
		WHERE md2.director_id = d.director_id AND md2.movie_id = mg2.movie_id AND mg2.genre_id = g2.genre_id AND g2.genre_id <> g.genre_id
		)
)
GROUP BY g.genre_id, a.actor_id
ORDER BY g.genre_id, a.actor_id;


