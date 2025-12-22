# 1. Use Java (needed for MARS)
FROM eclipse-temurin:17-jre

# 2. Set working directory inside container
WORKDIR /app

# 3. Copy MARS and source files into container
COPY mars.jar /app/mars.jar
COPY src /app/src

# 4. Default command: run MARS headlessly
CMD ["java", "-jar", "/app/mars.jar", "nc", "sm",     "/app/src/main.asm",     "/app/src/util.asm",     "/app/src/iban2knr.asm",     "/app/src/knr2iban.asm",     "/app/src/moduloStr.asm",     "/app/src/validateChecksum.asm"]
