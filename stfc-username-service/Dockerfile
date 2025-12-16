FROM golang:1.25-alpine AS BuildStage
WORKDIR /app
COPY . .
RUN go mod download && go mod verify
RUN go build -o username .

# Run the tests in the container
FROM BuildStage AS TestStage
RUN go test -v ./...

FROM alpine:latest AS FinalStage
WORKDIR /
COPY --from=BuildStage /app/username /username

RUN addgroup -S appgroup && adduser -S appuser -G appgroup
RUN apk add --no-cache tini

USER appuser
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["./username"]