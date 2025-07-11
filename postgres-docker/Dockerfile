FROM postgres:14

# 安裝必要套件（含編譯用、PostgreSQL dev、Apache AGE 依賴）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    wget \
    ca-certificates \
    flex \
    bison \
    postgresql-server-dev-14 \
    && rm -rf /var/lib/apt/lists/*

# 安裝 pgvector v0.7.3
RUN wget https://github.com/pgvector/pgvector/archive/v0.7.3.tar.gz \
    && tar -xzf v0.7.3.tar.gz \
    && cd pgvector-0.7.3 && make && make install \
    && cd .. && rm -rf pgvector-0.7.3 v0.7.3.tar.gz

# 安裝 Apache AGE v1.5.0 (支援 PostgreSQL 14)
RUN wget https://github.com/apache/age/archive/refs/tags/PG14/v1.5.0-rc0.tar.gz -O age-pg14-1.5.0.tar.gz \
    && tar -xzf age-pg14-1.5.0.tar.gz \
    && cd age-PG14-v1.5.0-rc0 && make && make install \
    && cd .. && rm -rf age-PG14-v1.5.0-rc0 age-pg14-1.5.0.tar.gz

# 預載 age extension（可選）
RUN echo "shared_preload_libraries = 'age'" >> /usr/share/postgresql/postgresql.conf.sample
