# base image
FROM python:3.12-slim-bookworm AS base

WORKDIR /app/api

# Install Poetry
ENV POETRY_VERSION=1.8.4

# if you located in China, you can use aliyun mirror to speed up
# RUN pip install --no-cache-dir poetry==${POETRY_VERSION} -i https://mirrors.aliyun.com/pypi/simple/

RUN pip install --no-cache-dir poetry==${POETRY_VERSION}

# Configure Poetry
ENV POETRY_CACHE_DIR=/tmp/poetry_cache
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV POETRY_VIRTUALENVS_CREATE=true
ENV POETRY_REQUESTS_TIMEOUT=15

FROM base AS packages

# if you located in China, you can use aliyun mirror to speed up
# RUN sed -i 's@deb.debian.org@mirrors.aliyun.com@g' /etc/apt/sources.list.d/debian.sources
RUN apt-get update \
    && apt-get install -y --no-install-recommends wget
RUN wget https://packages.microsoft.com/config/ubuntu/24.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
RUN dpkg -i packages-microsoft-prod.deb

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc g++ libc-dev libffi-dev libgmp-dev libmpfr-dev libmpc-dev wget

# Install Python dependencies
COPY pyproject.toml poetry.lock ./
RUN poetry install --sync --no-cache --no-root

# production stage
FROM base AS production

ENV FLASK_APP=app.py
ENV EDITION=SELF_HOSTED
ENV DEPLOY_ENV=PRODUCTION
ENV CONSOLE_API_URL=http://127.0.0.1:5001
ENV CONSOLE_WEB_URL=http://127.0.0.1:3000
ENV SERVICE_API_URL=http://127.0.0.1:5001
ENV APP_WEB_URL=http://127.0.0.1:3000

EXPOSE 5001

# set timezone
ENV TZ=UTC

WORKDIR /app/api

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl nodejs libgmp-dev libmpfr-dev libmpc-dev libgl1-mesa-glx libglib2.0-0 \
    # if you located in China, you can use aliyun mirror to speed up
    # && echo "deb http://mirrors.aliyun.com/debian testing main" > /etc/apt/sources.list \
    && echo "deb http://deb.debian.org/debian testing main" > /etc/apt/sources.list \
    && apt-get update \
    # For Security
    && apt-get install -y --no-install-recommends expat=2.6.4-1 libldap-2.5-0=2.5.19+dfsg-1 perl=5.40.0-8 libsqlite3-0=3.46.1-1 zlib1g=1:1.3.dfsg+really1.3.1-1+b1 \
    # install a chinese font to support the use of tools like matplotlib
    && apt-get install -y fonts-noto-cjk \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Copy Python environment and packages
ENV VIRTUAL_ENV=/app/api/.venv
COPY --from=packages ${VIRTUAL_ENV} ${VIRTUAL_ENV}
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

# Download nltk data
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')"

RUN pip install --no-cache-dir playwright==1.49.1
RUN playwright install
RUN apt-get update && apt-get install -y \
    libnss3 \
    libnspr4 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libxkbcommon0 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy source code
COPY . /app/api/

# Copy entrypoint
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh


ARG COMMIT_SHA
ENV COMMIT_SHA=${COMMIT_SHA}

ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]
