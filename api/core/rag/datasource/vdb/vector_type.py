from enum import StrEnum


class VectorType(StrEnum):
    ANALYTICDB = "analyticdb"
    CHROMA = "chroma"
    MILVUS = "milvus"
    MYSCALE = "myscale"
    PGVECTOR = "pgvector"
    VASTBASE = "vastbase"
    PGVECTO_RS = "pgvecto-rs"

    QDRANT = "qdrant"
    RELYT = "relyt"
    TIDB_VECTOR = "tidb_vector"
    WEAVIATE = "weaviate"
    OPENSEARCH = "opensearch"
    TENCENT = "tencent"
    ORACLE = "oracle"
    ELASTICSEARCH = "elasticsearch"
    ELASTICSEARCH_JA = "elasticsearch-ja"
    LINDORM = "lindorm"
    COUCHBASE = "couchbase"
    BAIDU = "baidu"
    VIKINGDB = "vikingdb"
    UPSTASH = "upstash"
    TIDB_ON_QDRANT = "tidb_on_qdrant"
    OCEANBASE = "oceanbase"
    OPENGAUSS = "opengauss"
    # TABLESTORE = "tablestore"  # 已注释，暂不使用
    HUAWEI_CLOUD = "huawei_cloud"
    MATRIXONE = "matrixone"
