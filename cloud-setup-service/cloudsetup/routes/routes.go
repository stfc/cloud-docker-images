package routes

import (
	"net/http"
)

type RouteController interface {
	Serve(w http.ResponseWriter, r *http.Request)
}

type AllControllers struct {
	UsernameServiceController RouteController
	HealthServiceController   RouteController
}

func RegisterRoutes(mux *http.ServeMux, ctrls *AllControllers) {
	mux.HandleFunc("/getusername", ctrls.UsernameServiceController.Serve)
	// add more routes here for adding more setup scripts
	mux.HandleFunc("/health", ctrls.HealthServiceController.Serve)

}
