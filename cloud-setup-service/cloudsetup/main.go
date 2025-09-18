package main

import (
	"context"
	"log/slog"
	"net/http"
	"os"

	"cloudsetup/controllers"
	"cloudsetup/routes"

	"github.com/gophercloud/gophercloud/v2"
	"github.com/gophercloud/gophercloud/v2/openstack"
	"github.com/gophercloud/gophercloud/v2/openstack/config"
	"github.com/gophercloud/gophercloud/v2/openstack/config/clouds"
)

type Clients struct {
	ComputeClient  *gophercloud.ServiceClient
	IdentityClient *gophercloud.ServiceClient
}

func setupClients(ctx context.Context) (*Clients, error) {
	authOpts, endpointOpts, tlsConfig, err := clouds.Parse(clouds.WithCloudName("dev"))
	if err != nil {
		return nil, err
	}
	authOpts.AllowReauth = true

	provider, err := config.NewProviderClient(ctx, authOpts, config.WithTLSConfig(tlsConfig))
	if err != nil {
		return nil, err
	}

	computeClient, err := openstack.NewComputeV2(provider, endpointOpts)
	if err != nil {
		return nil, err
	}

	identityClient, err := openstack.NewIdentityV3(provider, endpointOpts)
	if err != nil {
		return nil, err
	}

	return &Clients{
		ComputeClient:  computeClient,
		IdentityClient: identityClient,
	}, nil
}

func setupControllers(clients *Clients) *routes.Controllers {

	// setup controllers here
	usercontroller := &controllers.UsernameServiceController{
		ComputeClient:  clients.ComputeClient,
		IdentityClient: clients.IdentityClient,
	}

	ctrls := &routes.Controllers{
		UsernameServiceController: usercontroller,
	}
	return ctrls
}

func setupRoutes(ctrls *routes.Controllers) *http.ServeMux {
	mux := http.NewServeMux()
	routes.RegisterRoutes(mux, ctrls)
	return mux
}

func serve(addr string, handler http.Handler) error {
	slog.Info("Starting server", "addr", addr)
	return http.ListenAndServe(addr, handler)
}

func main() {
	ctx := context.Background()
	clients, err := setupClients(ctx)
	if err != nil {
		slog.Error("Failed to setup clients", "error", err)
		panic(err)
	}

	ctrls := setupControllers(clients)
	mux := setupRoutes(ctrls)

	addr := os.Getenv("ADDR")
	if addr == "" {
		addr = ":80"
	}

	if err := serve(addr, mux); err != nil {
		slog.Error("Server failed", "error", err)
		panic(err)
	}
}
