package routes

import (
	"cloudsetup/controllers"
	"net/http"
)

type Controllers struct {
	UsernameServiceController *controllers.UsernameServiceController
}

func RegisterRoutes(mux *http.ServeMux, ctrls *Controllers) {
	mux.HandleFunc("/getusername", ctrls.UsernameServiceController.GetUsernameHandler)
	// add more routes here for adding more setup scripts

}
