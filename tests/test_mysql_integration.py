"""CI-only disposable MySQL; never connects to the user's real database."""
import os
import unittest
from pathlib import Path


@unittest.skipUnless(os.getenv("RUN_MYSQL_TESTS") == "1", "isolated CI MySQL not enabled")
class MySQLIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import pymysql
        host = os.environ.get("MYSQL_TEST_HOST", "127.0.0.1")
        database = os.environ.get("MYSQL_TEST_DATABASE", "")
        if host not in {"127.0.0.1", "localhost"} or not database.startswith("ci_climate_"):
            raise ValueError("Refusing to run integration fixtures outside disposable local CI schema")
        cls.connection = pymysql.connect(
            host=host, user=os.environ["MYSQL_TEST_USER"], password=os.environ["MYSQL_TEST_PASSWORD"],
            database=database, charset="utf8mb4", autocommit=False,
            connect_timeout=5, read_timeout=5, write_timeout=5,
        )
        # Controlled bootstrap file, not arbitrary external SQL. No user dataset is loaded.
        sql = (Path(__file__).resolve().parents[1] / "infrastructure/docker/mysql-init/001_schema.sql").read_text(encoding="utf8")
        with cls.connection.cursor() as cur:
            for statement in sql.split(";"):
                if statement.strip():
                    cur.execute(statement)
        cls.connection.commit()

    @classmethod
    def tearDownClass(cls):
        cls.connection.close()

    def tearDown(self):
        self.connection.rollback()

    def test_required_tables_exist(self):
        with self.connection.cursor() as cur:
            cur.execute("SHOW TABLES")
            tables = {r[0] for r in cur.fetchall()}
        self.assertTrue({"climate_data", "ua_places", "hri_cache", "hri_impacts"} <= tables)

    def test_parameterized_climate_insert_and_read(self):
        with self.connection.cursor() as cur:
            cur.execute("INSERT INTO climate_data (year,month,avg_temp,solar_irradiance,humidity) VALUES (%s,%s,%s,%s,%s)", (2026,1,10,180,65))
            cur.execute("SELECT avg_temp FROM climate_data WHERE id=%s", (cur.lastrowid,))
            self.assertEqual(cur.fetchone()[0], 10)

    def test_invalid_month_is_rejected(self):
        import pymysql
        with self.connection.cursor() as cur:
            with self.assertRaises(pymysql.err.OperationalError):
                cur.execute("INSERT INTO climate_data (year,month) VALUES (%s,%s)", (2026,13))


if __name__ == "__main__":
    unittest.main()
