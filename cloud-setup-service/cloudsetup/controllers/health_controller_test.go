package controllers

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestHealthServiceServe_Success(t *testing.T) {
	controller := &HealthServiceController{}
	req := httptest.NewRequest("GET", "/health", nil)
	w := httptest.NewRecorder()

	controller.Serve(w, req)

	assert.Equal(t, http.StatusOK, w.Code)
	assert.JSONEq(t, `{"status": "ok"}`, w.Body.String())
}
