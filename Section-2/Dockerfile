# Set up base image
FROM postgres

# Environment variables
ENV POSTGRES_PASSWORD password
ENV POSTGRES_DB database

# Copy the SQL script to create tables into the container
COPY Section-2/*.sql /docker-entrypoint-initdb.d/
COPY processed-datasets/20230520-1349-applications_dataset.csv /docker-entrypoint-initdb.d/

# Expose the PostgreSQL port
EXPOSE 5432