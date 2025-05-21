# ----- CONFIGURE YOUR EDITOR TO USE 4 SPACES PER TAB ----- #
import sys,os
sys.path.append(os.path.join(os.path.split(os.path.abspath(__file__))[0], 'lib'))
import pymysql

def connection():
    ''' User this function to create your connections '''    
    con = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='N1k0s@g3l0', db='movies') #update with your settings
    
    return con


def updateRank(rank1, rank2, movieTitle):

    # Create a new connection
    con = connection()

    # Create a cursor on the connection
    cur = con.cursor()

    try:
        rank1 = float(rank1)
        if not (0 <= rank1 <= 10):
            return [("status",), ("error",)]
    except ValueError:
        return [("status",), ("error",)]

    try:
        rank2 = float(rank2)
        if not (0 <= rank2 <= 10):
            return [("status",), ("error",)]
    except ValueError:
        return [("status",), ("error",)]

    try:
        # Check if the movie exists and get the current rank
        query = "SELECT movie_id, `rank` FROM movie WHERE title = %s"
        cur.execute(query, (movieTitle,))
        rows = cur.fetchall()

        if len(rows) == 0:
            return [("status",), ("error",)]  # No movie found
        elif len(rows) > 1:
            return [("status",), ("error",)]  # Multiple movies found

        movie_id, current_rank = rows[0]

        # Calculate the new rank
        if current_rank is None:
            new_rank = (rank1 + rank2) / 2
        else:
            new_rank = (current_rank + rank1 + rank2) / 3

        # Update the movie's rank
        update_query = "UPDATE movie SET `rank` = %s WHERE movie_id = %s"
        cur.execute(update_query, (new_rank, movie_id))
        con.commit()
        
        print (rank1, rank2, movieTitle)
        return [("status",), ("ok",)]
    except Exception as e:
        con.rollback()
        print(f"Exception: {e}")  # Debug print
        return [("status",), ("error",)]
    finally:
        cur.close()
        con.close()


def colleaguesOfColleagues(actorId1, actorId2):

 # Create a new connection
    con = connection()

    # Create a cursor on the connection
    cur = con.cursor()

    try:
        actorId1 = int(actorId1)
    except ValueError:
        return [("status",), ("error",)]
    
    try:
        actorId2 = int(actorId2)
    except ValueError:
        return [("status",), ("error",)]

    try:
        if actorId1 != actorId2:

            # Step 1: Find all actors 'c' who have acted with actor 'a'
            query1 = """
                SELECT DISTINCT rc.actor_id
                FROM role ra, role rc
                WHERE ra.movie_id = rc.movie_id AND ra.actor_id = %s AND rc.actor_id <> ra.actor_id AND rc.actor_id <> %s
            """
            cur.execute(query1, (actorId1, actorId2))
            actor_c_list = cur.fetchall()
       

            # Step 2: Find all actors 'd' who have acted with actor 'b'
            query2 = """
                SELECT DISTINCT rd.actor_id
                FROM role rb, role rd
                WHERE rb.movie_id = rd.movie_id and rb.actor_id = %s AND rd.actor_id <> rb.actor_id AND rd.actor_id <> %s
            """
            cur.execute(query2, (actorId2, actorId1))
            actor_d_list = cur.fetchall()
        
            # Step 3: Find movies where 'c' and 'd' have acted together
            result = []
            seen_pairs = set()
            query3 = """
                SELECT DISTINCT m.title, rc.actor_id as actor_c, rd.actor_id as actor_d
                FROM role rc, role rd, movie m
                WHERE m.movie_id = rc.movie_id and rc.movie_id = rd.movie_id and rc.actor_id = %s AND rd.actor_id = %s
            """
            
            for actor_c in actor_c_list:
                for actor_d in actor_d_list:
                   
                    if actor_c[0] != actor_d[0]:
                         # Create a sorted tuple of the pair to ensure uniqueness
                        pair = tuple(sorted((actor_c[0], actor_d[0])))
                        if pair not in seen_pairs:
                            cur.execute(query3, (actor_c[0], actor_d[0]))
                            movies = cur.fetchall()
                            for movie in movies:
                                result.append((movie[0], movie[1], movie[2], actorId1, actorId2))
                            seen_pairs.add(pair)
       

            if result:
                return [("movieTitle", "colleagueOfActor1", "colleagueOfActor2", "actor1", "actor2")] + result 
            else:
                return [("status",), ("error",)]

    except Exception as e:
        con.rollback()
        return [("status",), ("error",)]
    finally:
        cur.close()
        con.close()


