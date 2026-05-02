# Neo4j Graph Database

이 프로젝트는 Neo4j를 사용하여 인용 네트워크와 협업 네트워크를 저장하고 쿼리합니다.

## 빠른 시작

### Docker로 실행 (권장)

```bash
# Neo4j 시작
docker-compose up -d neo4j

# 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f neo4j

# Neo4j 중지
docker-compose down
```

### 접속 정보

- **Bolt URI**: `bolt://localhost:7687`
- **HTTP URI**: `http://localhost:7474`
- **사용자명**: `neo4j`
- **비밀번호**: `research2026` (`.env` 파일에서 변경 가능)

### 브라우저 접속

웹 브라우저에서 http://localhost:7474 로 접속하여 Neo4j Browser를 사용할 수 있습니다.

## 데이터 가져오기

```bash
# OpenAlex 데이터를 Neo4j로 가져오기
uv run python scripts/prepare_neo4j_import.py
uv run python scripts/import_to_neo4j.py
```

## API 서버와 함께 사용

```bash
# Neo4j와 API 서버 모두 시작
docker-compose up -d
uv run python scripts/run_api.py
```

API는 Neo4j에 연결하여 그래프 쿼리를 실행합니다.

## 백업

```bash
# 데이터 백업
cp -r data/neo4j/data backup/neo4j-$(date +%Y%m%d)
```

## 문제 해결

### Neo4j가 시작되지 않는 경우

```bash
# 컨테이너 재시작
docker-compose restart neo4j

# 데이터 초기화 (주의: 모든 데이터 삭제)
docker-compose down -v
rm -rf data/neo4j/data/*
docker-compose up -d neo4j
```

### 메모리 부족

`docker-compose.yml`에서 메모리 설정을 조정하세요:

```yaml
environment:
  - NEO4J_dbms_memory_heap_max__size=4G  # 늘리기
```

## 참고

- Neo4j Community Edition 사용
- APOC 및 GDS (Graph Data Science) 플러그인 포함
- 데이터는 `data/neo4j/`에 영구 저장됨
