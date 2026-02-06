FROM golang:1.25-alpine AS build-stage
WORKDIR /app
COPY . .
RUN go mod download && go mod verify
RUN go build -o username .

# Run the tests in the container
FROM build-stage AS test-stage
RUN go test -v ./...

FROM alpine:latest AS build-release-stage
WORKDIR /
COPY --from=build-stage /app/username /username

RUN addgroup -S appgroup && adduser -S appuser -G appgroup
RUN apk add --no-cache tini

USER appuser
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["./username"]