def actorPairs(actorId):

    # Create a new connection
    con = connection()

    # Create a cursor on the connection
    cur = con.cursor()

    try:
        actorId = int(actorId)
    except ValueError:
        return [("status",), ("error",)]

    try:
        # Step 1: Retrieve colleagues who have worked in movies with the actor in at least 7 genres
        query_colleagues = """
            SELECT DISTINCT r2.actor_id
            FROM role r1, role r2, movie_has_genre mg
            WHERE r1.movie_id = r2.movie_id
            AND r2.movie_id = mg.movie_id
            AND r1.actor_id = %s
            AND r2.actor_id <> %s
            GROUP BY r2.actor_id
            HAVING COUNT(DISTINCT mg.genre_id) >= 7
        """
        cur.execute(query_colleagues, (actorId, actorId))
        colleagues = [row[0] for row in cur.fetchall()]
        if len(colleagues) == 0:
            return [("status",), ("error - This actor hasn't played in more than 7 genres",)]  

        # Step 2: Retrieve movies and genres that the given actor has played
        query_actor_movies_genres = """
            SELECT DISTINCT mg.genre_id, mg.movie_id
            FROM movie_has_genre mg, role r
            WHERE mg.movie_id = r.movie_id AND r.actor_id = %s
        """
        cur.execute(query_actor_movies_genres, (actorId,))
        actor_movies_genres = {(row[0], row[1]) for row in cur.fetchall()}

        # Step 3: Filter colleagues based on their movies and genres
        result = []
        for colleague_id in colleagues:
            # Retrieve movies and genres that the colleague has played
            query_colleague_movies_genres = """
                SELECT DISTINCT mg.genre_id, mg.movie_id
                FROM movie_has_genre mg, role r
                WHERE mg.movie_id = r.movie_id AND r.actor_id = %s
            """
            cur.execute(query_colleague_movies_genres, (colleague_id,))
            colleague_movies_genres = {(row[0], row[1]) for row in cur.fetchall()}

            valid_colleague = True

            # Find the common genres between actor and colleague
            common_genres = set()
            for genre_id, movie_id in actor_movies_genres:
                for col_genre_id, col_movie_id in colleague_movies_genres:
                    if genre_id == col_genre_id:
                        common_genres.add(genre_id)

            # Every common genre must be in the same movie
            for genre_id in common_genres:
                actor_movies_in_genre = set()
                for g_id, movie_id in actor_movies_genres:
                    if g_id == genre_id:
                        actor_movies_in_genre.add(movie_id)
                
                colleague_movies_in_genre = set()
                for g_id, movie_id in colleague_movies_genres:
                    if g_id == genre_id:
                        colleague_movies_in_genre.add(movie_id)
                
                # Check that there is at least one movie that they played together with that genre
                if len(actor_movies_in_genre & colleague_movies_in_genre) == 0:
                    valid_colleague = False
                    break

            if valid_colleague:
                result.append((colleague_id,))

        print(actorId)
        # Returning the results
        if len(result) == 0:
            return [("status",), ("error - This actor has no pair",)]  
        return [("actorId",)] + result

    except Exception as e:
        con.rollback()
        print(f"Exception: {e}")  # Debug print
        return [("status",), ("error",)]
    finally:
        cur.close()
        con.close()


def selectTopNactors(n):

    # Create a new connection
    con=connection()

    # Create a cursor on the connection
    cur=con.cursor()

    try:
        n = int(n)
        if not (n > 0):
            return [("status",), ("error",)]
    except ValueError:
        return [("status",), ("error",)]
    
    try:
        query = """ 
            SELECT g.genre_name, a.actor_id, count(mg.movie_id) AS Number_of_Movies
            FROM actor a, role r, movie_has_genre mg, genre g
            WHERE a.actor_id = r.actor_id AND r.movie_id = mg.movie_id AND mg.genre_id = g.genre_id
            GROUP BY a.actor_id, g.genre_name
            ORDER BY g.genre_name,  Number_of_Movies DESC
        """

        cur.execute(query)
        rows = cur.fetchall()

        results_by_genre = {}
        for row in rows:
            genre = row[0]
            actor_id = row[1]
            number_of_movies = row[2]
            if genre not in results_by_genre:
                results_by_genre[genre] = []
            results_by_genre[genre].append((actor_id, number_of_movies))
        
        # Prepare final results, keeping only top N actors per genre
        final_results = [("genreName", "actorId", "numberOfMovies")]
        for genre, actors in results_by_genre.items():
            top_actors = actors[:n]
            for actor in top_actors:
                final_results.append((genre, actor[0], actor[1]))

        print(n)
        return final_results

    except Exception as e:
        con.rollback()
        print(f"Exception: {e}")  # Debug print
        return [("status",), ("error",)]
    finally:
        cur.close()
        con.close()


def traceActorInfluence(actorId):
    # Create a new connection
    con=connection()

    # Create a cursor on the connection
    cur=con.cursor()


    return [("influencedActorId",),]
