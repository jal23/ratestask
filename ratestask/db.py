import psycopg2


class DBAPI(object):

    def __init__(self, db_uri):
        self.db_uri = db_uri

    def get_db_conn(self):
        # TODO: Implement DB connection pool.
        db_conn = psycopg2.connect(self.db_uri)
        return db_conn

    def get_avg_rates(
        self,
        db_cursor,
        start_date,
        end_date,
        origin,
        destination,
        min_price_count=3
    ):
        """
        Query for fetching daily average price rates between the given
        origin and destination port/region.
        """

        """
        CTEs:
            sub_regions: CTE for recursively querying nested sub-regions
                         for every main/parent region
            ports_prices: CTE for querying prices between origin and
                          destination ports.
        """
        query = """
            WITH RECURSIVE sub_regions AS (
                SELECT parent_slug, slug FROM regions
                WHERE parent_slug IS NOT NULL
                UNION ALL
                SELECT s.parent_slug, r.slug
                FROM sub_regions as s
                INNER JOIN regions AS r ON s.slug = r.parent_slug
            ),
            ports_prices AS (
                SELECT prices.*,
                       orig_ports.parent_slug AS orig_slug,
                       dest_ports.parent_slug AS dest_slug
                FROM prices
                INNER JOIN ports AS orig_ports
                    ON prices.orig_code = orig_ports.code
                INNER JOIN ports AS dest_ports
                    ON prices.dest_code = dest_ports.code
            )
            SELECT day,
                   CASE
                        WHEN COUNT(price) >= %(min_price_count)s THEN AVG(price)
                        ELSE NULL
                   END AS average_price
            FROM ports_prices
            WHERE day >= %(start_date)s AND
                  day <= %(end_date)s AND
                (
                    orig_code = %(origin)s OR
                    orig_slug = %(origin)s OR
                    orig_slug IN (
                        SELECT slug
                        FROM sub_regions
                        WHERE parent_slug = %(origin)s
                    )
                ) AND
                (
                    dest_code = %(destination)s OR
                    dest_slug = %(destination)s OR
                    dest_slug IN (
                        SELECT slug
                        FROM sub_regions
                        WHERE parent_slug = %(destination)s
                    )
                )
            GROUP BY day
            ORDER BY day
        """
        db_cursor.execute(
            query,
            {
                "start_date": start_date,
                "end_date": end_date,
                "origin": origin,
                "destination": destination,
                "min_price_count": min_price_count
            }
        )
        rows = db_cursor.fetchall()
        return rows

