"""Persistência DuckDB e importação inicial dos arquivos legados."""

from contextlib import contextmanager
from functools import lru_cache
import json
import logging
import math
import os
from pathlib import Path
from threading import RLock

import duckdb
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATABASE = BASE_DIR / "data" / "roadfixer.duckdb"
_LOCK = RLock()
logger = logging.getLogger(__name__)


class Database:
    def __init__(self, path: Path, seed_dir: Path = BASE_DIR):
        self.path = Path(path).resolve()
        self.seed_dir = Path(seed_dir)
        self._initialized = False

    @contextmanager
    def _transaction(self):
        # A API e o agendador usam threads do mesmo processo. Cada operação
        # possui sua conexão, e a trava protege também a troca de tabelas.
        with _LOCK:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            connection = duckdb.connect(str(self.path))
            try:
                connection.execute("BEGIN TRANSACTION")
                yield connection
                connection.execute("COMMIT")
            except BaseException:
                connection.execute("ROLLBACK")
                raise
            finally:
                connection.close()

    def initialize(self):
        with _LOCK:
            if self._initialized:
                return
            with self._transaction() as connection:
                connection.execute("CREATE TABLE IF NOT EXISTS documents (name VARCHAR PRIMARY KEY, payload JSON)")
                connection.execute("CREATE TABLE IF NOT EXISTS accidents (source_file VARCHAR)")
                connection.execute("CREATE TABLE IF NOT EXISTS weather (source_file VARCHAR)")
                connection.execute("CREATE TABLE IF NOT EXISTS tau (CLASSE VARCHAR, SUBCLASSE VARCHAR, TAU DOUBLE)")
                connection.execute("CREATE TABLE IF NOT EXISTS risk_values (km INTEGER PRIMARY KEY, risk DOUBLE)")
                connection.execute("CREATE TABLE IF NOT EXISTS predictions (km INTEGER, risk DOUBLE)")
                if self._get_document(connection, "migration_v1") is None:
                    self._import_legacy(connection)
                    self._put_document(connection, "migration_v1", {"complete": True})
            self._initialized = True

    @contextmanager
    def connection(self):
        self.initialize()
        with self._transaction() as connection:
            yield connection

    @staticmethod
    def _put_document(connection, name, value):
        connection.execute(
            "INSERT OR REPLACE INTO documents VALUES (?, ?)",
            [name, json.dumps(value, ensure_ascii=False, allow_nan=False)],
        )

    @staticmethod
    def _get_document(connection, name):
        row = connection.execute("SELECT payload FROM documents WHERE name = ?", [name]).fetchone()
        return json.loads(row[0]) if row else None

    def get_document(self, name):
        with self.connection() as connection:
            return self._get_document(connection, name)

    def save_document(self, name, value):
        with self.connection() as connection:
            self._put_document(connection, name, value)

    @staticmethod
    def _replace_frame(connection, table, source_file, frame):
        if table not in {"accidents", "weather"}:
            raise ValueError("Tabela de origem inválida")
        frame = frame.copy()
        frame["source_file"] = source_file
        connection.register("incoming", frame)
        try:
            connection.execute(
                f"CREATE OR REPLACE TABLE {table} AS "
                f"SELECT * FROM {table} WHERE source_file <> ? "
                "UNION ALL BY NAME SELECT * FROM incoming",
                [source_file],
            )
        finally:
            connection.unregister("incoming")

    def save_accidents(self, source_file, frame):
        with self.connection() as connection:
            self._replace_frame(connection, "accidents", source_file, frame)

    def save_weather(self, source_file, frame):
        with self.connection() as connection:
            self._replace_frame(connection, "weather", source_file, frame)

    def accident_sources(self):
        with self.connection() as connection:
            return [row[0] for row in connection.execute(
                "SELECT DISTINCT source_file FROM accidents ORDER BY source_file"
            ).fetchall()]

    def load_accidents(self, source_file=None):
        with self.connection() as connection:
            query = "SELECT * EXCLUDE (source_file) FROM accidents"
            # Antes da primeira importação a tabela possui apenas source_file.
            if len(connection.execute("DESCRIBE accidents").fetchall()) == 1:
                return pd.DataFrame()
            if source_file is None:
                return connection.execute(query + " ORDER BY source_file").df()
            return connection.execute(query + " WHERE source_file = ?", [source_file]).df()

    def load_weather(self, source_file):
        with self.connection() as connection:
            if len(connection.execute("DESCRIBE weather").fetchall()) == 1:
                return None
            frame = connection.execute(
                "SELECT * EXCLUDE (source_file) FROM weather WHERE source_file = ?", [source_file]
            ).df()
            return None if frame.empty else frame

    def load_tau(self):
        with self.connection() as connection:
            return connection.execute("SELECT * FROM tau").df()

    def _save_risk(self, connection, payload):
        values = [(km, float(value)) for km, value in enumerate(payload["risk"])]
        if any(not math.isfinite(value) for _, value in values):
            raise ValueError("Índices de risco devem ser finitos")
        connection.execute("DELETE FROM risk_values")
        if values:
            connection.executemany("INSERT INTO risk_values VALUES (?, ?)", values)
        self._put_document(connection, "risk_metadata", {key: value for key, value in payload.items() if key != "risk"})

    def save_risk(self, payload):
        with self.connection() as connection:
            self._save_risk(connection, payload)

    def get_risk(self):
        with self.connection() as connection:
            metadata = self._get_document(connection, "risk_metadata")
            if metadata is None:
                return {"last_update": None, "risk": [], "status": "risk_data_not_generated"}
            values = connection.execute("SELECT risk FROM risk_values ORDER BY km").fetchall()
            return {**metadata, "risk": [row[0] for row in values]}

    def _save_predictions(self, connection, frame):
        values = [(int(float(row.KM)), float(row.risco_previsto)) for row in frame.itertuples()]
        if any(not math.isfinite(value) for _, value in values):
            raise ValueError("Previsões devem ser finitas")
        connection.execute("DELETE FROM predictions")
        if values:
            connection.executemany("INSERT INTO predictions VALUES (?, ?)", values)
        self._put_document(connection, "prediction_metadata", {
            "period": str(frame.iloc[0]["PERIODO"]) if len(frame) else None,
            "status": "ready",
        })

    def save_predictions(self, frame):
        with self.connection() as connection:
            self._save_predictions(connection, frame)

    def get_predictions(self):
        with self.connection() as connection:
            metadata = self._get_document(connection, "prediction_metadata")
            if metadata is None:
                return {"period": None, "predictions": [], "status": "prediction_not_generated"}
            values = connection.execute("SELECT km, risk FROM predictions ORDER BY km").fetchall()
            return {**metadata, "predictions": [{"KM": km, "risco": value} for km, value in values]}

    def _import_legacy(self, connection):
        content = self.seed_dir / "API" / "content"
        for name, folder in (("cards", "cards"), ("stats", "stats"),
                             ("history", "accident-history"), ("datasets", "conjuntos")):
            path = content / folder / "content.json"
            if path.exists():
                self._put_document(connection, name, json.loads(path.read_text(encoding="utf-8")))

        for table, folder in (("accidents", "data/accidents/processed"), ("weather", "data/weather-data")):
            for path in sorted((self.seed_dir / folder).glob("p*.csv")):
                self._replace_frame(connection, table, path.name, pd.read_csv(path, encoding="utf-8"))

        tau_file = self.seed_dir / "ModeloEstatistico/data_tau/tau.csv"
        if tau_file.exists():
            connection.register("tau_import", pd.read_csv(tau_file, encoding="utf-8"))
            connection.execute("INSERT INTO tau BY NAME SELECT CLASSE, SUBCLASSE, TAU FROM tau_import")
            connection.unregister("tau_import")

        risk_file = content / "accident-history/risk/savedData.json"
        if risk_file.exists():
            try:
                self._save_risk(connection, json.loads(risk_file.read_text(encoding="utf-8")))
            except (OSError, ValueError, KeyError, TypeError) as error:
                logger.warning("Risco legado não importado: %s", error)

        prediction_file = self.seed_dir / "ModeloEstatistico/data_tau/previsao_proximo_mes.csv"
        if prediction_file.exists():
            try:
                self._save_predictions(connection, pd.read_csv(prediction_file, encoding="utf-8"))
            except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
                logger.warning("Previsão legada não importada: %s", error)


@lru_cache(maxsize=None)
def _database(path):
    return Database(Path(path))


def get_database():
    return _database(str(Path(os.environ.get("ROADFIXER_DB_PATH", DEFAULT_DATABASE)).resolve()))


if __name__ == "__main__":
    database = get_database()
    database.initialize()
    print(f"DuckDB pronto: {database.path}")
