FROM eclipse-temurin:17-jdk

WORKDIR /app

COPY connector.jar .
COPY configuration ./configuration

CMD ["java", "-Dedc.fs.config=configuration/configuration.properties", "-jar", "connector.jar"]
