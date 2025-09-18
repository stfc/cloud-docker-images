// file: routes/routes_test.go

package routes

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/stretchr/testify/assert"
)

// Mock implementation of RouteController
type mockController struct {
	Called      bool
	Response    string
	StatusCode  int
	LastRequest *http.Request
}

func (m *mockController) Serve(w http.ResponseWriter, r *http.Request) {
	m.Called = true
	m.LastRequest = r
	w.WriteHeader(http.StatusOK)

}

func setupControllers(mc RouteController) *AllControllers {
	return &AllControllers{
		UsernameServiceController: mc,
		HealthServiceController:   mc,
	}
}

func TestRegisterRoutes_Username(t *testing.T) {
	mux := http.NewServeMux()
	mc := &mockController{}

	RegisterRoutes(mux, setupControllers(mc))

	req := httptest.NewRequest("GET", "/getusername", nil)
	w := httptest.NewRecorder()

	mux.ServeHTTP(w, req)

	resp := w.Result()
	// to pass linter
	defer func() { _ = resp.Body.Close() }()

	assert.True(t, mc.Called)
	assert.Equal(t, "/getusername", mc.LastRequest.RequestURI)
}

func TestRegisterRoutes_Health(t *testing.T) {
	mux := http.NewServeMux()
	mc := &mockController{}

	RegisterRoutes(mux, setupControllers(mc))

	req := httptest.NewRequest("GET", "/health", nil)
	w := httptest.NewRecorder()

	mux.ServeHTTP(w, req)

	resp := w.Result()
	// to pass linter
	defer func() { _ = resp.Body.Close() }()

	assert.True(t, mc.Called)
	assert.Equal(t, "/health", mc.LastRequest.RequestURI)
}
