package controllers

import (
	"net/http"
)

type HealthServiceController struct{}

func (h *HealthServiceController) Serve(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Header().Set("content-Type", "application/json")
	w.Write([]byte(`{"status": "ok"}`))
}
