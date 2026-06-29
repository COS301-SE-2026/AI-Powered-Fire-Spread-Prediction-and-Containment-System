Start test db in background
```bash
docker-compose -f docker-compose.test.yml up -d
```

Run tests:
```bash
pytest app/backend/src/tests/
```

Shut down and wipe test db completely:
```bash
docker-compose -f docker-compose.test.yml down -v
```