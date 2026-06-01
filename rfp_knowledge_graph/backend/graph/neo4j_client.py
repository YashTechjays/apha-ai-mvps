from neo4j import GraphDatabase
from backend.utils.config import get_settings
from backend.utils.logger import get_logger

logger = get_logger("neo4j_client")
_driver = None


def get_driver():
    global _driver
    if _driver is None:
        settings = get_settings()
        _driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )
        _driver.verify_connectivity()
        logger.info(f"Connected to Neo4j at {settings.neo4j_uri}")
    return _driver


def get_session():
    return get_driver().session()


def close_driver():
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None
        logger.info("Neo4j driver closed")
